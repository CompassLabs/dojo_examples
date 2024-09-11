from datetime import timedelta
from decimal import Decimal
from typing import List, Tuple

from binance_data import Binance_data, Binance_data_point

from dojo.actions.uniswapV3 import UniswapV3Action, UniswapV3Trade
from dojo.agents import UniswapV3Agent
from dojo.environments.uniswapV3 import UniswapV3Observation
from dojo.network import block_date
from dojo.policies import BasePolicy

USDC = "USDC"
WETH = "WETH"


class TradeTowardsCentralisedExchangePolicy(
    BasePolicy[UniswapV3Action, UniswapV3Agent, UniswapV3Observation]
):
    """Arbitrage trading policy for a UniswapV3Env with two pools.

    :param agent: The agent which is using this policy.
    """

    PERCENTAGE_THRESHOLD = 0.01
    DEFAULT_WEALTH_TRADE_PERCENTAGE = 0.5
    TIME_ADVANTAGE = timedelta(minutes=16.0)

    # SNIPPET 1 START
    def __init__(self, agent: UniswapV3Agent, binance_data: Binance_data) -> None:
        super().__init__(agent=agent)
        self.binance_data = binance_data

    # SNIPPET 1 END

    def predict(self, obs: UniswapV3Observation) -> List[UniswapV3Action]:
        pool = obs.pools[0]
        pool_tokens = obs.pool_tokens(pool)
        dex_usdc_per_eth = float(obs.price(WETH, USDC, pool))
        initial_portfolio = self.agent.initial_portfolio
        initial_usdc = initial_portfolio[USDC]
        initial_weth = initial_portfolio[WETH]

        block = obs.block
        # let's run every tenth block
        if block % 10 != 0:  # type: ignore
            return []

        date = obs.backend.block_to_datetime(block) + self.TIME_ADVANTAGE  # type: ignore
        # SNIPPET 2 START
        # inside [ def predict(self, obs: UniswapV3Observation -> List[UniswapV3Action]: ]
        binance_data_point = self.binance_data.find_nearest(date)
        cex_usdc_per_eth = (binance_data_point.open_ + binance_data_point.close) / 2.0
        # SNIPPET 2 END

        wallet_porfolio = self.agent.erc20_portfolio()
        usdc_amount = wallet_porfolio[USDC]
        weth_amount = wallet_porfolio[WETH]
        usdc_trade_amount = min(
            float(usdc_amount) * 0.95,
            float(initial_usdc) * self.DEFAULT_WEALTH_TRADE_PERCENTAGE,
        )
        weth_trade_amount = min(
            float(weth_amount) * 0.95,
            float(initial_weth) * self.DEFAULT_WEALTH_TRADE_PERCENTAGE,
        )

        # SNIPPET 3 START
        if (
            dex_usdc_per_eth - cex_usdc_per_eth
        ) / cex_usdc_per_eth > self.PERCENTAGE_THRESHOLD:
            if usdc_trade_amount < 0.001:
                return []
            return [
                UniswapV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(Decimal(usdc_trade_amount), Decimal(0)),
                )
            ]
            # (and then the same in the other direction)
            # SNIPPET 3 END
        elif (
            cex_usdc_per_eth - dex_usdc_per_eth
        ) / cex_usdc_per_eth > self.PERCENTAGE_THRESHOLD:
            if weth_trade_amount < 0.000001:
                return []
            return [
                UniswapV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(Decimal(0), Decimal(weth_trade_amount)),
                )
            ]
        else:
            return []
