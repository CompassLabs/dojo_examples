import logging
import time
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from dateutil import parser as dateparser

from dojo.environments import UniV3Env
from dojo.runners import backtest_run

pool = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"


"""Testing that re-running market actions leads to the same state as forking at a
later time."""
start_time = dateparser.parse("2023-04-29 10:00:00 UTC")
end_time = dateparser.parse("2023-04-29 12:00:00 UTC")

# 5179794797478171634

env2 = UniV3Env(
    date_range=(end_time, end_time), agents=[], pools=[pool], market_impact="replay"
)
obs2 = env2.obs
env2_sqrt_priceX96, env2_tick, _, _, _, _, _ = obs2.slot0(pool)
env2_liquidity = obs2.liquidity(pool)


del env2
time.sleep(10)

env = UniV3Env(
    date_range=(start_time, end_time), agents=[], pools=[pool], market_impact="replay"
)
initial_sqrt_priceX96, initial_tick, _, _, _, _, _ = env.obs.slot0(pool)
initial_liquidity = env.obs.liquidity(pool)


backtest_run(env, [], port=8051)


obs = env.obs
sqrt_priceX96, tick, _, _, _, _, _ = obs.slot0(pool)
assert obs.liquidity(pool) == env2_liquidity, "Pool liquidities are not equal."
assert tick == env2_tick, "Ticks are not equal."
assert sqrt_priceX96 == env2_sqrt_priceX96, "Sqrt prices are not equal."
