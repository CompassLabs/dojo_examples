"""Run the free sample period."""
from decimal import Decimal
from typing import Any, Optional

from passiveLP import PassiveConcentratedLP
from policy import MovingAveragePolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.market_agents.uniswapV3 import HistoricReplayAgent
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int] = 8768,
    simulation_status_bar: bool = False,
    auto_close: bool,
    num_sim_blocks: int,
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    start_time = "2024-12-01 00:00:00"
    chain = Chain.ETHEREUM
    block_range = (
        time_to_block(start_time, chain),
        time_to_block(start_time, chain) + num_sim_blocks,
    )

    # Agents
    market_agent = HistoricReplayAgent(
        chain=chain, pools=pools, block_range=block_range
    )

    agent1 = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="TraderAgent",
        unit_token="USDC",
        policy=MovingAveragePolicy(
            pool="USDC/WETH-0.05", short_window=25, long_window=100
        ),
    )

    agent2 = TotalWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="LPAgent",
        unit_token="USDC",
        policy=PassiveConcentratedLP(lower_price_bound=0.95, upper_price_bound=1.05),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=chain,
        block_range=block_range,
        agents=[market_agent, agent1, agent2],
        pools=pools,
        backend_type="local",
    )

    backtest_run(
        env,
        dashboard_server_port=dashboard_server_port,
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=600,
        # number of blocks in 2 hours
    )
