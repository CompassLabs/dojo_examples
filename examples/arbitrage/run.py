import logging
import os
import sys
from decimal import Decimal

from dateutil import parser as dateparser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from policy import ArbitragePolicy

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

pools = ["USDC/WETH-0.05", "USDC/WETH-0.3"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:10:00 UTC")

# Agents
arb_agent = UniswapV3PoolWealthAgent(
    initial_portfolio={
        "ETH": Decimal(100),
        "USDC": Decimal(10000),
        "WETH": Decimal(0),
    },
    name="Arbitrage_Agent",
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
    dashboard_server_port=8051,
    output_dir="./",
    auto_close=True,
)
