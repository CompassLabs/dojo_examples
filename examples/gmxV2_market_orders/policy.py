# type: ignore
from decimal import Decimal
from enum import Enum

from dojo.actions.gmxV2.orders.models import (
    GmxBaseTraderOrder,
    GmxDecreaseLongMarketOrder,
    GmxIncreaseLongMarketOrder,
)
from dojo.agents import BaseAgent
from dojo.environments.gmxV2 import GmxV2Observation
from dojo.policies import BasePolicy


# SNIPPET 1 START
class State(Enum):
    NO_POSITION = 0
    POSITION_OPEN = 1
    FINISH = 2


class GmxV2Policy(BasePolicy):
    """Example gmx policy."""

    def __init__(self, agent: BaseAgent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)
        self.state = State.NO_POSITION

    # SNIPPET 1 END

    def predict(self, obs: GmxV2Observation) -> list[GmxBaseTraderOrder]:
        total_trader_pnl = 0
        # SNIPPET 2 START
        gm_token_value, market_pool_value_info = obs.get_market_token_price_for_traders(
            "WETH:WETH:USDC", True
        )
        index_token_price = obs.index_token_price(market_key="WETH:WETH:USDC")
        long_token_price = obs.long_token_price(market_key="WETH:WETH:USDC")
        short_token_price = obs.short_token_price(market_key="WETH:WETH:USDC")
        net_pnl = obs.get_net_pnl(market_key="WETH:WETH:USDC", maximize=True)
        long_pnl = obs.get_pnl(market_key="WETH:WETH:USDC", is_long=True, maximize=True)
        short_pnl = obs.get_pnl(
            market_key="WETH:WETH:USDC", is_long=False, maximize=True
        )
        long_open_interest_with_pnl = obs.get_open_interest_with_pnl(
            market_key="WETH:WETH:USDC", is_long=True, maximize=True
        )
        short_open_interest_with_pnl = obs.get_open_interest_with_pnl(
            market_key="WETH:WETH:USDC", is_long=False, maximize=True
        )
        _ = obs.get_market_info(market_key="WETH:WETH:USDC")

        obs.add_signal("net pnl", net_pnl)
        obs.add_signal("long pnl", long_pnl)
        obs.add_signal("short pnl", short_pnl)
        obs.add_signal("long open interest with pnl", long_open_interest_with_pnl)
        obs.add_signal("short open interest with pnl", short_open_interest_with_pnl)
        obs.add_signal("gm token value", gm_token_value)
        obs.add_signal("index token price", index_token_price)
        obs.add_signal("long token price", long_token_price)
        obs.add_signal("short token price", short_token_price)
        total_trader_pnl = self.agent.reward(obs)
        # SNIPPET 2 END

        index_token_price = obs.index_token_price(market_key="WETH:WETH:USDC")
        # SNIPPET 3 START
        if index_token_price < Decimal(2525) and self.state == State.NO_POSITION:
            self.state = State.POSITION_OPEN
            return [
                GmxIncreaseLongMarketOrder(
                    agent=self.agent,
                    size_delta_usd=Decimal(100000),
                    market_key="WETH:WETH:USDC",
                    token_in_symbol="WETH",
                    collateral_token_symbol="WETH",
                    slippage=200,
                    observations=obs,
                    leverage=Decimal(3),
                )
            ]

        if total_trader_pnl > Decimal(120) and self.state == State.POSITION_OPEN:
            self.state = State.NO_POSITION
            return [
                GmxDecreaseLongMarketOrder(
                    agent=self.agent,
                    size_delta_usd=Decimal(100000),
                    market_key="WETH:WETH:USDC",
                    token_in_symbol="WETH",
                    collateral_token_symbol="WETH",
                    slippage=200,
                    observations=obs,
                    leverage=Decimal(3),
                )
            ]

        if total_trader_pnl < Decimal(-70) and self.state == State.POSITION_OPEN:
            self.state = State.FINISH
            return [
                GmxDecreaseLongMarketOrder(
                    agent=self.agent,
                    size_delta_usd=Decimal(100000),
                    market_key="WETH:WETH:USDC",
                    token_in_symbol="WETH",
                    collateral_token_symbol="WETH",
                    slippage=200,
                    observations=obs,
                    leverage=Decimal(3),
                )
            ]
        # SNIPPET 3 END

        obs.add_signal("Current trader pnl", total_trader_pnl)

        return []
