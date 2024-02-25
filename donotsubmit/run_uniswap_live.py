import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.moving_average import MovingAveragePolicy
from policies.passiveLP import PassiveConcentratedLP

from dojo.environments import UniV3Env
from dojo.runners import live_run


def main():
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
    end_time = dateparser.parse("2021-06-21 12:00:00 UTC")

    # Agents
    agent1 = UniV3PoolWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="TraderAgent",
    )

    # Simulation environment (Uniswap V3)
    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent1],
        pools=pools,
        backend_type="live",
        market_impact="no_market",
    )

    # Policies
    mvag_policy = MovingAveragePolicy(agent=agent1, short_window=25, long_window=100)

    sim_blocks, sim_rewards = live_run(
        env, [mvag_policy], dashboard_port=8051, auto_close=True
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    main()
