import logging
from decimal import Decimal
from typing import List

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Action, UniV3Obs
from dojo.policies import BasePolicy


# SNIPPET price_window START
class PriceWindowPolicy(BasePolicy):
    def __init__(
        self, agent: BaseAgent, lower_limit: float, upper_limit: float
    ) -> None:
        super().__init__(agent=agent)
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    # derive actions from observations
    def predict(self, obs: UniV3Obs) -> List[UniV3Action]:
        pool_name = obs.pools[0]
        x_token, y_token = obs.pool_tokens(pool_name=pool_name)
        spot_price = obs.price(token=x_token, unit=y_token, pool_name=pool_name)

        x_quantity, y_quantity = self.agent.quantity(x_token), self.agent.quantity(
            y_token
        )

        if spot_price > self.upper_limit and y_quantity > Decimal("0"):
            action = UniV3Action(
                agent=self.agent,
                type="trade",
                pool_name=pool_name,
                quantities=(Decimal(0), y_quantity),
            )
            return [action]

        if spot_price < self.lower_limit and x_quantity > Decimal("0"):
            action = UniV3Action(
                agent=self.agent,
                type="trade",
                pool_name=pool_name,
                quantities=(x_quantity, Decimal(0)),
                tick_range=(0, 0),
            )
            return [action]

        return []


# SNIPPET price_window END
