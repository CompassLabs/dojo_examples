# type: ignore
import logging
from decimal import Decimal
from typing import Optional

from dateutil import parser as dateparser
from policy import GmxV2Policy

from dojo.agents import BaseAgent
from dojo.common.constants import Chain
from dojo.environments import GmxV2Env
from dojo.models.gmxV2.market import MarketVenue
from dojo.observations.gmxV2 import GmxV2Observation
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class GmxV2Agent(BaseAgent):
    """An agent that does not have any particular objective."""

    def __init__(
        self, initial_portfolio: dict[str, Decimal], name: Optional[str] = None
    ):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: GmxV2Observation) -> float:
        """PnL in USD."""
        return obs.total_trader_pnl(self.original_address)


def main() -> None:
    # SNIPPET 1 START
    start_time = dateparser.parse("2024-08-30 00:00:00 UTC")
    end_time = dateparser.parse("2024-08-30 00:25:00 UTC")

    # SNIPPET 2 START
    market_venue = MarketVenue(
        long_token="WETH",
        short_token="USDC",
        index_token="WETH",
    )
    # SNIPPET 2 END

    # Agents
    agent1 = GmxV2Agent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(30000),
            "WETH": Decimal(200),
        },
        name="GMXAgent",
    )

    # Simulation environment
    # SNIPPET 1 START
    env = GmxV2Env(
        chain=Chain.ARBITRUM,
        date_range=(start_time, end_time),
        agents=[agent1],
        market_venues=[market_venue],
        market_impact="no_market",
        backend_type="forked",
    )
    # SNIPPET 1 END

    # Policies
    policy = GmxV2Policy(agent=agent1)

    backtest_run(
        env=env,
        policies=[policy],
        dashboard_server_port=8051,
        output_dir="./",
        auto_close=False,
    )


if __name__ == "__main__":
    main()
