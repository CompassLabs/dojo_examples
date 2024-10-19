import logging
from decimal import Decimal
from typing import List

from dojo.actions.base_action import BaseAction
from dojo.actions.uniswapV3 import UniswapV3Trade
from dojo.agents import BaseAgent
from dojo.observations.uniswapV3 import UniswapV3Observation
from dojo.policies import BasePolicy

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


# SNIPPET price_window START
class PriceWindowPolicy(BasePolicy):  # type: ignore
    def __init__(
        self, agent: BaseAgent, lower_limit: float, upper_limit: float
    ) -> None:
        super().__init__(agent=agent)
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    # derive actions from observations
    def predict(self, obs: UniswapV3Observation) -> List[BaseAction]:  # type: ignore
        pool = obs.pools[0]
        x_token, y_token = obs.pool_tokens(pool)
        spot_price = obs.price(token=x_token, unit=y_token, pool=pool)

        x_quantity, y_quantity = self.agent.quantity(x_token), self.agent.quantity(
            y_token
        )

        if spot_price > self.upper_limit and y_quantity > Decimal("0"):
            action = UniswapV3Trade(
                agent=self.agent,
                pool=pool,
                quantities=(Decimal(0), y_quantity),
            )
            return [action]

        if spot_price < self.lower_limit and x_quantity > Decimal("0"):
            action = UniswapV3Trade(
                agent=self.agent,
                pool=pool,
                quantities=(x_quantity, Decimal(0)),
            )
            return [action]

        return []


# SNIPPET price_window END
