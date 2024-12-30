"""Run uniswap RSI strategy on arbitrum."""
import logging
from decimal import Decimal
from typing import Any, Optional

from policy import RSIPolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common import time_to_block
from dojo.common.constants import Chain

# SNIPPET 1 START
from dojo.environments import UniswapV3Env

# SNIPPET 1 END
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    num_sim_blocks: int = 10,
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    pools = ["WETH/USDC-0.05"]
    start_time = "2024-12-06 13:00:00"
    chain = Chain.ARBITRUM

    # Agents
    rsi_agent = TotalWealthAgent(
        initial_portfolio={
            "USDC": Decimal(10000),
            "ETH": Decimal(10),
            "WETH": Decimal(100),
        },
        name="RSI_Agent_Arbitrum",
        unit_token="USDC",
        policy=RSIPolicy(),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ARBITRUM,
        block_range=(
            time_to_block(start_time, chain),
            time_to_block(start_time, chain) + num_sim_blocks,
        ),
        agents=[rsi_agent],
        pools=pools,
        backend_type="forked",
    )

    backtest_run(
        env=env,
        dashboard_server_port=dashboard_server_port,
        output_file="rsi_arbitrum.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="RSI",
        simulation_description="Investing according the the Relative Strenght Indicator (RSI) index.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=10,
    )
