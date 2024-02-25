import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from policies.arbitrage import ArbitragePolicy

from dojo.environments import UniV3Env
from dojo.runners import backtest_run


def main():
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05", "USDC/WETH-0.3"]
    start_time = dateparser.parse("2023-06-21 09:00:00 UTC")
    end_time = dateparser.parse("2023-06-24 22:00:00 UTC")

    # Agents
    agent1 = UniV3PoolWealthAgent(
        initial_portfolio={
            "ETH": Decimal(100),
            "USDC": Decimal(10000),
            "WETH": Decimal(0),
        },
        name="ArbitrageAgent",
    )

    # Simulation environment (Uniswap V3)
    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[agent1],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    # Policies
    arb_policy = ArbitragePolicy(agent=agent1)

    _, _ = backtest_run(env, [arb_policy], dashboard_port=8051, auto_close=True)
    # SNIPPET 1 END


if __name__ == "__main__":
    main()
