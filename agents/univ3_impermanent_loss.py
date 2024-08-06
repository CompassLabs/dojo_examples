from typing import Optional

from dojo.agents import UniV3Agent
from dojo.environments.uniswapV3 import UniV3Obs


class ImpermanentLossAgent(UniV3Agent):
    """This agent implements an IL reward function for a single UniV3 pool.

    The agent should not be given any tokens that are not in the UniV3Env pool.
    """

    def __init__(self, initial_portfolio: dict, name: Optional[str] = None):
        super().__init__(name=name, initial_portfolio=initial_portfolio)
        self.hold_portfolio = []

    def _pool_wealth(self, obs: UniV3Obs, portfolio: dict) -> float:
        """Calculate the wealth of a portfolio denoted in the y asset of the pool.

        :param portfolio: Portfolio to calculate wealth for.
        :raises ValueError: If agent token is not in pool.
        """
        wealth = 0
        if len(portfolio) == 0:
            return wealth

        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=pool)
        for token, quantity in portfolio.items():
            if token not in pool_tokens:
                raise ValueError(f"{token} not in pool, so it can't be priced.")
            price = obs.price(token=token, unit=pool_tokens[1], pool=pool)
            wealth += quantity * price
        return wealth

    def reward(self, obs: UniV3Obs) -> float:
        """Impermanent loss of the agent denoted in the y asset of the pool."""
        token_ids = self.get_liquidity_ownership_tokens()
        if not self.hold_portfolio:
            self.hold_portfolio = obs.lp_quantities(token_ids)
        hold_wealth = self._pool_wealth(obs, self.hold_portfolio)
        lp_wealth = self._pool_wealth(obs, obs.lp_portfolio(token_ids))
        if hold_wealth == 0:
            return 0.0
        return (lp_wealth - hold_wealth) / hold_wealth
