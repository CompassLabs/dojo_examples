"""Run moving averages strategy on Uniswap."""
from decimal import Decimal
from typing import Any, Optional

from policy import MovingAveragePolicy

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
    num_sim_blocks: int = 3000,
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05"]
    start_time = "2021-06-28 00:00:00"
    chain = Chain.ETHEREUM
    block_range = (
        time_to_block(start_time, chain),
        time_to_block(start_time, chain) + num_sim_blocks,
    )

    # Agents
    market_agent = HistoricReplayAgent(
        chain=chain, pools=pools, block_range=block_range
    )

    mavg_agent = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="MAvg_Agent",
        unit_token="USDC",
        policy=MovingAveragePolicy(
            pool="USDC/WETH-0.05", short_window=25, long_window=100
        ),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        block_range=block_range,
        agents=[market_agent, mavg_agent],
        pools=pools,
        backend_type="forked",  # change to local for better speed
    )

    # SNIPPET 1 START
    backtest_run(
        env=env,
        dashboard_server_port=dashboard_server_port,
        output_file="moving_averages.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Moving averages",
        simulation_description="Moving Average Strategy	Also known as mean reversion or mean crossover strategy.",
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=300,
    )
