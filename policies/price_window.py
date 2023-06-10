import logging
from datetime import datetime
from decimal import Decimal
from typing import List

logging.basicConfig(format="%(asctime)s - %(message)s", level=20)

from dojo.agents import BaseAgent
from dojo.environments.uniswapV3 import UniV3Action, UniV3Obs
from dojo.policies import BasePolicy

from demo.agents import UniV3PoolWealthAgent
from dojo.environments import UniV3Env

class PriceWindowPolicy(BasePolicy):
    def __init__(
        self, agent: BaseAgent, lower_limit: float, upper_limit: float
    ) -> None:
        super().__init__(agent=agent)
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    # derive actions from observations
    def predict(self, obs: UniV3Obs) -> List[UniV3Action]:
        pool = obs.pools[0]
        x_token, y_token = obs.pool_tokens(pool)
        spot_price = obs.get_price(token=x_token, unit=y_token, pool=pool)

        if spot_price > self.upper_limit:
            y_quantity = self.agent.quantity(y_token)
            action = UniV3Action(
                agent=self.agent,
                type="trade",
                pool=pool,
                quantities=(Decimal(0), y_quantity),
            )
            return [action]

        if spot_price < self.lower_limit:
            x_quantity = self.agent.quantity(x_token)
            action = self.env.make_action(
                event_type="trade", pool=self.pool, quantities=(x_quantity, Decimal(0))
            )
            return [action]

        return []


if __name__ == "__main__":

    demo_agent = UniV3PoolWealthAgent(initial_portfolio={"USDC": Decimal(10_000)})
    env = UniV3Env(
        date_range=(datetime(2023, 4, 29), datetime(2023, 5, 2)),
        agents=[demo_agent],
        pools=["0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"],
        market_impact="replay",
    )

    demo_policy = PriceWindowPolicy(agent=demo_agent, lower_limit=0.9, upper_limit=1.1)

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
