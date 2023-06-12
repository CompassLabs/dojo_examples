import logging
from argparse import ArgumentParser
from datetime import datetime
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

import pytz
from dateutil import parser as dateparser
from matplotlib import pyplot as plt

from demo.agents import UniV3PoolWealthAgent
from demo.policies import MovingAveragePolicy
from dojo.environments import UniV3Env
from dojo.vis import plotter


def run(pool: str, policy: str, start_time: datetime, end_time: datetime):
    demo_agent = UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})

    env = UniV3Env(
        date_range=(start_time, end_time),
        agents=[demo_agent],
        pools=[pool],
        market_impact="replay",
    )

    if policy.lower() == "moving-average":
        demo_policy = MovingAveragePolicy(
            agent=demo_agent, short_window=20, long_window=50
        )

    sim_blocks = []
    sim_rewards = []
    obs = env.reset()
    for block in env.iter_block():
        demo_actions = []
        market_actions = env.market_actions(agents_actions=demo_actions)
        actions = market_actions + demo_actions
        next_obs, rewards, dones, infos = env.step(actions=actions)
        if len(actions) > 0:
            plotter.send_data(block, "reward", rewards)
        plotter.send_data(
            block,
            "progress",
            int((block - env.start_block) * 100 / (env.end_block - env.start_block)),
        )
        obs = next_obs
        sim_blocks.append(block)
        sim_rewards.append(rewards[1])

    plt.plot(sim_blocks, sim_rewards)
    plt.show()


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Run a demo simulation with the UniswapV3 environment."
    )
    parser.add_argument(
        "--policy",
        "-p",
        type=str,
        default="moving-average",
        help="The policy to use for the demo, defaults to 'moving-average'.",
    )

    parser.add_argument(
        "--pool",
        "-pool",
        type=str,
        default="0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
        help="Pool address, defaults to WETH/USDC pool",
    )

    parser.add_argument(
        "--start_time",
        "-s",
        type=str,
        default="2023-04-29 10:00:00 UTC",
        help="start time",
    )

    parser.add_argument(
        "--end_time",
        "-e",
        type=str,
        default="2023-05-01 10:00:00 UTC",
        help="end time",
    )

    args = parser.parse_args()

    start_time = dateparser.parse(args.start_time)
    end_time = dateparser.parse(args.end_time)

    run(args.pool, args.policy, start_time, end_time)
