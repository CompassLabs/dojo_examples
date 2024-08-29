import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dateutil import parser as dateparser

from demo.agents.univ3_impermanent_loss import ImpermanentLossAgent
from demo.policies.passiveLP import PassiveConcentratedLP
from dojo.common.constants import Chain
from dojo.environments import UniV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

pools = ["USDC/WETH-0.05"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:20:00 UTC")

# Agents
impermanent_loss_agent = ImpermanentLossAgent(
    initial_portfolio={
        "USDC": Decimal(10_000),
        "WETH": Decimal(1),
    },
    name="Impermanent_Loss_Agent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    chain=Chain.ETHEREUM,
    date_range=(start_time, end_time),
    agents=[impermanent_loss_agent],
    pools=pools,
    backend_type="forked",
    market_impact="replay",
)

# Policies
liquidity_policy = PassiveConcentratedLP(
    agent=impermanent_loss_agent,
    lower_price_bound=Decimal(0.95),
    upper_price_bound=Decimal(1.05),
)

_, _ = backtest_run(
    env=env,
    policies=[liquidity_policy],
    dashboard_server_port=8051,
    output_dir="./",
    auto_close=True,
)
