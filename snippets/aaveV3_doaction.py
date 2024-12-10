"""Execute an action on AAVEv3."""
import os
import sys
from decimal import Decimal

from agents.dummy_agent import DummyAgent

from dojo.actions.aaveV3 import AAVEv3Supply, AAVEv3WithdrawAll
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments.aaveV3 import AAVEv3Env

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
chain = Chain.ETHEREUM
start_time = "2023-06-29 00:00:00"
end_time = "2023-06-29 00:05:00"

# SNIPPET 1 START
agent = DummyAgent(initial_portfolio={"USDC": Decimal(11_000)})
env = AAVEv3Env(
    chain=chain,
    block_range=(
        time_to_block(start_time, chain),
        time_to_block(end_time, chain),
    ),
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
