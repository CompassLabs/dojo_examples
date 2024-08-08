import logging
from decimal import Decimal
from typing import Optional

from dateutil import parser as dateparser
from policy import AAVEv3Policy

from dojo.agents import AAVEv3Agent
from dojo.common.constants import Chain
from dojo.environments import AAVEv3Env
from dojo.environments.aaveV3 import AAVEv3Obs
from dojo.runners import backtest_run

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


class ConstantRewardAgent(AAVEv3Agent):
    """An agent that does not have any particular objective."""

    def __init__(self, initial_portfolio: dict, name: Optional[str] = None):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: AAVEv3Obs) -> float:
        """This agent does not measure reward."""
        return 0


def main() -> None:
    start_time = dateparser.parse("2023-03-11 00:00:00 UTC")
    end_time = dateparser.parse("2023-03-11 00:10:00 UTC")

    # Agents
    agent1 = ConstantRewardAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(30000),
            "WBTC": Decimal(2),
        },
        name="AAVE_Agent",
    )

    # Simulation environment (AAVE V3)
    env = AAVEv3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[agent1],
        backend_type="forked",
        market_impact="default",
    )

    # Policies
    policy = AAVEv3Policy(agent=agent1)

    _, _ = backtest_run(env, [policy], dashboard_port=8051, auto_close=True)


if __name__ == "__main__":
    main()
