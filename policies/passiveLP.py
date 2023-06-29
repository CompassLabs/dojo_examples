from decimal import Decimal
from typing import Any, Dict, List, Tuple

import numpy as np

from dojo import money
from dojo.agents import BaseAgent
from dojo.environments import uniswapV3
from dojo.environments.uniswapV3 import UniV3Action, UniV3Obs
from dojo.policies import BasePolicy


class PassiveConcentratedLPPolicy(BasePolicy):
    """Provide liquidity passively to a pool in the sepcified tick bounds"""

    def __init__(
        self, agent: BaseAgent, lower_tick_bound: float, upper_tick_bound: float
    ) -> None:
        super().__init__(agent=agent)
        self.lower_tick_bound = Decimal(lower_tick_bound)
        self.upper_tick_bound = Decimal(upper_tick_bound)
        self.has_invested = True
        self.has_traded = True
        self.agent = agent

    def has_position(self) -> bool:
        return "UNI-V3-POS" in self.agent.portfolio()

    def is_pos_out_of_range(
        self, lower_tick: int, upper_tick: int, spot_price: float
    ) -> bool:
        """
        pos: your LP NFT token ID
        lower: lower percentage bound of the range, e.g. 0.95
        upper: upper percentage bound of the range, e.g. 1.05
        """
        token0, token1 = uniswapV3.get_pool_tokens(
            "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8", "ethereum"
        )
        decimals0 = money.get_decimals(token0)
        decimals1 = money.get_decimals(token1)
        upper_price = self.upper_tick_bound * spot_price
        lower_price = self.lower_tick_bound * spot_price
        lower_pos_price = uniswapV3.tick_to_price(lower_tick, [decimals0, decimals1])
        upper_pos_price = uniswapV3.tick_to_price(upper_tick, [decimals0, decimals1])

        if lower_pos_price > upper_price or upper_pos_price < lower_price:
            return True
        return False

    def fit(self):
        pass

    def initial_trade(self, obs: UniV3Obs) -> List[UniV3Action]:
        pool_idx = 0
        pool_address = obs.pools[pool_idx]
        token0, token1 = obs.pool_tokens(obs.pools[pool_idx])
        spot_price = obs.price("WETH", "USDC", pool_address)
        wallet_portfolio = self.agent.erc20_portfolio()
        # swap = self.get_swap_given_quote(
        #     spot_price, [wallet_portfolio[token0], Decimal(0)], wallet_portfolio
        # )
        trade_action = UniV3Action(
            agent=self.agent,
            type="trade",
            pool=pool_address,
            quantities=(wallet_portfolio[token0], Decimal(0)),
            tick_range=(0, 0),
        )
        self.has_traded = True
        return [trade_action]

    def inital_quote(self, obs: UniV3Obs) -> List[UniV3Action]:
        pool_idx = 0
        pool_address = obs.pools[pool_idx]
        token0, token1 = obs.pool_tokens(obs.pools[pool_idx])
        spot_price = obs.price("WETH", "USDC", pool_address)
        wallet_portfolio = self.agent.erc20_portfolio()
        decimals0 = money.get_decimals(
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        )  # USDC
        decimals1 = money.get_decimals(
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        )  # WETH

        lower_price_range = self.lower_tick_bound * (1 / spot_price)
        upper_price_range = self.upper_tick_bound * (1 / spot_price)
        tick_spacing = uniswapV3.get_tick_spacing(pool_address, "ethereum")

        lower_tick = uniswapV3.price_to_tick(
            lower_price_range, tick_spacing, [decimals0, decimals1]
        )
        upper_tick = uniswapV3.price_to_tick(
            upper_price_range, tick_spacing, [decimals0, decimals1]
        )
        provide_action = UniV3Action(
            agent=self.agent,
            type="quote",
            pool=pool_address,
            quantities=[wallet_portfolio[token0], wallet_portfolio[token1]],
            tick_range=(lower_tick, upper_tick),
        )
        self.has_invested = True
        return [provide_action]

    def predict(self, obs: UniV3Obs, **kwargs: Dict[str, Any]) -> List[UniV3Action]:

        if not self.has_traded:
            return self.initial_trade(obs)
        if not self.has_invested:
            return self.inital_quote(obs)
        return []
