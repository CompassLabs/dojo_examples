import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

import os

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Obs

from .price_window import PriceWindowPolicy


# SNIPPET dynamic_price_window START
class DynamicPriceWindowPolicy(PriceWindowPolicy):

    # upper and lower limit are now parameters of the policy
    def __init__(
        self, agent: BaseAgent, lower_limit: float, upper_limit: float
    ) -> None:
        super().__init__(agent=agent, lower_limit=lower_limit, upper_limit=upper_limit)
        self.old_price = 0
        self.spread = self.upper_limit - self.lower_limit
        self.center = (self.upper_limit + self.lower_limit) / 2
        self.returns = []

    def fit(self, obs: UniV3Obs) -> None:
        pool = obs.pools[0]
        x_token, y_token = obs.pool_tokens(pool)
        spot_price = obs.get_price(token=x_token, unit=y_token, pool=pool)
        if len(self.returns) == 0:
            self.old_price = spot_price

        new_return = spot_price / old_price
        returns.append(new_return)
        vol = np.std(self.returns)
        self.vols.append(vol)
        vol_diff = vol / np.mean(self.vols)
        self.spread = self.spread * vol_diff
        self.lower_limit = max(0, self.center - (self.spread / 2))
        self.upper_limit = self.center + (self.spread / 2)


# SNIPPET dynamic_price_window END
