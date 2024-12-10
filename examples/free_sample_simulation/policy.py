"""Policy for moving averages."""
from collections import deque
from decimal import Decimal

import numpy as np

from dojo.actions.uniswapV3 import BaseUniswapV3Action, UniswapV3Trade
from dojo.agents import UniswapV3Agent
from dojo.environments.uniswapV3 import UniswapV3Observation
from dojo.policies import UniswapV3Policy


# SNIPPET 1 START
class MovingAveragePolicy(UniswapV3Policy):
    """Moving average trading policy for a UniswapV3Env with a single pool.

    :param agent: The agent which is using this policy.
    :param short_window: The short window length for the moving average.
    :param long_window: The long window length for the moving average.
    """

    def __init__(
        self, agent: UniswapV3Agent, pool: str, short_window: int, long_window: int
    ) -> None:
        """Moving agerave strategy on one Uniwap pool."""
        super().__init__(agent=agent)
        self._short_window_len: int = short_window
        self._long_window_len: int = long_window
        self.long_window: deque[float] = deque(maxlen=long_window)
        self.short_window: deque[float] = deque(maxlen=short_window)
        self.pool: str = pool

    # SNIPPET 1 END

    def _clear_windows(self) -> None:
        self.long_window = deque(maxlen=self._long_window_len)
        self.short_window = deque(maxlen=self._short_window_len)

    def _x_to_y_indicated(self, pool_tokens: tuple[str, str]) -> bool:
        """Check if the short window crosses above the long window.

        Only do so if there are tokens left to trade.
        """
        return bool(
            np.mean(self.short_window) > np.mean(self.long_window)
            and self.agent.quantity(pool_tokens[1]) > 0
        )

    def _y_to_x_indicated(self, pool_tokens: tuple[str, str]) -> bool:
        """Check if the short window crosses below the long window.

        Only do so if there are tokens left to trade.
        """
        return bool(
            np.mean(self.short_window) < np.mean(self.long_window)
            and self.agent.quantity(pool_tokens[0]) > 0
        )

    def predict(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        """Create actions from observations."""
        pool_tokens = obs.pool_tokens(pool=self.pool)
        price = obs.price(token=pool_tokens[0], unit=pool_tokens[1], pool=self.pool)
        self.short_window.append(float(price))
        self.long_window.append(float(price))
        obs.add_signal(
            "LongShortDiff",
            float(np.mean(self.short_window) - np.mean(self.long_window)),
        )

        # Only start trading when the windows are full
        if len(self.short_window) < self._short_window_len:
            obs.add_signal("Locked", float(True))
            return []
        if len(self.long_window) < self._long_window_len:
            obs.add_signal("Locked", float(True))
            return []
        obs.add_signal("Locked", float(False))

        # SNIPPET 2 START
        if self._x_to_y_indicated(pool_tokens):
            y_quantity = self.agent.quantity(pool_tokens[1])
            self._clear_windows()
            return [
                UniswapV3Trade(
                    agent=self.agent,
                    pool=self.pool,
                    quantities=(Decimal(0), y_quantity),
                )
            ]
        # SNIPPET 2 END

        if self._y_to_x_indicated(pool_tokens):
            x_quantity = self.agent.quantity(pool_tokens[0])
            self._clear_windows()
            return [
                UniswapV3Trade(
                    agent=self.agent,
                    pool=self.pool,
                    quantities=(x_quantity, Decimal(0)),
                )
            ]
        return []
