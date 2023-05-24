from dojo.agents import BaseAgent
from dojo.common.types import BaseObs, Portfolio
from dojo.environments import UniV3Env


class ImpermanentLossAgent(BaseAgent):
    """This agent implements an IL reward function for a single UniV3 pool."""

    def __init__(self, initial_portfolio: dict):
        super().__init__(initial_portfolio=initial_portfolio)
        self.hold_portfolio = None

    def lp_portfolio(self) -> Portfolio:
        """Get the LP portfolio of the mostly created recent LP position."""
        token_id = self.erc721_portfolio()["UNI-V3-POS"][-1]
        position = self.env.nft_positions(token_id)
        return {
            position["token0"]: position["real_quantities"][0],
            position["token1"]: position["real_quantities"][1],
        }

    def _pool_wealth(self, portfolio: Portfolio) -> float:
        """Calculate the wealth of a portfolio denoted in the y asset of the pool.

        :param portfolio: Portfolio to calculate wealth for.

        :raises ValueError: If agent token is not in pool.
        """
        wealth = 0
        if len(portfolio) == 0:
            return wealth

        pool = self.env.pools[0]
        pool_tokens = self.env.pool_tokens(pool)
        obs = self.env.obs
        # price of x in units y
        spot_price = (
            obs["virtual_quantities"][0][0][1] / obs["virtual_quantities"][0][0][0]
        )
        for token, quantity in portfolio.items():
            if pool_tokens.index(token) == 0:
                wealth += quantity
            elif pool_tokens.index(token) == 1:
                wealth += quantity * spot_price
            else:
                raise ValueError(f"{token} not in pool.")
        return wealth

    def reward(self, obs: BaseObs) -> float:  # TODO(lukas)
        """Impermanent loss of the agent denoted in the y asset of the pool."""
        if self.hold_portfolio is None:
            self.hold_portfolio = self.lp_portfolio()
        hold_wealth = self._pool_wealth(self.hold_portfolio)
        lp_wealth = self._pool_wealth(self.lp_portfolio())
        return (lp_wealth - hold_wealth) / hold_wealth
