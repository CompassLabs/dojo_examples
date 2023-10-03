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
    pool = "USDC/WETH-0.05"
    start_time = dateparser.parse("2021-05-29 10:00:00 UTC")
    end_time = dateparser.parse("2021-05-30 16:00:00 UTC")

    # Agents
    agent1 = UniV3PoolWealthAgent(
        initial_portfolio={
            "ETH": Decimal(900),
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="moving_average_agent",
    )
    agent2 = UniV3PoolWealthAgent(
        initial_portfolio={"USDC": Decimal(10_000), "WETH": Decimal(1)},
        name="passive LP agent",
    )

    # Simulation environment ( Uniswap V3)
    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent1, agent2],
        pools=[pool],
        backend_type="local",
        market_impact="replay",
    )

    env.reset()
    agent1.portfolio()

    # Policies
    mvag_policy = MovingAveragePolicy(agent=agent1, short_window=50, long_window=200)
    passive_lp_policy = PassiveConcentratedLP(
        agent=agent2, lower_price_bound=0.95, upper_price_bound=1.05
    )

    _, _ = backtest_run(env, [mvag_policy, passive_lp_policy], port=8051)
    # SNIPPET 1 END


if __name__ == "__main__":
    main()
