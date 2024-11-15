"""Run backtest for impermanent loss tracking."""
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser
from policy import ImpermanentLossPolicy

from dojo.agents import UniswapV3Agent
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.observations import UniswapV3Observation
from dojo.runners import backtest_run


class ImpermanentLossAgent(UniswapV3Agent):
    """An agent that evaluates impermanent loss in a UniswapV3 pool.

    This agent calculates the difference in value between:
    1. Actively providing liquidity to a UniswapV3 pool
    2. Passively holding the same initial token quantities

    The reward function returns the relative impermanent loss/gain as a percentage,
    where negative values indicate losses and positive values indicate gains.

    Note:
        - Works with a single UniswapV3 pool
        - All tokens in the agent's portfolio must be part of the pool
        - Wealth calculations are denominated in the pool's second token (y asset).
    """

    def __init__(
        self, initial_portfolio: dict[str, Decimal], name: Optional[str] = None
    ):  # noqa: D107
        super().__init__(name=name, initial_portfolio=initial_portfolio)
        self.hold_portfolio: dict[str, Decimal] = {}

    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        """Impermanent loss of the agent denoted in the y asset of the pool."""
        token_ids = self.get_liquidity_ownership_tokens()
        if not self.hold_portfolio:
            self.hold_portfolio = obs.lp_quantities(token_ids)
        hold_wealth = self._pool_wealth(
            obs=obs, portfolio=self.hold_portfolio, unit_token="USDC"
        )
        lp_wealth = self._pool_wealth(
            obs=obs, portfolio=obs.lp_portfolio(token_ids), unit_token="USDC"
        )
        if hold_wealth == 0:
            return 0.0
        return (lp_wealth - hold_wealth) / hold_wealth


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=10),
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2021-06-21 00:00:00 UTC")
    end_time = start_time + run_length

    # Agents
    impermanent_loss_agent = ImpermanentLossAgent(
        initial_portfolio={
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        name="Impermanent_Loss_Agent",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[impermanent_loss_agent],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    liquidity_policy = ImpermanentLossPolicy(impermanent_loss_agent)

    backtest_run(
        env=env,
        policies=[liquidity_policy],
        simulation_status_bar=simulation_status_bar,
        dashboard_server_port=dashboard_server_port,
        output_file="impermanent_loss_tracking.db",
        auto_close=auto_close,
        simulation_title="Impermanent Loss Tracking",
        simulation_description="Comparing a passive LP agent to a HODL agent to measure Impermanent Loss.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
