"""Execute a single action."""
from typing import Any

from dojo.actions.base_action import BaseAction
from dojo.policies.base_policy import BasePolicy


class SingleAction(BasePolicy[Any, Any, Any]):
    """A policy that executes a single action.

    This is useful for testing the impact of a single action in an environment. For
    example, you might want to see what the final price in a UniswapV3 pool would be if
    you executed a single swap.
    """

    def __init__(self, action: BaseAction[Any]) -> None:
        """Initialize the policy.

        :param action: The action to execute.
        """
        super().__init__()
        self.action = action
