import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser
from policy import RSIPolicy

from dojo.common.constants import Chain
from dojo.config import cfg
from dojo.config.config import load_network_cfg

# SNIPPET 1 START
from dojo.environments import UniswapV3Env

# SNIPPET 1 END
from dojo.runners import backtest_run

cfg.network = load_network_cfg()


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
pools = ["WETH/USDC-0.05"]
start_time = dateparser.parse("2024-05-01 09:08:00 UTC")
end_time = dateparser.parse("2024-05-01 09:09:00 UTC")

# Agents
rsi_agent = UniswapV3PoolWealthAgent(
    initial_portfolio={
        "USDC": Decimal(10000),
        "ETH": Decimal(10),
        "WETH": Decimal(100),
    },
    name="RSI_Agent_Arbitrum",
)

# Simulation environment (Uniswap V3)
env = UniswapV3Env(
    chain=Chain.ARBITRUM,
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

backtest_run(
    env=env,
    policies=[rsi_policy],
    dashboard_server_port=8051,
    output_dir="./",
    auto_close=True,
)
