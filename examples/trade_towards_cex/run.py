"""Run strategy against binance data."""

from decimal import Decimal
from typing import Any, Optional

from binance_data import load_binance_data
from policy import TradeTowardsCentralisedExchangePolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common import time_to_block
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run


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
    year = 2021
    month = 6
    start_day = 1
    start_time = f"{year}-{month:02}-{start_day:02} 00:00:00"
    chain = Chain.ETHEREUM

    # Agents
    cex_directional_agent = TotalWealthAgent(
        initial_portfolio={
            "ETH": Decimal(10),
            "USDC": Decimal(1_000),
            "WETH": Decimal(1),
        },
        name="CEX Directional Agent",
        unit_token="USDC",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=chain,
        block_range=(
            time_to_block(start_time, chain),
            time_to_block(start_time, chain) + num_sim_blocks,
        ),
        agents=[cex_directional_agent],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    # SNIPPET 1 START
    binance_data = load_binance_data(year, month)

    # Policies
    arb_policy = TradeTowardsCentralisedExchangePolicy(
        agent=cex_directional_agent, binance_data=binance_data
    )
    # SNIPPET 1 END

    backtest_run(
        env=env,
        policies=[arb_policy],
        dashboard_server_port=dashboard_server_port,
        output_file="trade_towards_cex.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Trading with external signals",
        simulation_description="We make trading desicions on Uniswap based on the token price on Binance.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=3000,
    )
