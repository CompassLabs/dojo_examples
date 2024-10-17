import os
import sys
from decimal import Decimal

from dojo.common.constants import Chain

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from agents.dummy_agent import DummyAgent
from dateutil import parser as dateparser

from dojo.actions.aaveV3 import AAVEv3Supply, AAVEv3WithdrawAll
from dojo.environments.aaveV3 import AAVEv3Env

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

start_time = dateparser.parse("2023-06-29 00:00:00 UTC")
end_time = dateparser.parse("2023-06-29 00:05:00 UTC")

# SNIPPET 1 START
agent = DummyAgent(initial_portfolio={"USDC": Decimal(11_000)})
env = AAVEv3Env(
    chain=Chain.ETHEREUM,
    date_range=(start_time, end_time),
    agents=[agent],
    backend_type="forked",
    market_impact="default",
)

actions = [
    AAVEv3Supply(
        agent=agent,
        token="USDC",
        amount=Decimal(10_000),
    ),
    AAVEv3WithdrawAll(agent=agent, token="USDC"),
]

for action in actions:
    env.step(actions=[action])
# SNIPPET 1 END
