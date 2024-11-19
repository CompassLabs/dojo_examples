"""Run GMXv2 swap order policy."""
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser
from policy import GmxV2Policy

from dojo.agents import BaseAgent
from dojo.common.constants import Chain
from dojo.environments import GmxV2Env
from dojo.models.gmxV2.market import MarketVenue
from dojo.observations.gmxV2 import GmxV2Observation
from dojo.runners import backtest_run


class GmxV2Agent(BaseAgent[GmxV2Observation]):
    """An agent that does not have any particular objective."""

    def __init__(
        self, initial_portfolio: dict[str, Decimal], name: Optional[str] = None
    ):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio)

    def reward(self, obs: GmxV2Observation) -> float:
        """Pnl in USD."""
        return float(obs.total_trader_pnl(self.original_address))


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=10),
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    # SNIPPET 1 START
    start_time = dateparser.parse("2024-08-30 00:00:00 UTC")
    end_time = start_time + run_length

    market_venue1 = MarketVenue(
        long_token="WETH",
        short_token="USDC",
        index_token="WETH",
    )
    market_venue2 = MarketVenue(
        long_token="PEPE",
        short_token="USDC",
        index_token="PEPE",
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
        market_venues=[market_venue1, market_venue2],
        market_impact="replay",
        backend_type="forked",
    )

    # Policies
    policy = GmxV2Policy(agent=gmx_agent)

    backtest_run(
        env=env,
        policies=[policy],
        dashboard_server_port=dashboard_server_port,
        output_file="gmxV2_swap_orders.db",
        simulation_status_bar=simulation_status_bar,
        auto_close=auto_close,
        simulation_title="GMXv2 Swap Orders",
        simulation_description="GMXv2 Swap Orders",
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
