from decimal import Decimal
from typing import Any, List, Tuple

from dojo.actions.base_action import BaseAction
from dojo.actions.uniswapV3 import UniswapV3Quote
from dojo.agents import BaseAgent
from dojo.observations import uniswapV3
from dojo.observations.uniswapV3 import UniswapV3Observation
from dojo.policies import BasePolicy


# SNIPPET 1 START
class ImpermanentLossPolicy(BasePolicy):  # type: ignore
    def __init__(self, agent: BaseAgent) -> None:
        super().__init__(agent=agent)
        self.has_provided_liquidity = False
        self.has_executed_lp_action = False
        self.initial_lp_positions: dict[str, Decimal] = {}

    # SNIPPET 1 END

    def calculate_initial_signal(
        self, obs: UniswapV3Observation
    ) -> Tuple[Decimal, Decimal]:
        """Calculate initial signal based on the portfolio's token holdings."""
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)

        token0_amount = self.agent.initial_portfolio[token0]
        token1_amount = self.agent.initial_portfolio[token1] * obs.price(
            token1, token0, pool
        )

        if token1_amount <= token0_amount:
            return (token1_amount, self.agent.initial_portfolio[token1])
        return (token0_amount, token0_amount * obs.price(token0, token1, pool))

    # SNIPPET 3 START
    def compute_signals(self, obs: UniswapV3Observation) -> None:
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        token_ids = self.agent.get_liquidity_ownership_tokens()

        current_portfolio = obs.lp_portfolio(token_ids)
        current_quantities = obs.lp_quantities(token_ids)

        if current_portfolio == {}:
            token0_amount, token1_amount = self.calculate_initial_signal(obs)
            current_portfolio.update({token0: token0_amount, token1: token1_amount})
            current_quantities.update({token0: token0_amount, token1: token1_amount})
            self.initial_lp_positions.update(
                {token0: token0_amount, token1: token1_amount}
            )
        elif not self.has_provided_liquidity:
            self.has_provided_liquidity = True
            self.initial_lp_positions.update(
                {token0: current_quantities[token0], token1: current_quantities[token1]}
            )

        value_if_held0 = self.initial_lp_positions[token0] + self.initial_lp_positions[
            token1
        ] * obs.price(token1, token0, pool)
        value_if_held1 = (
            self.initial_lp_positions[token0] * obs.price(token0, token1, pool)
            + self.initial_lp_positions[token1]
        )

        current_wealth0 = current_portfolio[token0] + current_portfolio[
            token1
        ] * obs.price(token1, token0, pool)
        current_wealth1 = current_portfolio[token1] + current_portfolio[
            token0
        ] * obs.price(token0, token1, pool)

        obs.add_signal("Hodl Value in Token0", value_if_held0)
        obs.add_signal("Hodl Value in Token1", value_if_held1)
        obs.add_signal("Current Token0 Value", current_quantities[token0])
        obs.add_signal("Current Token1 Value", current_quantities[token1])
        obs.add_signal("Current Token0 Value With Fees", current_wealth0)
        obs.add_signal("Current Token1 Value With Fees", current_wealth1)
        obs.add_signal("Token0 Impermanent Loss", current_wealth0 - value_if_held0)
        obs.add_signal("Token1 Impermanent Loss", current_wealth1 - value_if_held1)

    # SNIPPET 3 END

    def predict(self, obs: UniswapV3Observation) -> List[BaseAction[Any]]:
        pool = obs.pools[0]
        token0, token1 = obs.pool_tokens(pool)
        action = None

        # SNIPPET 2 START
        if not self.has_executed_lp_action:
            self.has_executed_lp_action = True
            portfolio = self.agent.portfolio()
            spot_price = obs.price(token0, token1, pool)

            decimals0 = obs.token_decimals(token0)
            decimals1 = obs.token_decimals(token1)

            lower_price_range = Decimal(0.95) * spot_price
            upper_price_range = Decimal(1.05) * spot_price
            tick_spacing = obs.tick_spacing(pool)

            lower_tick = uniswapV3.price_to_active_tick(
                lower_price_range, tick_spacing, (decimals0, decimals1)
            )
            upper_tick = uniswapV3.price_to_active_tick(
                upper_price_range, tick_spacing, (decimals0, decimals1)
            )
            action = UniswapV3Quote(
                agent=self.agent,
                pool=pool,
                quantities=(portfolio[token0], portfolio[token1]),
                tick_range=(lower_tick, upper_tick),
            )
        # SNIPPET 2 END

        self.compute_signals(obs)
        return [action] if action else []
