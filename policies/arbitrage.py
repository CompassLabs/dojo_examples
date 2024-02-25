from collections import deque
from decimal import Decimal
from typing import List, Tuple

import numpy as np

from dojo.actions.base_action import BaseAction
from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Obs, UniV3Trade
from dojo.policies import BasePolicy


class ArbitragePolicy(BasePolicy):
    """Moving average trading policy for a UniV3Env with a single pool.

    :param agent: The agent which is using this policy.
    :param short_window: The short window length for the moving average.
    :param long_window: The long window length for the moving average.
    """

    def __init__(self, agent: BaseAgent) -> None:
        super().__init__(agent=agent)
        self.block_last_trade = -1
        self.min_block_dist = 20
        self.min_signal = 1.901
        self.tradeback_via_pool = None

    def compute_signal(self, obs: UniV3Obs) -> Tuple[Decimal, Decimal]:
        pools = obs.pools
        pool_tokens_0 = obs.pool_tokens(pool=pools[0])
        pool_tokens_1 = obs.pool_tokens(pool=pools[1])
        assert (
            pool_tokens_0 == pool_tokens_1
        ), "This policy arbitrages same token pools with different fee levels."

        price_0 = obs.price(
            token=pool_tokens_0[0], unit=pool_tokens_0[1], pool=pools[0]
        )
        price_1 = obs.price(
            token=pool_tokens_0[0], unit=pool_tokens_0[1], pool=pools[1]
        )
        ratio = price_0 / price_1
        obs.add_signal(
            "Ratio",
            float(ratio),
        )
        signals = (
            ratio * (1 - obs.pool_fee(pools[0])) * (1 - obs.pool_fee(pools[1])),
            1 / ratio * (1 - obs.pool_fee(pools[0])) * (1 - obs.pool_fee(pools[1])),
        )

        obs.add_signal(
            "CalculatedProfit",
            float(max(signals)),
        )

        with open("earnings.csv", "a") as f:
            f.write(f"{max(signals)}\n")
        return signals

    def predict(self, obs: UniV3Obs) -> List[BaseAction]:

        pools = obs.pools
        pool_tokens_0 = obs.pool_tokens(pool=pools[0])
        pool_tokens_1 = obs.pool_tokens(pool=pools[1])
        assert (
            pool_tokens_0 == pool_tokens_1
        ), "This policy arbitrages same token pools with different fee levels."

        # Agent will always be in USDC
        amount_0 = self.agent.quantity(pool_tokens_0[0])
        amount_1 = self.agent.quantity(pool_tokens_0[1])
        ###print("agent portfolio", amount_0, amount_1)

        # Since we don't support multihop yet, we need to trade this way for now.
        if self.tradeback_via_pool is not None:
            action = UniV3Trade(
                agent=self.agent,
                pool=self.tradeback_via_pool,
                quantities=(Decimal(0), amount_1),
            )
            self.tradeback_via_pool = None
            return [action]

        signals = self.compute_signal(obs)
        ###print("signals", signals)
        earnings = max(signals)
        index_pool_first = signals.index(max(signals))
        pool = obs.pools[index_pool_first]

        # Don't trade if the last trade was to recently
        if (
            earnings < self.min_signal
            or obs.block - self.block_last_trade < self.min_block_dist
        ):
            return []

        # Make first trade
        self.tradeback_via_pool = (
            obs.pools[0] if index_pool_first == 1 else obs.pools[1]
        )
        self.block_last_trade = obs.block
        return [
            UniV3Trade(
                agent=self.agent,
                pool=pool,
                quantities=(amount_0, Decimal(0)),
            )
        ]
