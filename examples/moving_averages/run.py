"""Run moving averages strategy on Uniswap."""
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser
from policy import MovingAveragePolicy

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
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-28 00:00:00 UTC")
    end_time = start_time + run_length

    # Agents
    mavg_agent = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="MAvg_Agent",
        unit_token="USDC",
    )
    lp_agent = TotalWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="LP_Agent",
        unit_token="USDC",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[mavg_agent, lp_agent],
        pools=pools,
        backend_type="forked",  # change to local for better speed
        market_impact="replay",
    )

    # Policies
    mavg_policy = MovingAveragePolicy(
        agent=mavg_agent, pool="USDC/WETH-0.05", short_window=25, long_window=100
    )

    # SNIPPET 1 START
    backtest_run(
        env=env,
        policies=[mavg_policy],
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
        run_length=timedelta(hours=2),
    )
