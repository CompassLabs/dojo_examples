import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import RSIPolicy

from dojo.common.constants import Chain

# SNIPPET 1 START
from dojo.environments import UniV3Env

# SNIPPET 1 END
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
pools = ["USDC/WETH-0.05"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:10:00 UTC")

# Agents
rsi_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "USDC": Decimal(10000),
        "WETH": Decimal(10),
    },
    name="RSI_Agent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    chain=Chain.ETHEREUM,
    date_range=(start_time, end_time),
    agents=[rsi_agent],
    pools=pools,
    backend_type="local",
    market_impact="replay",
)

# Policies
rsi_policy = RSIPolicy(
    agent=rsi_agent,
)

_, _ = backtest_run(env, [rsi_policy], dashboard_port=8051, auto_close=True)
