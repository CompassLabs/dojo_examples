import logging
import os

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniswapV3Observation

from .price_window import PriceWindowPolicy

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# SNIPPET dynamic_price_window START
class DynamicPriceWindowPolicy(PriceWindowPolicy):

    # upper and lower limit are now parameters of the policy
    def __init__(
        self, agent: BaseAgent, lower_limit: float, upper_limit: float
    ) -> None:
        super().__init__(agent=agent, lower_limit=lower_limit, upper_limit=upper_limit)
        self.old_price: float = 0.0
        self.spread: float = self.upper_limit - self.lower_limit
        self.center: float = (self.upper_limit + self.lower_limit) / 2
        self.returns: list[float] = []


# SNIPPET dynamic_price_window END
