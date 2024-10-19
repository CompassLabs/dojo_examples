from typing import List

from dojo.actions.base_action import BaseAction
from dojo.agents.base_agent import BaseAgent
from dojo.observations import BaseObservation
from dojo.policies import BasePolicy


class SingleAction(BasePolicy):  # type: ignore
    """A policy that executes a single action.

    This is useful for testing the impact of a single action in an environment. For
    example, you might want to see what the final price in a UniswapV3 pool would be if
    you executed a single swap.
    """

    def __init__(self, agent: BaseAgent, action: BaseAction) -> None:  # type: ignore
        """Initialize the policy.

        :param agent: The agent which is using this policy.
        :param action: The action to execute.
        """
        super().__init__(agent)
        self.action = action
