import logging
import os
import sys
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.passiveLP import PassiveConcentratedLP
from policy import MovingAveragePolicy

from dojo.environments import UniV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
pools = ["USDC/WETH-0.05"]
start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
end_time = dateparser.parse("2021-06-21 00:10:00 UTC")

# Agents
mavg_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "ETH": Decimal(100),
        "USDC": Decimal(10_000),
        "WETH": Decimal(1),
    },
    name="MAvg_Agent",
)
lp_agent = UniV3PoolWealthAgent(
    initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
    name="LP_Agent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[mavg_agent, lp_agent],
    pools=pools,
    backend_type="forked",  # change to local for better speed
    market_impact="replay",
)

# Policies
mavg_policy = MovingAveragePolicy(agent=mavg_agent, short_window=25, long_window=100)

passive_lp_policy = PassiveConcentratedLP(
    agent=lp_agent, lower_price_bound=0.95, upper_price_bound=1.05
)

# SNIPPET 1 START
sim_blocks, sim_rewards = backtest_run(
    env, [mavg_policy, passive_lp_policy], dashboard_port=8051, auto_close=True
)
# SNIPPET 1 END
