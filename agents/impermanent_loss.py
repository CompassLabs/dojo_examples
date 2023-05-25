from dojo.agents import BaseAgent
from dojo.common.types import Portfolio
from dojo.environments.uniswapV3 import UniV3Obs


class ImpermanentLossAgent(BaseAgent):
    """This agent implements an IL reward function for a single UniV3 pool.

    The agent should not be given any tokens that are not in the UniV3Env pool.
    """

    def __init__(self, initial_portfolio: dict):
        super().__init__(initial_portfolio=initial_portfolio)
        self.hold_portfolio = None

    def lp_portfolio(self, obs: UniV3Obs) -> Portfolio:
        """Get the LP portfolio of the first LP position created."""
        lp_portfolio = self.erc721_portfolio()
        portfolio = {}
        if "UNI-V3-POS" in lp_portfolio:
            token_id = lp_portfolio["UNI-V3-POS"][0]
            pos_info = obs.nft_positions(token_id=token_id)
            token0 = pos_info["token0"]
            token1 = pos_info["token1"]
            quantities = pos_info["real_quantities"]
            portfolio[token0] = quantities[0]
            portfolio[token1] = quantities[1]
        return portfolio

    def _pool_wealth(self, obs: UniV3Obs, portfolio: Portfolio) -> float:
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
        if self.hold_portfolio is None:
            self.hold_portfolio = self.lp_portfolio(obs)
        hold_wealth = self._pool_wealth(self.hold_portfolio)
        lp_wealth = self._pool_wealth(self.lp_portfolio())
        return (lp_wealth - hold_wealth) / hold_wealth
