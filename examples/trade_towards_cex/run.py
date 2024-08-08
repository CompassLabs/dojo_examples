import logging
import os
import sys
from dataclasses import dataclass
from decimal import Decimal

from dateutil import parser as dateparser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import csv
import io
import zipfile
from datetime import datetime
from typing import List

import requests
from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from binance_data import load_binance_data
from policy import TradeTowardsCentralisedExchangePolicy

from dojo.common.constants import Chain
from dojo.environments import UniV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

pools = ["USDC/WETH-0.05"]
year = 2021
month = 6
start_time = dateparser.parse(f"{year}-{month:02}-01 00:00:00 UTC")
end_time = dateparser.parse(f"{year}-{month:02}-10 00:00:00 UTC")

# Agents
cex_directional_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "ETH": Decimal(10),
        "USDC": Decimal(1_000),
        "WETH": Decimal(1),
    },
    name="CEX Directional Agent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
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

_, _ = backtest_run(env, [arb_policy], dashboard_port=8051, auto_close=True)
