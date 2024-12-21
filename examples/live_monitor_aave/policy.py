"""Policy for the AAVE agent."""
from dojo.actions.aaveV3 import BaseAaveAction
from dojo.environments.aaveV3 import AAVEv3Observation
from dojo.policies import AAVEv3Policy as BaseAAVEv3Policy


# SNIPPET 1 START
class AAVEv3Policy(BaseAAVEv3Policy):
    """Provide liquidity passively to a pool in the specified price bounds."""

    def __init__(self) -> None:
        """Initialize the policy."""
        super().__init__()

    def predict(self, obs: AAVEv3Observation) -> list[BaseAaveAction]:
        """Tracking a number of accounts."""
        user_account_data_base = obs.get_user_account_data_base(
            self.agent.account.address
        )
        total_collateral = user_account_data_base.totalCollateral
        obs.add_signal(
            name=f"Total Collateral {self.agent.account.address}",
            value=total_collateral,
        )

        return []
