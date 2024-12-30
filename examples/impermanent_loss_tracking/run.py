"""Run backtest for impermanent loss tracking."""
from decimal import Decimal
from typing import Any, Optional

from policy import ImpermanentLossPolicy

from dojo.agents import UniswapV3Agent
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.market_agents.uniswapV3 import HistoricReplayAgent
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
        self,
        initial_portfolio: dict[str, Decimal],
        unit_token: str,
        policy: Any,
        name: Optional[str] = None,
    ):  # noqa: D107
        super().__init__(
            name=name,
            unit_token=unit_token,
            initial_portfolio=initial_portfolio,
            policy=policy,
        )
        self.hold_portfolio: dict[str, Decimal] = {}

    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        """Impermanent loss of the agent denoted in the y asset of the pool."""
        token_ids = self.get_liquidity_ownership_tokens()
        if not self.hold_portfolio:
            self.hold_portfolio = obs.lp_quantities(token_ids)
        hold_wealth = self._pool_wealth(
            obs=obs, portfolio=self.hold_portfolio, unit_token=self.unit_token
        )
        lp_wealth = self._pool_wealth(
            obs=obs, portfolio=obs.lp_portfolio(token_ids), unit_token=self.unit_token
        )
        if hold_wealth == 0:
            return 0.0
        return (lp_wealth - hold_wealth) / hold_wealth


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    num_sim_blocks: int = 3000,
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05"]

    chain = Chain.ETHEREUM
    start_time = "2024-12-06 13:00:00"
    block_range = (
        time_to_block(start_time, chain),
        time_to_block(start_time, chain) + num_sim_blocks,
    )

    # Agents
    market_agent = HistoricReplayAgent(
        chain=chain, pools=pools, block_range=block_range
    )
    impermanent_loss_agent = ImpermanentLossAgent(
        initial_portfolio={
            "USDC": Decimal(10_000),
            "WETH": Decimal(1),
        },
        unit_token="USDC",
        name="Impermanent_Loss_Agent",
        policy=ImpermanentLossPolicy(),
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=chain,
        block_range=block_range,
        agents=[market_agent, impermanent_loss_agent],
        pools=pools,
        backend_type="forked",
    )

    backtest_run(
        env=env,
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
        num_sim_blocks=600,
    )
