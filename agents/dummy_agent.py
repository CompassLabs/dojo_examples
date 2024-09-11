from decimal import Decimal
from typing import Optional

from dojo.agents import BaseAgent
from dojo.environments.aaveV3 import AAVEv3Observation


class DummyAgent(BaseAgent):
    """An agent that does not have any particular objective."""

    def __init__(
        self, initial_portfolio: dict[str, Decimal], name: Optional[str] = None
    ):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: AAVEv3Observation) -> float:  # type: ignore
        """This agent does not measure reward."""
        return 0.0
