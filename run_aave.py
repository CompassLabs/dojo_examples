import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from agents.aavev3_agent import AAVEv3Agent
from dateutil import parser as dateparser
from policies.aavev3_policy import AAVEv3Policy

from dojo.environments import AAVEv3Env
from dojo.runners import backtest_run


def main():
    # SNIPPET 1 START
    start_time = dateparser.parse("2023-03-11 00:00:00 UTC")
    end_time = dateparser.parse("2023-03-11 12:00:00 UTC")

    # Agents
    agent1 = AAVEv3Agent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(30000),
            "WBTC": Decimal(2),
        },
        name="AAVEAgent",
    )

    # Simulation environment (AAVE V3)
    env = AAVEv3Env(
        date_range=(start_time, end_time),
        agents=[agent1],
        backend_type="forked",
        market_impact="default",
    )

    env.reset()

    # Policies
    policy = AAVEv3Policy(agent=agent1)

    sim_blocks, sim_rewards = backtest_run(
        env, [policy], dashboard_port=8051, auto_close=True
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    main()
