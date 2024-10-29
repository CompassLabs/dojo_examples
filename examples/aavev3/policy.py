from decimal import Decimal

from dojo.actions.aaveV3 import (
    AAVEv3BorrowToHealthFactor,
    AAVEv3RepayToHealthFactor,
    AAVEv3Supply,
    BaseAaveAction,
)
from dojo.agents import AAVEv3Agent
from dojo.environments.aaveV3 import AAVEv3Observation
from dojo.policies import AAVEv3Policy as BaseAAVEv3Policy


# SNIPPET 1 START
class AAVEv3Policy(BaseAAVEv3Policy):
    """Provide liquidity passively to a pool in the specified price bounds."""

    def __init__(self, agent: AAVEv3Agent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)

        self.has_invested = False

    # SNIPPET 1 END

    # SNIPPET 2 START
    def predict(self, obs: AAVEv3Observation) -> list[BaseAaveAction]:
        if not self.has_invested:
            self.has_invested = True
            return [
                AAVEv3Supply(agent=self.agent, token="USDC", amount=Decimal("30000"))
            ]
        # SNIPPET 2 END
        # SNIPPET 3 START
        health_factor = obs.get_user_account_data_base(
            self.agent.original_address
        ).healthFactor

        if health_factor > 2.0:
            return [
                AAVEv3BorrowToHealthFactor(
                    agent=self.agent, token="WBTC", factor=1.8, mode="variable"
                )
            ]
        if health_factor < 1.7:
            return [
                AAVEv3RepayToHealthFactor(
                    agent=self.agent, token="WBTC", factor=1.90, mode="variable"
                )
            ]
        return []
        # SNIPPET 3 END
