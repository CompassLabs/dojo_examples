"""Run GMXv2 limit order strategy."""
from decimal import Decimal
from typing import Any, Optional

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
    num_sim_blocks: int = 5000,
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    # SNIPPET 1 START
    start_block = 248100522

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
        block_range=(
            start_block,
            start_block + num_sim_blocks,
        ),
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
        dashboard_server_port=dashboard_server_port,
        output_file="gmxV2_limit_orders.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="GMXv2 Limit Orders",
        simulation_description="GMXv2 Limit Orders",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=5000,
    )
