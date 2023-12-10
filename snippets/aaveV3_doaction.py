import os
import sys
from decimal import Decimal

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from agents import AAVEv3Agent
from dateutil import parser as dateparser

from dojo.actions.aaveV3 import (
    AAVEv3BorrowToHealthFactor,
    AAVEv3RepayAll,
    AAVEv3Supply,
    AAVEv3WithdrawAll,
)
from dojo.environments.aaveV3 import AAVEv3Env

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

start_time = dateparser.parse("2023-06-29 00:00:00 UTC")
end_time = dateparser.parse("2023-06-29 12:30:00 UTC")

# SNIPPET 1 START
agent = AAVEv3Agent(initial_portfolio={"USDC": Decimal(11_000)})
env = AAVEv3Env(
    date_range=(start_time, end_time),
    agents=[agent],
    backend_type="forked",
    market_impact="default",
)

actions = [
    AAVEv3Supply(
        agent=agent,
        token_name="USDC",
        amount=Decimal(10_000),
    ),
    AAVEv3BorrowToHealthFactor(
        agent=agent, token_name="WETH", factor=2.0, mode="variable"
    ),
    AAVEv3RepayAll(
        agent=agent,
        token_name="WETH",
        mode="variable",
    ),
    AAVEv3WithdrawAll(agent=agent, token_name="WETH"),
]

for action in actions:
    env.step(actions=[action])
# SNIPPET 1 END
