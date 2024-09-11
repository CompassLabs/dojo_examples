# type: ignore
from dojo.actions.gmxV2.orders.base_models import BaseTraderOrder
from dojo.actions.gmxV2.orders.models import (
    DecreaseLongLimitOrder,
    DecreaseLongMarketOrder,
    DecreaseShortLimitOrder,
    DecreaseShortMarketOrder,
    IncreaseLongLimitOrder,
    IncreaseLongMarketOrder,
    IncreaseShortLimitOrder,
    IncreaseShortMarketOrder,
)
from dojo.agents import BaseAgent
from dojo.environments.gmxV2 import GmxV2Observation
from dojo.policies import BasePolicy
from dojo.utils.gmxV2.position import get_position_key


class GmxV2Policy(BasePolicy):
    """Example gmx policy."""

    def __init__(self, agent: BaseAgent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)
        self.count = 0

    def fit(self):
        pass

    def predict(self, obs: GmxV2Observation) -> list[BaseTraderOrder]:
        positions = obs.get_account_positions(self.agent.original_address)
        total_trader_pnl = 0
        gm_token_value, market_pool_value_info = obs.get_market_token_price_for_traders(True)
        index_token_price = obs.index_token_price()
        long_token_price = obs.long_token_price()
        short_token_price = obs.short_token_price()
        net_pnl = obs.get_net_pnl(True)
        long_pnl = obs.get_pnl(True, True)
        short_pnl = obs.get_pnl(False, True)
        long_open_interest_with_pnl = obs.get_open_interest_with_pnl(True, True)
        short_open_interest_with_pnl = obs.get_open_interest_with_pnl(False, True)
        market_info = obs.get_market_info()
        
        obs.add_signal("Net_Pnl", net_pnl)
        obs.add_signal("Long_Pnl", long_pnl)
        obs.add_signal("Short_Pnl", short_pnl)
        obs.add_signal("Long_Open_Interest_With_Pnl", long_open_interest_with_pnl)
        obs.add_signal("Short_Open_Interest_With_Pnl", short_open_interest_with_pnl)
        obs.add_signal("GM_Token_Value", gm_token_value)
        obs.add_signal("Index_Token_Price", index_token_price)
        obs.add_signal("Long_Token_Price", long_token_price)
        obs.add_signal("Short_Token_Price", short_token_price)

        for position in positions:
            position_pnl = obs.get_position_pnl_usd(position)
            total_trader_pnl += position_pnl.position_pnl_usd
            
        obs.add_signal("Total_Trader_Pnl", total_trader_pnl)

        if total_trader_pnl == 0:
            return [
                IncreaseLongMarketOrder.from_parameters(
                    agent=self.agent,
                    initial_collateral_delta_amount=10**17,
                    market_key="WETH:WETH:USDC",
                    token_in_symbol="WETH",
                    collateral_token_symbol="WETH",
                    slippage=0.01,
                )
            ]
        return []
