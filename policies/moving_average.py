from collections import deque
from typing import List

import numpy as np

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Action, UniV3Env, UniV3Obs
from dojo.policies import BasePolicy


class MovingAveragePolicy(BasePolicy):
    """Moving average trading policy.

    :param agent: The agent which is using this policy.
    :param short_window: The short window length for the moving average.
    :param long_window: The long window length for the moving average.
    """

    def __init__(self, agent: BaseAgent, short_window: int, long_window: int) -> None:
        super().__init__(agent=agent)
        self.agent: UniV3Env = self.agent
        # self.pool = self.env.pools[0]
        self.long_window = deque(maxlen=long_window)
        self.short_window = deque(maxlen=short_window)

    # if the short window crosses above the long window, convert asset y to asset x
    # Only do so if there are tokens left to trade
    def _x_to_y_indicated(self, pool_tokens):
        return (
            np.mean(self.short_window) > np.mean(self.long_window)
            and self.agent.quantity(pool_tokens[1]) > 0
        )

    # if the short window crosses below the long window, convert asset x to asset y
    # Only do so if there are tokens left to trade
    def _y_to_x_indicated(self, pool_tokens):
        return (
            np.mean(self.short_window) < np.mean(self.long_window)
            and self.agent.quantity(pool_tokens[0]) > 0
        )

    def predict(self, obs: UniV3Obs) -> List[UniV3Action]:
        return []

        # price of asset x in units of asset y
        # spot_price = obs.price("ETH", "USDC", self.pool) # TODO(lukas)
        spot_price = 1
        # (self, token: str, unit: str, pool: str)
        # spot_price = (
        #     obs["virtual_quantities"][0][0][1] / obs["virtual_quantities"][0][0][0]
        # )
        self.short_window.append(spot_price)
        self.long_window.append(spot_price)

        # Only start trading when the windows are full
        if len(self.short_window) < self.short_window.maxlen:
            return ()
        if len(self.long_window) < self.long_window.maxlen:
            return ()

        pool_tokens = self.env.pool_tokens(self.pool)

        if self._x_to_y_indicated(pool_tokens):
            y_quantity = self.agent.quantity(pool_tokens[1])
            return self.env.make_action(
                agent=self.agent,
                event_type="trade",
                pool=self.pool,
                quantities=np.array([0, y_quantity]),
            )

        if self._y_to_x_indicated(pool_tokens):
            x_quantity = self.agent.quantity(pool_tokens[0])
            return self.env.make_action(
                agent=self.agent,
                event_type="trade",
                pool=self.pool,
                quantities=np.array([x_quantity, 0]),
            )
        return []
