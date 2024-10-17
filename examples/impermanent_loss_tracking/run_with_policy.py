import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dateutil import parser as dateparser

from demo.agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from demo.examples.impermanent_loss_tracking.policy import ImpermanentLossPolicy
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

pools = ["USDC/WETH-0.05"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:20:00 UTC")

# Agents
impermanent_loss_agent = UniswapV3PoolWealthAgent(
    initial_portfolio={
        "USDC": Decimal(10_000),
        "WETH": Decimal(1),
    },
    name="Impermanent_Loss_Agent",
)

# Simulation environment (Uniswap V3)
env = UniswapV3Env(
    chain=Chain.ETHEREUM,
    date_range=(start_time, end_time),
    agents=[impermanent_loss_agent],
    pools=pools,
    backend_type="forked",
    market_impact="replay",
)

# Policies
impermanent_loss_policy = ImpermanentLossPolicy(
    agent=impermanent_loss_agent,
)

backtest_run(
    env=env,
    policies=[impermanent_loss_policy],
    dashboard_server_port=8051,
    output_file="impermanent_loss_tracking.db",
    auto_close=True,
    simulation_title="Impermanent Loss Tracking",
    simulation_description="Comparing a passive LP agent to a HODL agent to measure IL.",
)
