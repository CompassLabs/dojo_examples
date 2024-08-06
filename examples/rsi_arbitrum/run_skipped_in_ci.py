import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import RSIPolicy

# SNIPPET 1 START
from dojo.environments import UniV3Env

# SNIPPET 1 END
from dojo.runners import backtest_run

# HACK to make tests pass
os.environ["CHAIN"] = "arbitrum"
from dojo.config import cfg
from dojo.config.config import load_network_cfg
cfg.network = load_network_cfg()


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
pools = ["WETH/USDC-0.05"]
start_time = dateparser.parse("2024-05-01 09:08:00 UTC")
end_time = dateparser.parse("2024-05-01 09:20:00 UTC")

# Agents
rsi_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "USDC": Decimal(10000),
        "ETH": Decimal(10),
        "WETH": Decimal(100),
    },
    name="RSI_Agent_Arbitrum",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[rsi_agent],
    pools=pools,
    backend_type="forked",
    market_impact="replay",
)

# Policies
rsi_policy = RSIPolicy(
    agent=rsi_agent,
)

_, _ = backtest_run(env, [rsi_policy], dashboard_port=8051, auto_close=True)
