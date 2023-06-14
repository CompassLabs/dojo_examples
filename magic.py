import logging
from argparse import ArgumentParser
from datetime import datetime
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

import pytz
from dateutil import parser as dateparser
from matplotlib import pyplot as plt

from demo.agents import UniV3PoolWealthAgent
from demo.policies import MovingAveragePolicy
from dojo.environments import UniV3Env
from dojo.vis import plotter

# SNIPPET 1 START
# def run(pool: str, policy: str, start_time: datetime, end_time: datetime):

start_time = dateparser.parse("2023-04-29 10:00:00 UTC")
end_time = dateparser.parse("2023-04-29 16:00:00 UTC")
pool = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"


demo_agent = UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})

env2 = UniV3Env(
    date_range=(end_time, end_time),
    agents=[demo_agent],
    pools=[pool],
    market_impact="replay",
)
env2.reset()
env2_liquidity = env2.obs.liquidity(pool)

env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[demo_agent],
    pools=[pool],
    market_impact="replay",
)


demo_policy = MovingAveragePolicy(agent=demo_agent, short_window=20, long_window=50)

obs = env.reset()
for block in env.iter_block():
    agent_actions = []
    market_actions = env.market_actions(agents_actions=agent_actions)
    actions = market_actions + agent_actions
    next_obs, rewards, dones, infos = env.step(actions=actions)
    obs = next_obs

# print("test")
assert (
    env.obs.liquidity(pool) == env2_liquidity
), f"Liquidities are not equal: {env.obs.liquidity(pool)} != {env2_liquidity}"
# print(env.obs.pool_quantities(pool,1))


# sqrtPriceX96	uint160	The current price of the pool as a sqrt(token1/token0) Q64.96 value
# tick	int24	The current tick of the pool, i.e. according to the last tick transition that was run. This value may not always be equal to SqrtTickMath getTickAtSqrtRatio(sqrtPriceX96) if the price is on a tick boundary.
# observationIndex	uint16	The index of the last oracle observation that was written,
# observationCardinality	uint16	The current maximum number of observations stored in the pool,
# observationCardinalityNext	uint16	The next maximum number of observations, to be updated when the observation.
# feeProtocol	uint8	The protocol fee for both tokens of the pool. Encoded as two 4 bit values, where the protocol fee of token1 is shifted 4 bits and the protocol fee of token0is the lower 4 bits.Used as the denominator of a fraction of the swap fee, e.g. 4 means 1/4th of the swap fee.
# unlocked	bool	Whether the pool is currently locked to reentrancy

sqrtPriceX96, tick, _, _, _, _, _ = env.obs.slot0(pool)
