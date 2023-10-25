from typing import Optional

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Obs


class UniV3PoolWealthAgent(BaseAgent):
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

        token_ids = self.erc721_portfolio().get("UNI-V3-POS", [])
        lp_portfolio = obs.lp_quantities(token_ids)
        wallet_portfolio = self.erc20_portfolio()
        total_portfolio = {**lp_portfolio, **wallet_portfolio}

        # wealth expressed as token0 of the pool
        wealth = 0
        for token, quantity in total_portfolio.items():
            wealth += quantity * obs.price(token=token, unit=pool_tokens[0], pool=pool)
        return wealth
