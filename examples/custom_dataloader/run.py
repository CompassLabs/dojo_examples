"""Run two agents.

One active one passive.
"""
from decimal import Decimal
from typing import Any, Optional

from custom_loader import CustomDataLoader
from policy import MovingAveragePolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.market_agents.uniswapV3 import HistoricReplayAgent
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int] = 8768,
    simulation_status_bar: bool = False,
    auto_close: bool,
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05"]
    chain = Chain.ETHEREUM
    block_range = 21302933, 21354333

    Loader = CustomDataLoader

    market_agent = HistoricReplayAgent(
        chain=chain, pools=pools, block_range=block_range, Dataloader=Loader
    )

    # Agents
    trader_agent = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(100),
        },
        name="TraderAgent",
        unit_token="USDC",
        policy=MovingAveragePolicy(
            pool="USDC/WETH-0.05", short_window=25, long_window=100
        ),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=chain,
        block_range=block_range,
        agents=[market_agent, trader_agent],
        pools=pools,
        backend_type="forked",
        Dataloader=Loader,
    )

    backtest_run(
        env,
        dashboard_server_port=dashboard_server_port,
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        output_file="custom_dataloader.db",
        simulation_title="Using custom dataloader",
        simulation_description="Using custom dataloader.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
    )
