from typing import Any, Dict

import numpy as np

from dojo.agents import BaseAgent
from dojo.common.types import Action, Observation
from dojo.environments import UniV3Env, uniswapV3
from dojo.network import chain_utils
from dojo.policies import BasePolicy


class DGCapitalPolicy(BasePolicy):
    """Provide liquidity passively to a pool in the sepcified tick bounds"""

    def __init__(
        self, agent: BaseAgent, lower_tick_bound: float, upper_tick_bound: float
    ) -> None:
        super().__init__(agent=agent)
        self.env: UniV3Env = self.agent.env
        self.lower_tick_bound = lower_tick_bound
        self.upper_tick_bound = upper_tick_bound
        self.is_invested = False

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
        token0, token1 = uniswapV3.get_pool_tokens(self.env.pools[0], "ethereum")
        decimals0 = chain_utils.get_decimals(token0)
        decimals1 = chain_utils.get_decimals(token1)
        upper_price = self.upper_tick_bound * spot_price
        lower_price = self.lower_tick_bound * spot_price
        lower_pos_price = uniswapV3.tick_to_price(lower_tick, [decimals0, decimals1])
        upper_pos_price = uniswapV3.tick_to_price(upper_tick, [decimals0, decimals1])

        if lower_pos_price > upper_price or upper_pos_price < lower_price:
            return True
        return False

    def fit():
        pass

    @staticmethod
    def get_amount1_trade(withdraw_quote: np.ndarray, spot_price: float) -> float:
        return withdraw_quote[1] * spot_price - withdraw_quote[0] / (2 * spot_price)

    def get_5050_quote(self, spot_price: float, erc20_portfolio: dict) -> np.ndarray:
        usdc_amount = erc20_portfolio["USDC"]
        weth_amount = erc20_portfolio["WETH"]

        total_value = (usdc_amount + weth_amount * spot_price) * 0.999

        usdc_provided = total_value / 2
        weth_provided = (total_value / 2) / spot_price

        return np.array([usdc_provided, weth_provided], dtype=np.float32)

    def get_swap_given_quote(
        self, spot_price: float, quote: np.ndarray, erc20_portfolio: dict
    ) -> np.ndarray:
        usdc_amount = erc20_portfolio["USDC"]

        usdc_needed = usdc_amount - quote[0]
        rough_weth_needed = -usdc_needed * spot_price

        return np.array([usdc_needed, rough_weth_needed], dtype=np.float32)

    def predict(self, obs: Observation, **kwargs: Dict[str, Any]) -> Action:
        if not self.is_invested:
            pool_idx = 0
            token0, token1 = uniswapV3.get_pool_tokens(
                self.env.pools[pool_idx], "ethereum"
            )
            decimals0 = chain_utils.get_decimals(token0)
            decimals1 = chain_utils.get_decimals(token1)
            tick_spacing = uniswapV3.get_tick_spacing(
                self.env.pools[pool_idx], "ethereum"
            )
            spot_price = (
                obs["virtual_quantities"][0][0][0] / obs["virtual_quantities"][0][0][1]
            )
            wallet_portfolio = self.agent.erc20_portfolio()
            provide_quote = self.get_5050_quote(spot_price, wallet_portfolio)
            swap = self.get_swap_given_quote(
                spot_price, provide_quote, wallet_portfolio
            )
            trade_action = {
                "type": 0,
                "pool": pool_idx,
                "quantities": np.array([swap[0], 0], dtype=np.float32),
                "tick_range": np.array([0, 0], dtype=np.float32),
                "agent": self.agent.id,
                "owner": 0,
            }
            lower_price_range = self.lower_tick_bound * (1 / spot_price)
            upper_price_range = self.upper_tick_bound * (1 / spot_price)
            lower_tick = uniswapV3.price_to_tick(
                lower_price_range, tick_spacing, [decimals0, decimals1]
            )
            uppper_tick = uniswapV3.price_to_tick(
                upper_price_range, tick_spacing, [decimals0, decimals1]
            )
            provide_action = {
                "type": 1,
                "pool": pool_idx,
                "quantities": provide_quote,
                "tick_range": np.array([lower_tick, uppper_tick], dtype=np.float32),
                "agent": self.agent.id,
                "owner": 0,
            }
            self.is_invested = True
            return (
                trade_action,
                provide_action,
            )
        return ()
