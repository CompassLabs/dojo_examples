import logging
from decimal import Decimal

import matplotlib.pyplot as plt

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from dateutil import parser as dateparser

from demo.agents import UniV3PoolWealthAgent
from demo.policies import MovingAveragePolicy
from dojo.environments import UniV3Env
from dojo.runners import backtest_run

# SNIPPET 1 START
pool = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
start_time = dateparser.parse("2023-04-29 10:00:00 UTC")
end_time = dateparser.parse("2023-05-01 10:00:00 UTC")

demo_agent = UniV3PoolWealthAgent(
    initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)}
)

env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[demo_agent],
    pools=[pool],
    market_impact="replay",
)

demo_policy = MovingAveragePolicy(agent=demo_agent, short_window=200, long_window=1000)

sim_blocks, sim_rewards = backtest_run(env, [demo_policy])
plt.plot(sim_blocks, sim_rewards)
# SNIPPET 1 END
