# type: ignore
import logging
import os
import sys
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from datetime import timedelta

from policy import GmxV2Policy

from dojo.agents import BaseAgent
from dojo.common.constants import Chain
from dojo.environments import GmxV2Env
from dojo.models.gmxV2.market import MarketVenue
from dojo.observations.gmxV2 import GmxV2Observation
from dojo.runners import backtest_run


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


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=20),
    **kwargs: dict[str, Any]
) -> None:
    # SNIPPET 1 START
    start_time = dateparser.parse("2024-08-30 00:00:00 UTC")
    end_time = start_time + run_length

    market_venue = MarketVenue(
        long_token="WETH",
        short_token="USDC",
        index_token="WETH",
    )

    # Agents
    gmx_agent = GmxV2Agent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(30000),
            "WETH": Decimal(200),
        },
        name="GMX_Agent",
    )

    # Simulation environment
    env = GmxV2Env(
        chain=Chain.ARBITRUM,
        date_range=(start_time, end_time),
        agents=[gmx_agent],
        market_venues=[market_venue],
        market_impact="replay",
        backend_type="forked",
    )

    # Policies
    policy = GmxV2Policy(agent=gmx_agent)

    backtest_run(
        env=env,
        policies=[policy],
        dashboard_server_port=dashboard_server_port,
        output_file="gmxV2_market_orders.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="GMXv2 Market Orders",
        simulation_description="GMXv2 Market Orders",
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
