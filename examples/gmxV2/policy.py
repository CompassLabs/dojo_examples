from dojo.actions.base_action import BaseAction
from dojo.actions.gmxV2 import (
    CreateOrderParams,
    CreateOrderParamsAddresses,
    CreateOrderParamsNumbers,
    DecreasePositionSwapType,
    Order,
    OrderType,
)
from dojo.agents import BaseAgent
from dojo.environments.gmxV2 import GmxV2Obs
from dojo.policies import BasePolicy


class GmxV2Policy(BasePolicy):
    """Example gmx policy."""

    def __init__(self, agent: BaseAgent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)
        self.count = 0

    def fit(self):
        pass

    def predict(self, obs: GmxV2Obs) -> list[BaseAction]:
        self.count += 1
        addresses = CreateOrderParamsAddresses(receiver=self.agent.original_address)
        numbers = CreateOrderParamsNumbers(
            size_delta_usd=10**16,
            initial_collateral_delta_amount=10**18,
            trigger_price=0,
            acceptable_price=0,
            execution_fee=10**16,
            callback_gas_limit=0,
            min_output_amount=0,
        )
        create_order_params = CreateOrderParams(
            addresses=addresses,
            numbers=numbers,
            order_type=OrderType.MARKET_INCREASE,
            decrease_position_swap_type=DecreasePositionSwapType.NO_SWAP,
            is_long=True,
            should_unwrap_native_token=False,
        )
        if self.count % 10 == 0:
            return [Order(self.agent, create_order_params)]
        return []
