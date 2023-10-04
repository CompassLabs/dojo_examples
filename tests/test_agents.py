import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)


import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from dateutil import parser as dateparser

from dojo.agents import BaseAgent
from dojo.environments import UniV3Env
from dojo.runners import backtest_run

from ..agents.univ3_impermanent_loss import ImpermanentLossAgent
from ..agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from ..policies.moving_average import MovingAveragePolicy


def run_agent(agent: BaseAgent):
    pool = "USDC/WETH-0.3"
    start_time = dateparser.parse("2021-05-29 10:00:00 UTC")
    end_time = dateparser.parse("2021-05-29 12:00:00 UTC")

    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent],
        pools=[pool],
        market_impact="replay",
    )
    demo_policy = MovingAveragePolicy(agent=agent, short_window=200, long_window=1000)
    backtest_run(env, [demo_policy])


def test_impermanent_loss():
    agent = ImpermanentLossAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)}
    )

    run_agent(agent)


def test_univ3_pool_wealth():
    agent = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)}
    )
    run_agent(agent)
