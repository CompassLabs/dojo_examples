from decimal import Decimal
from typing import List, Tuple, Union

from dojo.actions.base_action import BaseAction
from dojo.actions.uniswapV3 import UniswapV3Trade
from dojo.agents import BaseAgent
from dojo.observations.uniswapV3 import UniswapV3Observation
from dojo.policies import BasePolicy


# SNIPPET 1 START
class ArbitragePolicy(BasePolicy):  # type: ignore
    """Arbitrage trading policy for a UniswapV3Env with two pools.

    :param agent: The agent which is using this policy.
    """

    def __init__(self, agent: BaseAgent) -> None:
        super().__init__(agent=agent)
        self.block_last_trade: int = -1
        self.min_block_dist: int = 20
        self.min_signal: float = 1.901
        self.tradeback_via_pool: Union[str, None] = None

    # SNIPPET 1 END

    # SNIPPET 2 START
    def compute_signal(self, obs: UniswapV3Observation) -> Tuple[Decimal, Decimal]:
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

        return signals

    # SNIPPET 2 END

    # SNIPPET 3 START
    def predict(self, obs: UniswapV3Observation) -> List[BaseAction]:  # type: ignore
        pools = obs.pools
        pool_tokens_0 = obs.pool_tokens(pool=pools[0])
        pool_tokens_1 = obs.pool_tokens(pool=pools[1])
        assert (
            pool_tokens_0 == pool_tokens_1
        ), "This policy arbitrages same token pools with different fee levels."

        # Agent will always be in USDC
        amount_0 = self.agent.quantity(pool_tokens_0[0])
        amount_1 = self.agent.quantity(pool_tokens_0[1])

        # Since we don't support multihop yet, we need to trade this way for now.
        if self.tradeback_via_pool is not None:
            action = UniswapV3Trade(
                agent=self.agent,
                pool=self.tradeback_via_pool,
                quantities=(Decimal(0), amount_1),
            )
            self.tradeback_via_pool = None
            return [action]

        signals = self.compute_signal(obs)
        earnings = max(signals)
        index_pool_first = signals.index(max(signals))
        pool = obs.pools[index_pool_first]

        # Don't trade if the last trade was too recent
        if earnings < self.min_signal or obs.block - self.block_last_trade < self.min_block_dist:  # type: ignore
            return []

        # Make first trade
        self.tradeback_via_pool = (
            obs.pools[0] if index_pool_first == 1 else obs.pools[1]
        )
        self.block_last_trade = obs.block  # type: ignore
        return [
            UniswapV3Trade(
                agent=self.agent,
                pool=pool,
                quantities=(amount_0, Decimal(0)),
            )
        ]

    # SNIPPET 3 END
