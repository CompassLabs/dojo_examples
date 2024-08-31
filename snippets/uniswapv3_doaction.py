import os
import sys
from decimal import Decimal

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


import numpy as np
from dateutil import parser as dateparser

from agents import UniswapV3PoolWealthAgent
from dojo.environments.uniswapV3 import UniswapV3Env, UniswapV3Trade

pools = ["USDC/WETH-0.3"]
sim_start = dateparser.parse("2021-06-21 00:00:00 UTC")
sim_end = dateparser.parse("2021-06-21 00:10:00 UTC")

agent = UniswapV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
env = UniswapV3Env(
    agents=[agent],  # Of course, you'd want an agent here to actually do things
    date_range=(sim_start, sim_end),
    pools=pools,
    backend_type="forked",
    market_impact="replay",  # defaults to "replay", simply replaying history
)

action = UniswapV3Trade(
    agent=agent,
    pool=env.obs.pools[0],
    quantities=(Decimal("0.1"), Decimal("0")),
)

env.step(actions=[action])
