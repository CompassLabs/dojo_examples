import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import DCAPolicy

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

pools = ["USDC/WETH-0.05"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:20:00 UTC")

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
    dashboard_server_port=8051,
    output_dir="./",
    auto_close=True,
)
