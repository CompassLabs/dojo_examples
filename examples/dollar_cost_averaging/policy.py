from decimal import Decimal
from typing import List

from dojo.actions.base_action import BaseAction
from dojo.actions.uniswapV3 import UniswapV3Trade
from dojo.agents import BaseAgent
from dojo.observations.uniswapV3 import UniswapV3Observation
from dojo.policies import BasePolicy


# a policy that buys a fixed amount of the first token in the pool
# SNIPPET 1 START
class DCAPolicy(BasePolicy):  # type: ignore
    """Dollar Cost Averaging policy for a UniswapV3Env with a single pool.

    :param agent: The agent which is using this policy.
    :param buying_amount: The number of tokens to swap at each trade.
    :param min_dist: The interval to swap tokens. The agent will only swap tokens if the
        last trade was at least min_dist blocks ago.
    """

    def __init__(self, agent: BaseAgent, buying_amount: float, min_dist: int) -> None:
        super().__init__(agent=agent)
        self.buying_amount = buying_amount
        self.min_dist = min_dist
        self.last_trade_block = 0

    # SNIPPET 1 END

    def predict(self, obs: UniswapV3Observation) -> List[BaseAction]:  # type: ignore
        # SNIPPET 2 START
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        portfolio = self.agent.portfolio()

        # add a signal to obs to monitor the difference in wealth if the agent bought the token all at once vs. dollar cost averaging
        token0_balance = portfolio.get(token0, 0)
        token1_balance = portfolio.get(token1, 0)

        # calculate the current value of the portfolio if the agent bought the token all at once
        value_if_held = self.agent.initial_portfolio[
            token0
        ] + self.agent.initial_portfolio[token1] * obs.price(
            token1, unit=token0, pool=pool
        )

        # calculate the current value of the portfolio if the agent used dollar cost averaging
        dca_value = token0_balance * Decimal(1.0) + token1_balance * obs.price(
            token1, unit=token0, pool=pool
        )

        wealth_difference = dca_value - value_if_held
        obs.add_signal("Wealth Difference", wealth_difference)
        # SNIPPET 2 END

        # buy the first token in the pool only when the agent has enough balance and the last trade was long enough ago
        # SNIPPET 3 START
        if (
            portfolio[token0] >= self.buying_amount
            and obs.block - self.last_trade_block >= self.min_dist  # type: ignore
        ):
            self.last_trade_block = obs.block  # type: ignore
            return [
                UniswapV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(Decimal(self.buying_amount), Decimal(0)),
                )
            ]
        return []
        # SNIPPET 3 END
