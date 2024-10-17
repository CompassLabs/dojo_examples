from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Union

from dojo.actions.base_action import BaseAction
from dojo.actions.uniswapV3 import (
    UniswapV3BurnNew,
    UniswapV3CollectFull,
    UniswapV3ProvideQuantities,
    UniswapV3TradeToTickRange,
    UniswapV3WithdrawLiquidity,
)
from dojo.agents import BaseAgent
from dojo.observations import UniswapV3Observation
from dojo.policies import BasePolicy


class State(Enum):
    IDLE = 0
    REBALANCED = 1
    INVESTED = 2
    WITHDRAWN = 3
    COLLECTED = 4


@dataclass
class _PositionInfo:
    lower_tick: int
    upper_tick: int
    liquidity: int


class ActiveConcentratedLP(BasePolicy):  # type: ignore
    """Actively managing LP postions to always stay around the current price."""

    def __init__(self, agent: BaseAgent, lp_width: int) -> None:
        """Initialize the policy.

        :param agent: The agent which is using this policy.
        :param lower_price_bound: The lower price bound for the tick range of the LP
            position to invest in. e.g. 0.95 means the lower price bound is 95% of the
            current spot price.
        :param upper_price_bound: The upper price bound for the tick range of the LP
            position to invest in. e.g. 1.05 means the upper price bound is 105% of the
            current spot price.
        """
        super().__init__(agent=agent)
        self.state: State = State.IDLE
        self.position_info: Union[_PositionInfo, None] = None
        self.lp_width = lp_width
        self.swap_volume = 0
        self.swap_count = 0
        self.wealth_before = 0

    def _get_provide_lp_range(self, obs: UniswapV3Observation) -> tuple[int, int]:
        lower_active_tick, upper_active_tick = obs.active_tick_range(obs.pools[0])
        tick_spacing = obs.tick_spacing(obs.pools[0])
        return (
            lower_active_tick - self.lp_width * tick_spacing,
            upper_active_tick + self.lp_width * tick_spacing,
        )

    def _rebalance(self, obs: UniswapV3Observation) -> list[BaseAction[Any]]:
        token0, token1 = obs.pool_tokens(obs.pools[0])
        portfolio = self.agent.portfolio()
        self.wealth_before = portfolio[token0] + portfolio[token1] * obs.price(
            token1, token0, obs.pools[0]
        )
        action = UniswapV3TradeToTickRange(
            agent=self.agent,
            pool=obs.pools[0],
            quantities=(portfolio[token0], portfolio[token1]),
            tick_range=self._get_provide_lp_range(obs),
        )
        self.state = State.REBALANCED
        return [action]

    def _invest(self, obs: UniswapV3Observation) -> list[BaseAction[Any]]:
        token0, token1 = obs.pool_tokens(obs.pools[0])
        portfolio = self.agent.portfolio()
        wealth_after = portfolio[token0] + portfolio[token1] * obs.price(
            token1, token0, obs.pools[0]
        )
        volume = abs(wealth_after - self.wealth_before)
        self.swap_volume += volume
        self.swap_count += 1
        provide_tick_range = self._get_provide_lp_range(obs)
        action = UniswapV3ProvideQuantities(
            agent=self.agent,
            pool=obs.pools[0],
            amount0=portfolio[token0],
            amount1=portfolio[token1],
            tick_range=provide_tick_range,
        )
        self.position_info = _PositionInfo(
            lower_tick=provide_tick_range[0],
            upper_tick=provide_tick_range[1],
            liquidity=-1,
        )
        self.state = State.INVESTED
        return [action]

    def _withdraw_if_neccessary(self, obs: UniswapV3Observation) -> list[Any]:
        lower_active_tick, upper_active_tick = obs.active_tick_range(obs.pools[0])

        if not self.position_info:
            return []

        if (lower_active_tick > self.position_info.upper_tick) or (
            upper_active_tick < self.position_info.lower_tick
        ):
            position_id = self.agent.erc721_portfolio()["UNI-V3-POS"][-1]
            provided_lp_stats = obs.nft_positions(position_id)
            action = UniswapV3WithdrawLiquidity(
                agent=self.agent,
                position_id=position_id,
                liquidity=provided_lp_stats["liquidity"],
            )
            self.state = State.WITHDRAWN
            return [action]
        else:
            return []

    def _collect(self, obs: UniswapV3Observation) -> list[BaseAction[Any]]:
        position_id = self.agent.erc721_portfolio()["UNI-V3-POS"][-1]
        action = UniswapV3CollectFull(
            agent=self.agent,
            pool=obs.pools[0],
            position_id=position_id,
        )
        self.state = State.COLLECTED
        return [action]

    def _burn_position(self, obs: UniswapV3Observation) -> list[BaseAction[Any]]:
        action = UniswapV3BurnNew(
            agent=self.agent,
            position_id=self.agent.erc721_portfolio()["UNI-V3-POS"][-1],
        )
        self.position_info = None
        self.state = State.IDLE
        return [action]

    def compute_signals(self, obs: UniswapV3Observation) -> None:
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        token_ids = self.agent.get_liquidity_ownership_tokens()

        current_portfolio = obs.lp_portfolio(token_ids)
        current_quantities = obs.lp_quantities(token_ids)
        current_fees = obs.lp_fees(token_ids)

        obs.add_signal(
            "LP fees earned", float(current_fees[token0] + current_fees[token1])
        )
        obs.add_signal("WETH Price", float(obs.price("WETH", "USDC", pool)))
        obs.add_signal("WETH Holdings", float(current_quantities[token0]))
        obs.add_signal(
            "WETH Holdings in USD",
            float(current_portfolio[token0] * obs.price(token0, token1, pool)),
        )
        obs.add_signal("Swap count", self.swap_count)
        obs.add_signal("Swap volume", self.swap_volume)

    def predict(self, obs: UniswapV3Observation) -> List[BaseAction]:  # type: ignore
        obs.add_signal("Swap Volume", self.swap_volume)
        obs.add_signal("Swap Count", self.swap_count)
        obs.add_signal("LP fees earned", float(0))
        obs.add_signal("WETH Price", float(obs.price("WETH", "USDC", obs.pools[0])))
        obs.add_signal("WETH Holdings", float(self.agent.portfolio()["WETH"]))
        obs.add_signal(
            "WETH Holdings in USD",
            self.agent.portfolio()["WETH"] * obs.price("WETH", "USDC", obs.pools[0]),
        )

        match self.state:
            case State.IDLE:
                return self._rebalance(obs)
            case State.REBALANCED:
                return self._invest(obs)
            case State.INVESTED:
                self.compute_signals(obs)
                return self._withdraw_if_neccessary(obs)
            case State.WITHDRAWN:
                return self._collect(obs)
            case State.COLLECTED:
                return self._burn_position(obs)

        return []
