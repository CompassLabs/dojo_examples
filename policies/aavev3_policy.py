from decimal import Decimal
from typing import List

from dojo.actions.aaveV3 import AAVEv3Borrow, AAVEv3Repay, AAVEv3Supply, AAVEv3Withdraw
from dojo.actions.base_action import BaseAction
from dojo.agents import BaseAgent
from dojo.environments.aaveV3 import AAVEv3Obs
from dojo.policies import BasePolicy


class AAVEv3Policy(BasePolicy):
    """Provide liquidity passively to a pool in the sepcified price bounds."""

    def __init__(self, agent: BaseAgent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)

        self.block_counter = -1
        self.active = True

        self.block2action = {
            500: AAVEv3Supply(agent=self.agent, token_name="WBTC", amount=Decimal("1")),
            1000: AAVEv3Borrow(
                agent=self.agent,
                token_name="BAL",
                amount=Decimal("850"),  # 4852 is max
                mode="variable",
            ),
            # 1500: AAVEv3Borrow(
            #     agent=self.agent,
            #     token_name="USDC",
            #     amount=Decimal("300"),
            #     mode="variable",
            # ),
            # 2000: AAVEv3Supply(
            #     agent=self.agent, token_name="USDC", amount=Decimal("1200")
            # ),
            # 2500: AAVEv3Repay(
            #     agent=self.agent,
            #     token_name="USDC",
            #     amount=Decimal("0.1"),
            #     mode="variable",
            # ),
            # 3000: AAVEv3Withdraw(
            #     agent=self.agent, token_name="WETH", amount=Decimal("0.3")
            # ),
            # 3500: AAVEv3Withdraw(
            #     agent=self.agent, token_name="WETH", amount=Decimal("0.3")
            # ),
        }

    def fit(self):
        pass

    def predict(self, obs: AAVEv3Obs) -> List[BaseAction]:
        self.block_counter += 1
        if self.block_counter in self.block2action:
            return [self.block2action[self.block_counter]]

        return []
