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


class GmxV2Policy(BasePolicy):
    """Example gmx policy."""

    def __init__(self, agent: BaseAgent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)
        self.count = 0

    def fit(self):
        pass

    def predict(self, obs: GmxV2Observation) -> list[BaseTraderOrder]:
        # return []
        self.count += 1
        match self.count % 10:
            case 0:
                return [
                    IncreaseLongMarketOrder.from_parameters(
                        agent=self.agent,
                        initial_collateral_delta_amount=10**17,
                        market_key="WETH:WETH:USDC",
                        token_in_symbol="WETH",
                        collateral_token_symbol="WETH",
                        is_long=True,
                        slippage=0.01,
                    )
                ]
            # case 1:
            #     return [
            #         IncreaseShortMarketOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
            # case 2:
            #     return [
            #         IncreaseLongLimitOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             trigger_price=10**18,
            #             acceptable_price=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
            # case 3:
            #     return [
            #         IncreaseShortLimitOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             trigger_price=10**18,
            #             acceptable_price=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
            # case 4:
            #     return [
            #         DecreaseLongMarketOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
            # case 5:
            #     return [
            #         DecreaseShortMarketOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
            # case 6:
            #     return [
            #         DecreaseLongLimitOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             trigger_price=10**18,
            #             acceptable_price=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
            # case 7:
            #     return [
            #         DecreaseShortLimitOrder.from_parameters(
            #             agent=self.agent,
            #             initial_collateral_delta_amount=10**18,
            #             trigger_price=10**18,
            #             acceptable_price=10**18,
            #             market_key="WETH:WETH:USDC",
            #             token_in_symbol="WETH",
            #             collateral_token_symbol="WETH",
            #             slippage=0.01,
            #         )
            #     ]
        return []
