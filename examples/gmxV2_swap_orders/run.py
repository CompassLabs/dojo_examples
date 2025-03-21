"""Run GMXv2 swap order policy."""
from decimal import Decimal
from typing import Any, Optional

from policy import GmxV2Policy

from dojo.agents import BaseAgent
from dojo.common.constants import Chain
from dojo.environments import GmxV2Env
from dojo.market_agents.gmxV2 import HistoricReplayAgent
from dojo.models.gmxV2.market import MarketVenue
from dojo.observations.gmxV2 import GmxV2Observation
from dojo.runners import backtest_run


class GmxV2Agent(BaseAgent[GmxV2Observation]):
    """An agent that does not have any particular objective."""

    def __init__(
        self,
        policy: Any,
        initial_portfolio: dict[str, Decimal],
        name: Optional[str] = None,
    ):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio, policy=policy)

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
    chain = Chain.ARBITRUM
    block_range = (
        start_block,
        start_block + num_sim_blocks,
    )

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
    market_agent = HistoricReplayAgent(
        chain=chain,
        block_range=block_range,
        market_venues=[market_venue1, market_venue2],
    )

    gmx_agent = GmxV2Agent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(30000),
            "WETH": Decimal(200),
        },
        name="GMX_Agent",
        policy=GmxV2Policy(),
    )

    # Simulation environment
    env = GmxV2Env(
        chain=chain,
        block_range=block_range,
        agents=[market_agent, gmx_agent],
        market_venues=[market_venue1, market_venue2],
        backend_type="forked",
    )

    backtest_run(
        env=env,
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
        num_sim_blocks=5000,
    )
