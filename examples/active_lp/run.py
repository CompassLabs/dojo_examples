import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from examples.active_lp.policy import ActiveConcentratedLP

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

# Example logging configuration which:
# - by default, it logs only INFO
# - logs DEBUG messages only from "dojo.network"
# For more config options, see: https://docs.python.org/3.12/howto/logging-cookbook.html#customizing-handlers-with-dictconfig
logging.getLogger("dojo.network").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main() -> None:
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2023-05-01 00:00:00 UTC")
    end_time = dateparser.parse("2023-05-02 00:00:00 UTC")

    agent2 = UniswapV3PoolWealthAgent(
        initial_portfolio={
            "USDC": Decimal(1_000_000),
            "WETH": Decimal(2_000),
            "ETH": Decimal(10),
        },
        name="LPAgent",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[agent2],
        pools=pools,
        backend_type="local",
        market_impact="replay_trades_only",
    )

    active_lp_policy = ActiveConcentratedLP(agent=agent2, lp_width=2)

    backtest_run(env, [active_lp_policy], dashboard_server_port=8051, auto_close=True)
    # SNIPPET 1 END


if __name__ == "__main__":
    main()
