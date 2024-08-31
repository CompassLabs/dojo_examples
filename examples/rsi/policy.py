from collections import deque
from decimal import Decimal
from typing import List

import numpy as np

from dojo.actions.base_action import BaseAction
from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniswapV3Observation, UniswapV3Trade
from dojo.policies import BasePolicy


# SNIPPET 1 START
# a policy that uses the RSI indicator to make decisions
class RSIPolicy(BasePolicy):
    """RSI trading policy for a UniswapV3Env with a single pool.

    :param agent: The agent which is using this policy.
    """

    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.rsi_period = 14
        self.rsi_values = deque(maxlen=self.rsi_period)
        self.rsi = 0
        self.buying = False
        self.selling = False

    # SNIPPET 1 END

    def predict(self, obs: UniswapV3Observation) -> List[BaseAction]:
        # SNIPPET 2 START
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)

        # calculate RSI
        self.rsi_values.append(obs.price(token1, token0, pool))
        if len(self.rsi_values) == self.rsi_period:
            delta = np.diff(self.rsi_values)

            gains = delta[delta > 0]
            losses = -delta[delta < 0]
            if losses.size == 0:
                self.rsi = 100
            elif gains.size == 0:
                self.rsi = 0
            else:
                gain = Decimal(gains.mean())
                loss = Decimal(losses.mean())
                rs = gain / loss
                self.rsi = 100 - 100 / (1 + rs)

        obs.add_signal("RSI", self.rsi)
        # SNIPPET 2 END

        # SNIPPET 3 START
        # make decision
        if self.rsi < 30:
            self.buying = True
        elif self.rsi > 70:
            self.selling = True

        # execute action
        if self.buying:
            self.buying = False
            if self.agent.quantity(token0) == Decimal(0):
                return []
            return [
                UniswapV3Trade(
                    self.agent, pool, (Decimal(self.agent.quantity(token0)), Decimal(0))
                )
            ]
        elif self.selling:
            self.selling = False
            if self.agent.quantity(token1) == Decimal(0):
                return []
            return [
                UniswapV3Trade(
                    self.agent, pool, (Decimal(0), Decimal(self.agent.quantity(token1)))
                )
            ]
        return []

    # SNIPPET 3 END
