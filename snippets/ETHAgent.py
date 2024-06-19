# SNIPPET 2 START
from dojo.environments.uniswapV3 import UniV3Obs, UniV3Env
# SNIPPET 2 END

# SNIPPET 1 START
from decimal import Decimal
from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Obs
from dojo.common import Portfolio

class ETHAgent(BaseAgent):
    def __init__(self, initial_portfolio: Portfolio = {"ETH": Decimal(10), "USDC": Decimal(10_000)}) -> None:
        super().__init__(initial_portfolio=initial_portfolio)

    def reward(self, obs: UniV3Obs) -> float:
        return float(self.quantity("ETH"))
# SNIPPET 1 END