# SNIPPET 2 START
# SNIPPET 1 START
from decimal import Decimal

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniswapV3Env, UniswapV3Observation

# SNIPPET 2 END


class ETHAgent(BaseAgent):
    def __init__(
        self,
        initial_portfolio: dict[str, Decimal] = {
            "ETH": Decimal(10),
            "USDC": Decimal(10_000),
        },
    ) -> None:
        super().__init__(initial_portfolio=initial_portfolio)

    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        return float(self.quantity("ETH"))


# SNIPPET 1 END
