"""Policy for active liquidity provisioning."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union

from dojo.actions.uniswapV3 import (
    BaseUniswapV3Action,
    UniswapV3BurnNew,
    UniswapV3CollectFull,
    UniswapV3ProvideQuantities,
    UniswapV3TradeToTickRange,
    UniswapV3WithdrawLiquidity,
)
from dojo.observations import UniswapV3Observation
from dojo.policies import UniswapV3Policy


class State(Enum):
    """The agent is always in one of these states."""

    IDLE = 0
    REBALANCED = 1
    INVESTED = 2
    WITHDRAWN = 3
    COLLECTED = 4


@dataclass
class _PositionInfo:
    lower_tick: int
    upper_tick: int


# SNIPPET 1 START
class ActiveConcentratedLP(UniswapV3Policy):
    """Actively managing LP postions to always stay around the current price."""

    def __init__(self, lp_width: int) -> None:
        """Initialize the policy.

        :param lp_width: How many ticks to the left and right the liquidity will be
            spread.
        """
        super().__init__()
        self.state: State = State.IDLE
        self.position_info: Union[_PositionInfo, None] = None
        self.lp_width = lp_width
        self.swap_volume = Decimal(0)
        self.swap_count = Decimal(0)
        self.wealth_before = Decimal(0)
        # SNIPPET 1 END

    # SNIPPET 2 START
    def _get_provide_lp_range(self, obs: UniswapV3Observation) -> tuple[int, int]:
        lower_active_tick, upper_active_tick = obs.active_tick_range(obs.pools[0])
        tick_spacing = obs.tick_spacing(obs.pools[0])
        return (
            lower_active_tick - self.lp_width * tick_spacing,
            upper_active_tick + self.lp_width * tick_spacing,
        )

    def _rebalance(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        token0, token1 = obs.pool_tokens(obs.pools[0])
        portfolio = self.agent.portfolio()
        self.wealth_before = portfolio[token1] + portfolio[token0] * obs.price(
            token0, token1, obs.pools[0]
        )
        action = UniswapV3TradeToTickRange(
            agent=self.agent,
            pool=obs.pools[0],
            quantities=(portfolio[token0], portfolio[token1]),
            tick_range=self._get_provide_lp_range(obs),
        )
        self.state = State.REBALANCED
        return [action]

    # SNIPPET 2 END

    def _invest(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        token0, token1 = obs.pool_tokens(obs.pools[0])
        portfolio = self.agent.portfolio()
        wealth_after = portfolio[token1] + portfolio[token0] * obs.price(
            token0, token1, obs.pools[0]
        )
        volume = abs(wealth_after - self.wealth_before)
        self.swap_volume += volume
        self.swap_count += 1
        # SNIPPET 3 START
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
        )
        self.state = State.INVESTED
        # SNIPPET 3 END
        return [action]

    # SNIPPET 4 START
    def _withdraw_if_neccessary(
        self, obs: UniswapV3Observation
    ) -> list[BaseUniswapV3Action]:
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

    # SNIPPET 4 END

    def _collect(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        position_id = self.agent.erc721_portfolio()["UNI-V3-POS"][-1]
        action = UniswapV3CollectFull(
            agent=self.agent,
            pool=obs.pools[0],
            position_id=str(position_id),
        )
        self.state = State.COLLECTED
        return [action]

    def _burn_position(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        action = UniswapV3BurnNew(
            agent=self.agent,
            position_id=str(self.agent.erc721_portfolio()["UNI-V3-POS"][-1]),
        )
        self.position_info = None
        self.state = State.IDLE
        return [action]

    def compute_signals(self, obs: UniswapV3Observation) -> None:  # noqa: D102
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        token_ids = self.agent.get_liquidity_ownership_tokens()

        current_portfolio = obs.lp_portfolio(token_ids)
        current_fees = obs.lp_fees(token_ids)

        current_holdings = self.agent.total_wealth(obs, "USDC")
        initial_holdings = Decimal(0)
        for token in self.agent.initial_portfolio:
            if token == "USDC":
                initial_holdings += self.agent.initial_portfolio[token]
            elif token == token0:
                initial_holdings += self.agent.initial_portfolio[token] * obs.price(
                    token0, "USDC", pool
                )
            elif token == token1:
                initial_holdings += self.agent.initial_portfolio[token] * obs.price(
                    token1, "USDC", pool
                )
        impermanent_loss = current_holdings - float(initial_holdings)

        obs.add_signal(
            "LP fees earned",
            float(
                current_fees.get(token0, 0) * obs.price(token0, token1, pool)
                + current_fees.get(token1, 0)
            ),
        )
        obs.add_signal("PEPE Price", float(obs.price("PEPE", "USDC", pool)))
        obs.add_signal(
            "PEPE Holdings in USD",
            float(current_portfolio.get(token0, 0) * obs.price(token0, token1, pool)),
        )
        obs.add_signal("Swap count", self.swap_count)
        obs.add_signal("Swap volume", self.swap_volume)
        obs.add_signal("Impermanent Loss Active LPing", impermanent_loss)

    def predict(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        """Derive actions from observations."""
        self.compute_signals(obs)

        match self.state:
            case State.IDLE:
                return self._rebalance(obs)
            case State.REBALANCED:
                return self._invest(obs)
            case State.INVESTED:
                return self._withdraw_if_neccessary(obs)
            case State.WITHDRAWN:
                return self._collect(obs)
            case State.COLLECTED:
                return self._burn_position(obs)

        return []
