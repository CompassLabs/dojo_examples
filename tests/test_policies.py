import logging
from decimal import Decimal

from brownie import network

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)


import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.dynamic_price_window import DynamicPriceWindowPolicy
from policies.moving_average import MovingAveragePolicy
from policies.passiveLP import PassiveConcentratedLPPolicy
from policies.price_window import PriceWindowPolicy

from dojo.agents import BaseAgent
from dojo.environments import UniV3Env
from dojo.policies import BasePolicy
from dojo.runners import backtest_run


def run_policy(agent: BaseAgent, policy: BasePolicy):
    pool = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
    start_time = dateparser.parse("2023-04-29 10:00:00 UTC")
    end_time = dateparser.parse("2023-04-29 14:00:00 UTC")

    if network.is_connected():
        network.disconnect(kill_rpc=True)

    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent],
        pools=[pool],
        market_impact="replay",
    )
    backtest_run(env, [policy], port=8051)


def test_demo_policies():
    agent = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(1000), "WETH": Decimal(1)}
    )
    policies = [
        PriceWindowPolicy(agent=agent, lower_limit=0.9, upper_limit=1.1),
        PassiveConcentratedLPPolicy(
            agent=agent, lower_tick_bound=20000, upper_tick_bound=30000
        ),
        MovingAveragePolicy(agent=agent, short_window=200, long_window=500),
        DynamicPriceWindowPolicy(agent=agent, lower_limit=0.9, upper_limit=1.1),
    ]

    for policy in policies:
        print(policy)
        run_policy(agent, policy)