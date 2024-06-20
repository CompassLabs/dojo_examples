import os
import sys
from decimal import Decimal

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


import numpy as np
from agents import UniV3PoolWealthAgent
from dateutil import parser as dateparser

from dojo.environments.uniswapV3 import UniV3Env, UniV3Trade

pools = ["USDC/WETH-0.3"]
sim_start = dateparser.parse("2023-04-29 00:00:00 UTC")
sim_end = dateparser.parse("2023-04-30 00:00:00 UTC")

agent = UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
env = UniV3Env(
    agents=[agent],  # Of course, you'd want an agent here to actually do things
    date_range=(sim_start, sim_end),
    pools=pools,
    market_impact="replay",  # defaults to "replay", simply replaying history
)
env.reset()

action = UniV3Trade(
    agent=agent,
    pool=env.obs.pools[0],
    quantities=(Decimal("0.1"), Decimal("0")),
)

env.step(actions=[action])
