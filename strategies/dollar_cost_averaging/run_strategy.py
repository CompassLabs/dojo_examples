import logging
import os
import sys
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import DCAPolicy

from dojo.environments import UniV3Env
from dojo.runners import backtest_run

pools = ["USDC/WETH-0.05"]
start_time = dateparser.parse("2023-06-21 09:00:00 UTC")
end_time = dateparser.parse("2023-06-24 22:00:00 UTC")

# Agents
dca_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "USDC": Decimal(10000),
        "WETH": Decimal(0),
    },
    name="DCA_Agent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[dca_agent],
    pools=pools,
    backend_type="local",
    market_impact="replay",
)

# Policies
dca_policy = DCAPolicy(
    agent=dca_agent,
    buying_amount=100.0,
    min_dist=10,
)

_, _ = backtest_run(env, [dca_policy], dashboard_port=8051, auto_close=True)
