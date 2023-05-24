from dojo.agents import BaseAgent
from dojo.common.types import BaseObs, Portfolio
from dojo.environments import UniV3Env


class DummyAgent(BaseAgent):
    """This agent implements an IL reward function for a single UniV3 pool."""

    def __init__(self, initial_portfolio: dict):
        super().__init__(initial_portfolio=initial_portfolio)
        self.hold_portfolio = None

    def reward(self, obs: BaseObs) -> float:  # TODO(lukas)
        """TODO."""
        return 0.0
