"""Execute an action on Uniswap."""
import os
import sys
from decimal import Decimal

from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent

from dojo.actions.uniswapV3 import UniswapV3Trade
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments.uniswapV3 import UniswapV3Env

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

pools = ["USDC/WETH-0.3"]
sim_start = "2021-06-21 00:00:00"
sim_end = "2021-06-21 00:10:00"

agent = UniswapV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
chain = Chain.ETHEREUM
env = UniswapV3Env(
    agents=[agent],  # Of course, you'd want an agent here to actually do things
    chain=chain,
    block_range=(
        time_to_block(sim_start, chain),
        time_to_block(sim_end, chain),
    ),
    pools=pools,
    backend_type="forked",
)

action = UniswapV3Trade(
    agent=agent,
    pool=env.obs.pools[0],
    quantities=(Decimal("0.1"), Decimal("0")),
)

env.step(actions=[action])
