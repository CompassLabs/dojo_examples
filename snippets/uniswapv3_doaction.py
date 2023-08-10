import os
import sys
from decimal import Decimal

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


import numpy as np
from agents import UniV3PoolWealthAgent
from dateutil import parser as dateparser

from dojo.environments.uniswapV3 import UniV3Action, UniV3Env

# USDC/WETH pool on UniswapV3
pools = ["0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"]  # WETH/USDC
sim_start = dateparser.parse("2023-04-29 00:00:00 UTC")
sim_end = dateparser.parse("2023-04-30 00:00:00 UTC")

agent = UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
env = UniV3Env(
    agents=[agent],  # Of course, you'd want an agent here to actually do things
    date_range=(sim_start, sim_end),
    pools=pools,
    market_impact="replay",  # defaults to "replay", simply replaying history
)

action = UniV3Action(
    agent=agent,
    type="trade",
    pool=env.obs.pools[0],
    quantities=np.array([Decimal("0.1"), Decimal("0")]),
)

env.step(actions=[action])
