"""Run a strategy on AAVE."""
from decimal import Decimal
from typing import Any, Optional

from policy import AAVEv3Policy

from dojo.agents import AAVEv3Agent
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments import AAVEv3Env
from dojo.environments.aaveV3 import AAVEv3Observation
from dojo.market_agents.aaveV3 import HistoricReplayAgent
from dojo.runners import backtest_run


class ConstantRewardAgent(AAVEv3Agent):
    """An agent that displays health factor as its reward."""

    def __init__(
        self,
        policy: Any,
        initial_portfolio: dict[str, Decimal],
        name: Optional[str] = None,
    ):
        """Initialize the agent."""
        super().__init__(name=name, initial_portfolio=initial_portfolio, policy=policy)

    def reward(self, obs: AAVEv3Observation) -> float:
        """Tracks the health factor of the agent."""
        return obs.get_user_account_data_base(self.original_address).healthFactor


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    num_sim_blocks: int = 1800,
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    start_time = "2024-12-16 14:00:00"
    chain = Chain.ETHEREUM
    block_range = (
        time_to_block(start_time, chain),
        time_to_block(start_time, chain) + num_sim_blocks,
    )
    # Agents
    market_agent = HistoricReplayAgent(chain=chain, block_range=block_range)
    agent1 = ConstantRewardAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(30000),
            "WBTC": Decimal(2),
        },
        name="AAVE_Agent",
        policy=AAVEv3Policy(),
    )

    # SNIPPET 1 START
    env = AAVEv3Env(
        chain=Chain.ETHEREUM,
        block_range=block_range,
        agents=[market_agent, agent1],
        backend_type="forked",
    )
    # SNIPPET 1 END

    backtest_run(
        env=env,
        dashboard_server_port=dashboard_server_port,
        output_file="aavev3.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="AAVE strategy",
        simulation_description="This example is maintaining a position between 2 health factor thresholds.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=300,
    )
