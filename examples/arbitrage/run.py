import logging
import os
import sys
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import ArbitragePolicy

from dojo.environments import UniV3Env
from dojo.runners import backtest_run

pools = ["USDC/WETH-0.05", "USDC/WETH-0.3"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:10:00 UTC")

# Agents
arb_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "ETH": Decimal(100),
        "USDC": Decimal(10000),
        "WETH": Decimal(0),
    },
    name="Arbitrage_Agent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[arb_agent],
    pools=pools,
    backend_type="forked",
    market_impact="replay",
)

# Policies
arb_policy = ArbitragePolicy(agent=arb_agent)

_, _ = backtest_run(env, [arb_policy], dashboard_port=8051, auto_close=True)
