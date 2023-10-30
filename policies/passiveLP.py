from decimal import Decimal
from typing import List

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Action, UniV3Obs
from dojo.observations import uniswapV3
from dojo.policies import BasePolicy


class PassiveConcentratedLP(BasePolicy):
    """Provide liquidity passively to a pool in the sepcified price bounds."""

    def __init__(
        self, agent: BaseAgent, lower_price_bound: float, upper_price_bound: float
    ) -> None:
        """Initialize the policy.

        :param agent: The agent which is using this policy.
        :param lower_price_bound: The lower price bound for the tick range of the LP position to invest in.
            e.g. 0.95 means the lower price bound is 95% of the current spot price.
        :param upper_price_bound: The upper price bound for the tick range of the LP position to invest in.
            e.g. 1.05 means the upper price bound is 105% of the current spot price.
        """
        super().__init__(agent=agent)
        self.lower_price_bound = Decimal(lower_price_bound)
        self.upper_price_bound = Decimal(upper_price_bound)
        self.has_traded = False
        self.has_invested = False

    def fit(self):
        pass

    def initial_trade(self, obs: UniV3Obs) -> List[UniV3Action]:
        pool_idx = 0
        pool = obs.pools[pool_idx]
        token0, token1 = obs.pool_tokens(pool)
        spot_price = obs.price(token0, token1, pool)
        wallet_portfolio = self.agent.erc20_portfolio()

        token0, token1 = obs.pool_tokens(obs.pools[pool_idx])
        decimals0 = obs.token_decimals(token0)
        decimals1 = obs.token_decimals(token1)

        lower_price_range = self.lower_price_bound * spot_price
        upper_price_range = self.upper_price_bound * spot_price
        tick_spacing = obs.tick_spacing(pool)

        lower_tick = uniswapV3.price_to_active_tick(
            lower_price_range, tick_spacing, (decimals0, decimals1)
        )
        upper_tick = uniswapV3.price_to_active_tick(
            upper_price_range, tick_spacing, (decimals0, decimals1)
        )
        target0 = (wallet_portfolio[token0] + wallet_portfolio[token1] / spot_price) / 2
        target1 = spot_price * target0
        trade_action = UniV3Action(
            agent=self.agent,
            type="trade",
            pool=pool,
            quantities=[
                (-target0 + wallet_portfolio[token0]),
                (-target1 + wallet_portfolio[token1]),
            ],
            tick_range=(lower_tick, upper_tick),
        )
        self.has_traded = True
        return [trade_action]

    def inital_quote(self, obs: UniV3Obs) -> List[UniV3Action]:
        pool_idx = 0
        pool = obs.pools[pool_idx]
        token0, token1 = obs.pool_tokens(pool)
        spot_price = obs.price(token0, token1, pool)
        wallet_portfolio = self.agent.erc20_portfolio()

        token0, token1 = obs.pool_tokens(obs.pools[pool_idx])
        decimals0 = obs.token_decimals(token0)
        decimals1 = obs.token_decimals(token1)

        lower_price_range = self.lower_price_bound * spot_price
        upper_price_range = self.upper_price_bound * spot_price
        tick_spacing = obs.tick_spacing(pool)

        lower_tick = uniswapV3.price_to_active_tick(
            lower_price_range, tick_spacing, (decimals0, decimals1)
        )
        upper_tick = uniswapV3.price_to_active_tick(
            upper_price_range, tick_spacing, (decimals0, decimals1)
        )
        # target0 = (wallet_portfolio[token0] + wallet_portfolio[token1] / spot_price) / 2
        # target1 = spot_price * target0
        provide_action = UniV3Action(
            agent=self.agent,
            type="quote",
            pool=pool,
            quantities=[wallet_portfolio[token0], wallet_portfolio[token1]],
            tick_range=(lower_tick, upper_tick),
        )
        self.has_invested = True
        return [provide_action]

    def predict(self, obs: UniV3Obs) -> List[UniV3Action]:
        if not self.has_traded:
            return self.initial_trade(obs)
        if not self.has_invested:
            return self.inital_quote(obs)
        return []
