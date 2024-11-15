"""A simple agent."""
# SNIPPET 2 START
# SNIPPET 1 START
from decimal import Decimal

from dojo.agents import UniswapV3Agent
from dojo.environments.uniswapV3 import UniswapV3Observation

# SNIPPET 2 END


class ETHAgent(UniswapV3Agent):  # noqa: D101
    def __init__(
        self,
        initial_portfolio: dict[str, Decimal] = {
            "ETH": Decimal(10),
            "USDC": Decimal(10_000),
        },
    ) -> None:  # noqa: D107
        super().__init__(initial_portfolio=initial_portfolio)

    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        """Compute the reward value."""
        return float(self.quantity("ETH"))


# SNIPPET 1 END
