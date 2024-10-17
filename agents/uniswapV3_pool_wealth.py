from decimal import Decimal
from typing import Optional

from dojo.agents import UniswapV3Agent
from dojo.environments.uniswapV3 import UniswapV3Observation


class UniswapV3PoolWealthAgent(UniswapV3Agent):
    """This agent implements a pool wealth reward function for a single UniswapV3 pool.

    The agent should not be given any tokens that are not in the UniswapV3Env pool.
    """

    def __init__(
        self, initial_portfolio: dict[str, Decimal], name: Optional[str] = None
    ):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        """The agent wealth in units of asset y according to the UniswapV3 pool."""
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=pool)

        token_ids = self.get_liquidity_ownership_tokens()
        lp_portfolio = obs.lp_portfolio(token_ids)
        wallet_portfolio = self.erc20_portfolio()

        # wealth expressed as token0 of the pool
        wealth = Decimal(0)
        for token, quantity in lp_portfolio.items():
            wealth += quantity * obs.price(token=token, unit=pool_tokens[0], pool=pool)
        for token, quantity in wallet_portfolio.items():
            wealth += quantity * obs.price(token=token, unit=pool_tokens[0], pool=pool)
        return float(wealth)
