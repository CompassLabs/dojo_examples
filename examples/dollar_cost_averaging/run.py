import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from datetime import timedelta
from typing import Any, Optional

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import DCAPolicy

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=20),
    **kwargs: dict[str, Any]
) -> None:
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
    end_time = start_time + run_length

    # Agents
    dca_agent = UniswapV3PoolWealthAgent(
        initial_portfolio={
            "USDC": Decimal(10000),
            "WETH": Decimal(0),
        },
        name="DCA_Agent",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[dca_agent],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    # Policies
    dca_policy = DCAPolicy(
        agent=dca_agent,
        buying_amount=100.0,
        min_dist=10,
    )

    backtest_run(
        env=env,
        policies=[dca_policy],
        dashboard_server_port=dashboard_server_port,
        output_file="dollar_cost_averaging.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Dollar Cost Averaging",
        simulation_description="Investing in regular intervals.",
    )


if __name__ == "__main__":
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
