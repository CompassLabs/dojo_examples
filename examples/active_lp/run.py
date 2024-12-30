"""Run the active LP strategy."""
from decimal import Decimal
from typing import Any, Optional

from passive_lp_policy import PassiveConcentratedLP
from policy import ActiveConcentratedLP

from dojo.agents.uniswapV3 import PnLAgent
from dojo.common.constants import Chain
from dojo.common.time_to_block import time_to_block
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
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    chain = Chain.ETHEREUM
    start_time = "2024-12-06 13:00:00"
    block_range = (
        time_to_block(start_time, chain),
        time_to_block(start_time, chain) + num_sim_blocks,
    )

    market_agent = HistoricReplayAgent(
        chain=chain, pools=pools, block_range=block_range, mode="swaps_only"
    )

    active_lp_agent = PnLAgent(
        initial_portfolio={
            "USDC": Decimal(2000),
            "WETH": Decimal(1),
        },
        name="ActiveLPAgent",
        unit_token="USDC",
        policy=ActiveConcentratedLP(lp_width=3),
    )

    passive_lp_agent = PnLAgent(
        initial_portfolio={"USDC": Decimal(2000), "WETH": Decimal(1)},
        name="PassiveLPAgent",
        unit_token="USDC",
        policy=PassiveConcentratedLP(lower_price_bound=0.9, upper_price_bound=1.1),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=chain,
        block_range=block_range,
        agents=[market_agent, active_lp_agent, passive_lp_agent],
        pools=pools,
        backend_type="forked",
    )

    backtest_run(
        env,
        dashboard_server_port=dashboard_server_port,
        output_file="active_lp.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Active liquidity provisioning",
        simulation_description="Keep liquidity in the active tick range.",
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=3000,
    )
