import logging
from datetime import datetime
from decimal import Decimal
from typing import List

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from price_window import PriceWindowPolicy

from demo.agents import UniV3PoolWealthAgent
from dojo.agents import BaseAgent
from dojo.environments import UniV3Env
from dojo.environments.uniswapV3 import UniV3Obs


# SNIPPET dynamic_price_window START
class DynamicPriceWindowPolicy(PriceWindowPolicy):

    # upper and lower limit are now parameters of the policy
    def __init__(
        self, agent: BaseAgent, lower_limit: float, upper_limit: float
    ) -> None:
        super().__init__(agent=agent, lower_limit=lower_limit, upper_limit=upper_limit)
        self.old_price = 0
        self.spread = self.upper_limit - self.lower_limit
        self.center = (self.upper_limit + self.lower_limit) / 2
        self.returns = []

    def fit(self, obs: UniV3Obs) -> None:
        pool = obs.pools[0]
        x_token, y_token = obs.pool_tokens(pool)
        spot_price = obs.get_price(token=x_token, unit=y_token, pool=pool)
        if len(self.returns) == 0:
            self.old_price = spot_price

        new_return = spot_price / old_price
        returns.append(new_return)
        vol = np.std(self.returns)
        self.vols.append(vol)
        vol_diff = vol / np.mean(self.vols)
        self.spread = self.spread * vol_diff
        self.lower_limit = max(0, self.center - (self.spread / 2))
        self.upper_limit = self.center + (self.spread / 2)


# SNIPPET dynamic_price_window END


if __name__ == "__main__":

    demo_agent = UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
    env = UniV3Env(
        date_range=(datetime(2023, 4, 29), datetime(2023, 5, 2)),
        agents=[demo_agent],
        pools=["0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"],
        market_impact="replay",
    )

    demo_policy = DynamicPriceWindowPolicy(
        agent=demo_agent, lower_limit=0.9, upper_limit=1.1
    )

    sim_blocks = []
    sim_rewards = []
    obs = env.reset()
    for block in env.iter_block():
        demo_actions = []
        market_actions = env.market_actions(agents_actions=demo_actions)
        actions = market_actions + demo_actions
        next_obs, rewards, dones, infos = env.step(actions=actions)
        obs = next_obs
        sim_blocks.append(block)
        sim_rewards.append(rewards[1])
