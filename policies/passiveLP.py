"""Passive LP policy."""
from decimal import Decimal

from dojo.actions.uniswapV3 import BaseUniswapV3Action, UniswapV3Quote, UniswapV3Trade
from dojo.observations import uniswapV3
from dojo.observations.uniswapV3 import UniswapV3Observation
from dojo.policies import UniswapV3Policy


class PassiveConcentratedLP(UniswapV3Policy):
    """Provide liquidity passively to a pool in the specified price bounds."""

    def __init__(self, lower_price_bound: float, upper_price_bound: float) -> None:
        """Initialize the policy.

        :param lower_price_bound: The lower price bound for the tick range of the LP
            position to invest in. e.g. 0.95 means the lower price bound is 95% of the
            current spot price.
        :param upper_price_bound: The upper price bound for the tick range of the LP
            position to invest in. e.g. 1.05 means the upper price bound is 105% of the
            current spot price.
        """
        super().__init__()
        self.lower_price_bound: Decimal = Decimal(lower_price_bound)
        self.upper_price_bound: Decimal = Decimal(upper_price_bound)
        self.has_traded = False
        self.has_invested = False

    def initial_trade(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        """Rebalance token holdings to a 50/50 ratio."""
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        spot_price = obs.price(token0, token1, pool)
        wallet_portfolio = self.agent.erc20_portfolio()

        target0 = (wallet_portfolio[token0] + wallet_portfolio[token1] / spot_price) / 2
        target1 = spot_price * target0
        trade_action = UniswapV3Trade(
            agent=self.agent,
            pool=pool,
            quantities=(
                (-target0 + wallet_portfolio[token0]),
                (-target1 + wallet_portfolio[token1]),
            ),
        )
        self.has_traded = True
        return [trade_action]

    def inital_quote(
        self, obs: UniswapV3Observation
    ) -> list[BaseUniswapV3Action]:  # noqa: D102
        pool = obs.pools[0]
        portfolio = self.agent.portfolio()
        token0, token1 = obs.pool_tokens(pool)
        spot_price = obs.price(token0, token1, pool)

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
        provide_action = UniswapV3Quote(
            agent=self.agent,
            pool=pool,
            quantities=(portfolio[token0], portfolio[token1]),
            tick_range=(lower_tick, upper_tick),
        )
        self.has_invested = True
        return [provide_action]

    def predict(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        """Derive actions from observations."""
        if not self.has_traded:
            return self.initial_trade(obs)
        if not self.has_invested:
            return self.inital_quote(obs)
        return []
