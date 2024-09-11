import argparse
import logging
from decimal import Decimal
from typing import Union

# Example logging configuration which:
# - by default, it logs only INFO
# - logs DEBUG messages only from "dojo.network"
# For more config options, see: https://docs.python.org/3.12/howto/logging-cookbook.html#customizing-handlers-with-dictconfig
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.ERROR,
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from examples.moving_averages.policy import MovingAveragePolicy
from policies.passiveLP import PassiveConcentratedLP

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run


def main(dashboard_server_port: Union[int, None]) -> None:

    # SNIPPET 1 START
    # pools = ["USDC/WETH-0.3"]
    # start_time = dateparser.parse("2021-06-22 00:00:00 UTC")
    # end_time = dateparser.parse("2021-06-22 12:0:00 UTC")
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2022-06-21 00:00:00 UTC")
    end_time = dateparser.parse("2022-06-21 01:00:00 UTC")

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
        dashboard_server_port=dashboard_server_port
        if dashboard_server_port != -1
        else None,
        output_dir="./",
        auto_close=True,
        simulation_status_bar=True,
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    # Adding a boolean flag
    parser = argparse.ArgumentParser(
        description="Example script for boolean argument with argparse"
    )

    # Adding an optional integer argument with a default value
    parser.add_argument(
        "--dashboard_server_port",
        type=int,
        default=8786,
        help="What port the data should be served on. Can be None, in which case the data is not being served.",
    )

    args = parser.parse_args()
    main(dashboard_server_port=args.dashboard_server_port)
