import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from examples.moving_averages.policy import MovingAveragePolicy
from policies.passiveLP import PassiveConcentratedLP

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int] = 8768,
    simulation_status_bar: bool = False,
    auto_close: bool,
    run_length: timedelta = timedelta(hours=1),
    **kwargs: dict[str, Any],
) -> None:

    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2022-06-21 00:00:00 UTC")
    end_time = start_time + run_length

    # Agents
    agent1 = UniswapV3PoolWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="TraderAgent",
    )

    agent2 = UniswapV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="LPAgent",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[agent1, agent2],
        pools=pools,
        backend_type="local",
        market_impact="replay",
    )

    # Policies
    mvag_policy = MovingAveragePolicy(
        agent=agent1, pool="USDC/WETH-0.05", short_window=25, long_window=100
    )

    passive_lp_policy = PassiveConcentratedLP(
        agent=agent2, lower_price_bound=0.95, upper_price_bound=1.05
    )

    backtest_run(
        env,
        [mvag_policy, passive_lp_policy],
        dashboard_server_port=dashboard_server_port,
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.ERROR)

    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
