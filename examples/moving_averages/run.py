import os
import sys
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.passiveLP import PassiveConcentratedLP
from policy import MovingAveragePolicy

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=10),
    **kwargs: dict[str, Any],
) -> None:
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
    end_time = start_time + run_length

    # Agents
    mavg_agent = UniswapV3PoolWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="MAvg_Agent",
    )
    lp_agent = UniswapV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="LP_Agent",
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

    passive_lp_policy = PassiveConcentratedLP(
        agent=lp_agent, lower_price_bound=0.95, upper_price_bound=1.05
    )

    # SNIPPET 1 START
    backtest_run(
        env=env,
        policies=[mavg_policy, passive_lp_policy],
        dashboard_server_port=dashboard_server_port,
        output_file="moving_averages.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Moving averages",
        simulation_description="Moving Average Strategy	Also known as mean reversion or mean crossover strategy.",
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(message)s", level=logging.ERROR
    )  # change to logging.INFO for higher verbosity
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
