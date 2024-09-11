from decimal import Decimal
from typing import Optional

from dojo.agents import UniswapV3Agent
from dojo.environments.uniswapV3 import UniswapV3Observation


class ImpermanentLossAgent(UniswapV3Agent):
    """This agent implements an IL reward function for a single UniswapV3 pool.

    The agent should not be given any tokens that are not in the UniswapV3Env pool.
    """

    def __init__(
        self, initial_portfolio: dict[str, Decimal], name: Optional[str] = None
    ):
        super().__init__(name=name, initial_portfolio=initial_portfolio)
        self.hold_portfolio: dict[str, Decimal] = {}

    # SNIPPET 1 START
    def _pool_wealth(
        self, obs: UniswapV3Observation, portfolio: dict[str, Decimal]
    ) -> float:
        """Calculate the wealth of a portfolio denoted in the y asset of the pool.

        :param portfolio: Portfolio to calculate wealth for.
        :raises ValueError: If agent token is not in pool.
        """
        wealth = Decimal(0)
        if len(portfolio) == 0:
            return float(wealth)

        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=pool)
        for token, quantity in portfolio.items():
            if token not in pool_tokens:
                raise ValueError(f"{token} not in pool, so it can't be priced.")
            price = obs.price(token=token, unit=pool_tokens[1], pool=pool)
            wealth += quantity * price
        return float(wealth)

    # SNIPPET 1 END

    # SNIPPET 2 START
    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        """Impermanent loss of the agent denoted in the y asset of the pool."""
        token_ids = self.get_liquidity_ownership_tokens()
        if not self.hold_portfolio:
            self.hold_portfolio = obs.lp_quantities(token_ids)
        hold_wealth = self._pool_wealth(obs, self.hold_portfolio)
        lp_wealth = self._pool_wealth(obs, obs.lp_portfolio(token_ids))
        if hold_wealth == 0:
            return 0.0
        return (lp_wealth - hold_wealth) / hold_wealth

    # SNIPPET 2 END
