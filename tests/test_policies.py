import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)


import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser

from dojo.agents import BaseAgent
from dojo.environments import UniV3Env
from dojo.policies import BasePolicy
from dojo.runners import backtest_run

from ..policies.dynamic_price_window import DynamicPriceWindowPolicy
from ..policies.moving_average import MovingAveragePolicy
from ..policies.passiveLP import PassiveConcentratedLP
from ..policies.price_window import PriceWindowPolicy


def run_policy(agent: BaseAgent, policy: BasePolicy):
    pool = "USDC/WETH-0.3"
    start_time = dateparser.parse("2023-04-29 10:00:00 UTC")
    end_time = dateparser.parse("2023-04-29 12:00:00 UTC")

    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent],
        pools=[pool],
        market_impact="replay",
    )
    backtest_run(env, [policy], port=8051)


def test_price_window():
    agent = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(1000), "WETH": Decimal(1)}
    )
    policy = PriceWindowPolicy(agent=agent, lower_limit=0.9, upper_limit=1.1)
    run_policy(agent, policy)


def test_passive_concentrated_lp():
    agent = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(1000), "WETH": Decimal(1)}
    )
    policy = PassiveConcentratedLP(
        agent=agent, lower_price_bound=0.95, upper_price_bound=1.05
    )
    run_policy(agent, policy)


def test_moving_average():
    agent = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(1000), "WETH": Decimal(1)}
    )
    policy = MovingAveragePolicy(agent=agent, short_window=200, long_window=500)
    run_policy(agent, policy)


def test_dynamic_price_window():
    agent = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(1000), "WETH": Decimal(1)}
    )
    policy = DynamicPriceWindowPolicy(agent=agent, lower_limit=0.9, upper_limit=1.1)
    run_policy(agent, policy)
