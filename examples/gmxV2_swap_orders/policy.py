# type: ignore
"""GMXv2 swap order policy."""
from decimal import Decimal

from dojo.actions import SleepAction
from dojo.actions.gmxV2.orders.models import GmxBaseTraderOrder, GmxSwapOrder
from dojo.environments.gmxV2 import GmxV2Observation
from dojo.policies import GmxV2Policy


class GmxV2Policy(GmxV2Policy):
    """Example gmx policy."""

    def __init__(self) -> None:
        """Initialize the policy."""
        super().__init__()

    def predict(self, obs: GmxV2Observation) -> list[GmxBaseTraderOrder]:
        """Derive actions from observations."""
        actions = []
        actions.append(
            GmxSwapOrder(
                agent=self.agent,
                in_token="USDC",  # swap USDC to PEPE
                out_token="PEPE",
                in_token_amount=Decimal(100),  # number of tokens in start_token amount
                slippage=300,  # 3% slippage
                observations=obs,
            )
        )
        actions.append(
            SleepAction(agent=self.agent, number_of_blocks_to_sleep=19)
        )  # only run once every 20 blocks
        return actions
