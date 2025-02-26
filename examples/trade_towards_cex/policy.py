"""Example running a policy with Binance data."""
from datetime import timedelta
from decimal import Decimal
from enum import Enum

from binance_data import Binance_data

from dojo.actions.uniswapV3 import BaseUniswapV3Action, UniswapV3Trade
from dojo.environments.uniswapV3 import UniswapV3Observation
from dojo.policies import UniswapV3Policy


class State(Enum):
    """The agent is always in on of these states."""

    FROZEN = 0
    NOT_INVESTED = 1
    IN_TOKEN0 = 2
    IN_TOKEN1 = 3


class TradeTowardsCentralisedExchangePolicy(UniswapV3Policy):
    """Arbitrage trading policy for a UniswapV3Env with two pools.

    :param agent: The agent which is using this policy.
    """

    PERCENTAGE_THRESHOLD = 0.01
    DEFAULT_WEALTH_TRADE_PERCENTAGE = 0.5
    TIME_ADVANTAGE = timedelta(minutes=16.0)
    FREEZE_BLOCKS = 200

    # SNIPPET 1 START
    def __init__(self, binance_data: Binance_data) -> None:  # noqa: D107
        super().__init__()
        self.binance_data = binance_data
        self.block_last_trade: int = 0
        self.state = State.NOT_INVESTED

    # SNIPPET 1 END

    def predict(self, obs: UniswapV3Observation) -> list[BaseUniswapV3Action]:
        """Derive actions from observations."""
        block = obs.block
        obs.add_signal("state", float(self.state.value))
        if not block or block - self.block_last_trade < self.FREEZE_BLOCKS:
            return []

        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        dex_usdc_per_eth = float(obs.price(token1, token0, pool))

        date = obs.backend.block_to_datetime(block) + self.TIME_ADVANTAGE
        # SNIPPET 2 START
        # inside [ def predict(self, obs: UniswapV3Observation -> List[UniswapV3Action]: ]
        binance_data_point = self.binance_data.find_nearest(date)
        cex_usdc_per_eth = (binance_data_point.open_ + binance_data_point.close) / 2.0
        # SNIPPET 2 END

        diff = (dex_usdc_per_eth - cex_usdc_per_eth) / dex_usdc_per_eth

        obs.add_signal("cex_usdc_per_eth", cex_usdc_per_eth)
        obs.add_signal("dex_usdc_per_eth", dex_usdc_per_eth)
        obs.add_signal("diff", diff)

        # SNIPPET 3 START
        if diff < -0.025:
            # Buy WETH
            if self.state in [State.NOT_INVESTED, State.IN_TOKEN0]:
                token0_amount = self.agent.erc20_portfolio()[token0]
                self.state = State.IN_TOKEN1
                self.block_last_trade = block
                return [
                    UniswapV3Trade(
                        agent=self.agent,
                        pool=pool,
                        quantities=(Decimal(token0_amount), Decimal(0)),
                    )
                ]
        # SNIPPET 3 END
        elif diff > 0.025:
            # Buy USDC
            if self.state in [State.NOT_INVESTED, State.IN_TOKEN1]:
                token1_amount = self.agent.erc20_portfolio()[token1]
                self.state = State.IN_TOKEN0
                self.block_last_trade = block
                return [
                    UniswapV3Trade(
                        agent=self.agent,
                        pool=pool,
                        quantities=(Decimal(0), Decimal(token1_amount)),
                    )
                ]
        return []
