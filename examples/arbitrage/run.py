"""Run arbitrage strategy on Uniswap."""
from decimal import Decimal
from typing import Any, Optional

from policy import ArbitragePolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.market_agents.uniswapV3 import HistoricReplayAgent
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    num_sim_blocks: int = 1800,
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05", "USDC/WETH-0.3"]
    start_time = "2024-12-06 13:00:00"
    chain = Chain.ETHEREUM
    block_range = (
        time_to_block(start_time, chain),
        time_to_block(start_time, chain) + num_sim_blocks,
    )

    # Agents
    market_agent = HistoricReplayAgent(
        chain=chain, pools=pools, block_range=block_range
    )

    arb_agent = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10000),
            "WETH": Decimal(0),
        },
        name="Arbitrage_Agent",
        unit_token="USDC",
        policy=ArbitragePolicy(),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        block_range=block_range,
        agents=[market_agent, arb_agent],
        pools=pools,
        backend_type="forked",
    )

    backtest_run(
        env=env,
        dashboard_server_port=dashboard_server_port,
        output_file="arbitrage.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Arbitrage",
        simulation_description="Arbitraging between 2 uniswap pools that trade the same tokens.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=600,
    )
