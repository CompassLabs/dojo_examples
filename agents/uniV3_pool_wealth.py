from dojo.agents import BaseAgent
from dojo.common.types import Portfolio
from dojo.environments.uniswapV3 import UniV3Obs


class UniV3PoolWealthAgent(BaseAgent):
    """This agent implements a pool wealth reward function for a single UniV3 pool.

    The agent should not be given any tokens that are not in the UniV3Env pool.
    """

    def __init__(self, initial_portfolio: dict):
        """Initialize the agent."""
        super().__init__(initial_portfolio=initial_portfolio)

    def lp_portfolio(self, obs: UniV3Obs) -> Portfolio:
        """Get the portfolio of the agent LP positions."""
        lp_portfolio = self.erc721_portfolio()
        portfolio = {}
        if "UNI-V3-POS" in lp_portfolio:
            nfts = lp_portfolio["UNI-V3-POS"]
            for token_id in nfts:
                pos_info = obs.nft_positions(token_id=token_id)
                token0 = pos_info["token0"]
                token1 = pos_info["token1"]
                quantities = pos_info["real_quantities"]
                if token0 not in portfolio:
                    portfolio[token0] = 0.0
                if token1 not in portfolio:
                    portfolio[token1] = 0.0
                portfolio[token0] += quantities[0]
                portfolio[token1] += quantities[1]
        return portfolio

    def reward(self, obs: UniV3Obs) -> float:
        """The agent wealth in units of asset y according to the UniV3 pool."""
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=pool)

        lp_portfolio = self.lp_portfolio(obs)
        wallet_portfolio = self.erc20_portfolio()
        total_portfolio = {**lp_portfolio, **wallet_portfolio}

        wealth = 0
        for token, quantity in total_portfolio.items():
            if token not in pool_tokens:
                raise ValueError(f"{token} not in pool, so it can't be priced.")
            price = obs.price(token=token, unit=pool_tokens[1], pool=pool)
            wealth += quantity * price

        return wealth
