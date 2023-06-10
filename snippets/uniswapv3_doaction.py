from datetime import datetime
from decimal import Decimal

import numpy as np

from demo.agents import UniV3PoolWealthAgent
from dojo.environments.uniswapV3 import UniV3Action, UniV3Env

# USDC/WETH pool on UniswapV3
pools = ["0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"]  # WETH/USDC
sim_start = datetime(2023, 4, 29)
sim_end = datetime(2023, 4, 30)

agent=UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
env = UniV3Env(
    agents=[agent],  # Of course, you'd want an agent here to actually do things
    date_range=(sim_start, sim_end),
    pools=pools,
    market_impact="replay",  # defaults to "replay", simply replaying history
)
env.reset()

action = UniV3Action(
    agent=agent,
    type="quote",
    pool=env.obs.pools[0],
    quantities=np.array([Decimal(0.1), Decimal(1)]),
    tick_range=np.array([Decimal(0), Decimal(1)]),
)

env.step(actions=[action])
