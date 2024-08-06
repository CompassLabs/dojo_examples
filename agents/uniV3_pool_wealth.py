from typing import Optional

from dojo.agents import UniV3Agent
from dojo.environments.uniswapV3 import UniV3Obs


class UniV3PoolWealthAgent(UniV3Agent):
    """This agent implements a pool wealth reward function for a single UniV3 pool.

    The agent should not be given any tokens that are not in the UniV3Env pool.
    """

    def __init__(self, initial_portfolio: dict, name: Optional[str] = None):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: UniV3Obs) -> float:
        """The agent wealth in units of asset y according to the UniV3 pool."""
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=pool)

        token_ids = self.get_liquidity_ownership_tokens()
        lp_portfolio = obs.lp_total_potential_tokens_on_withdrawal(token_ids)
        wallet_portfolio = self.erc20_portfolio()

        # wealth expressed as token0 of the pool
        wealth = 0
        for token, quantity in lp_portfolio.items():
            wealth += quantity * obs.price(token=token, unit=pool_tokens[0], pool=pool)
        for token, quantity in wallet_portfolio.items():
            wealth += quantity * obs.price(token=token, unit=pool_tokens[0], pool=pool)
        return wealth
