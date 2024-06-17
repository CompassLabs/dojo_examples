import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.moving_average import MovingAveragePolicy
from policies.passiveLP import PassiveConcentratedLP

from dojo.environments import UniV3Env
from dojo.runners import backtest_run


def main():
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-22 00:00:00 UTC")
    end_time = dateparser.parse("2021-06-22 12:00:00 UTC")

    # Agents
    agent1 = UniV3PoolWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="TraderAgent",
    )
    agent2 = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="LPAgent",
    )

    # Simulation environment (Uniswap V3)
    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent1, agent2],
        pools=pools,
        backend_type="local",
        market_impact="replay",
    )

    # Policies
    mvag_policy = MovingAveragePolicy(agent=agent1, short_window=25, long_window=100)

    passive_lp_policy = PassiveConcentratedLP(
        agent=agent2, lower_price_bound=0.95, upper_price_bound=1.05
    )

    sim_blocks, sim_rewards = backtest_run(
        env, [mvag_policy, passive_lp_policy], dashboard_port=8051, auto_close=True
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    main()
