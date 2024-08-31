import logging
import os
import sys
from decimal import Decimal

from dateutil import parser as dateparser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from binance_data import load_binance_data
from policy import TradeTowardsCentralisedExchangePolicy

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

IS_RUNNING_TESTS = os.getenv("IS_RUNNING_TESTS", None) != None

if not IS_RUNNING_TESTS:
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

pools = ["USDC/WETH-0.05"]
year = 2021
month = 6
start_day = 1
if IS_RUNNING_TESTS:
    end_day = 2
else:
    end_day = 10
start_time = dateparser.parse(f"{year}-{month:02}-{start_day:02} 00:00:00 UTC")
end_time = dateparser.parse(f"{year}-{month:02}-{end_day:02} 00:00:00 UTC")

# Agents
cex_directional_agent = UniswapV3PoolWealthAgent(
    initial_portfolio={
        "ETH": Decimal(10),
        "USDC": Decimal(1_000),
        "WETH": Decimal(1),
    },
    name="CEX Directional Agent",
)

# Simulation environment (Uniswap V3)
env = UniswapV3Env(
    chain=Chain.ETHEREUM,
    date_range=(start_time, end_time),
    agents=[cex_directional_agent],
    pools=pools,
    backend_type="forked",
    market_impact="replay",
)

# SNIPPET 1 START
binance_data = load_binance_data(year, month)

# Policies
arb_policy = TradeTowardsCentralisedExchangePolicy(
    agent=cex_directional_agent, binance_data=binance_data
)
# SNIPPET 1 END

_, _ = backtest_run(
    env=env,
    policies=[arb_policy],
    dashboard_server_port=8051,
    output_dir="./",
    auto_close=True,
    simulation_status_bar=IS_RUNNING_TESTS,
)
