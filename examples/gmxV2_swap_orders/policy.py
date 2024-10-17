# type: ignore
from decimal import Decimal

from dojo.actions.gmxV2.orders.models import GmxBaseTraderOrder, GmxSwapOrder
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

    def predict(self, obs: GmxV2Observation) -> list[GmxBaseTraderOrder]:
        if self.count % 10 == 0:
            self.count = 1
            return [
                GmxSwapOrder(
                    agent=self.agent,
                    in_token="USDC",  # swap USDC to PEPE
                    out_token="PEPE",
                    in_token_amount=Decimal(
                        100
                    ),  # number of tokens in start_token amount
                    slippage=300,  # 3% slippage
                    observations=obs,
                )
            ]
        self.count += 1
        return []
