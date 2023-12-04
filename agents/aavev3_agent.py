from typing import Optional

from dojo.agents import BaseAgent
from dojo.environments.aaveV3 import AAVEv3Obs


class AAVEv3Agent(BaseAgent):
    """This agent implements a pool wealth reward function for a single UniV3 pool.

    The agent should not be given any tokens that are not in the UniV3Env pool.
    """

    def __init__(self, initial_portfolio: dict, name: Optional[str] = None):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: AAVEv3Obs) -> float:
        """The agent wealth in units of asset y according to the UniV3 pool."""
        return 0
