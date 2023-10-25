from collections import deque
from decimal import Decimal
from typing import List

import numpy as np

from dojo.actions import BaseAction
from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Obs, UniV3Trade
from dojo.policies import BasePolicy


class MovingAveragePolicy(BasePolicy):
    """Moving average trading policy for a UniV3Env with a single pool.

    :param agent: The agent which is using this policy.
    :param short_window: The short window length for the moving average.
    :param long_window: The long window length for the moving average.
    """

    def __init__(self, agent: BaseAgent, short_window: int, long_window: int) -> None:
        super().__init__(agent=agent)
        self._short_window = short_window
        self._long_window = long_window
        self.long_window = deque(maxlen=long_window)
        self.short_window = deque(maxlen=short_window)

    def _clear_windows(self):
        self.long_window = deque(maxlen=self._long_window)
        self.short_window = deque(maxlen=self._short_window)

    def _x_to_y_indicated(self, pool_tokens):
        """If the short window crosses above the long window, convert asset y to asset x.

        Only do so if there are tokens left to trade.
        """
        return (
            np.mean(self.short_window) > np.mean(self.long_window)
            and self.agent.quantity(pool_tokens[1]) > 0
        )

    def _y_to_x_indicated(self, pool_tokens):
        """If the short window crosses below the long window, convert asset x to asset y

        Only do so if there are tokens left to trade.
        """
        return (
            np.mean(self.short_window) < np.mean(self.long_window)
            and self.agent.quantity(pool_tokens[0]) > 0
        )

    def predict(self, obs: UniV3Obs) -> List[BaseAction]:
        """Make a trade if the mean of the short window crosses the mean of the long window."""
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool=pool)
        price = obs.price(token=pool_tokens[0], unit=pool_tokens[1], pool=pool)
        self.short_window.append(float(price))
        self.long_window.append(float(price))
        obs.add_signal(
            "LongShortDiff",
            float(np.mean(self.short_window) - np.mean(self.long_window)),
        )

        # Only start trading when the windows are full
        if len(self.short_window) < self.short_window.maxlen:
            obs.add_signal("Locked", float(True))
            return []
        if len(self.long_window) < self.long_window.maxlen:
            obs.add_signal("Locked", float(True))
            return []
        obs.add_signal("Locked", float(False))

        if self._x_to_y_indicated(pool_tokens):
            y_quantity = self.agent.quantity(pool_tokens[1])
            self._clear_windows()
            return [
                UniV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(Decimal(0), y_quantity),
                )
            ]

        if self._y_to_x_indicated(pool_tokens):
            x_quantity = self.agent.quantity(pool_tokens[0])
            self._clear_windows()
            return [
                UniV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(x_quantity, Decimal(0)),
                )
            ]
        return []
