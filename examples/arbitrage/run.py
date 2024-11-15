"""Run arbitrage strategy on Uniswap."""
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser
from policy import ArbitragePolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=10),
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05", "USDC/WETH-0.3"]
    start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
    end_time = start_time + run_length

    # Agents
    arb_agent = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10000),
            "WETH": Decimal(0),
        },
        name="Arbitrage_Agent",
        unit_token="USDC",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[arb_agent],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    # Policies
    arb_policy = ArbitragePolicy(agent=arb_agent)

    backtest_run(
        env=env,
        policies=[arb_policy],
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
        run_length=timedelta(hours=2),
    )
