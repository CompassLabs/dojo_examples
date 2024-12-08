"""Run uniswap RSI strategy on arbitrum."""
import logging
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser
from policy import RSIPolicy

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common.constants import Chain

# SNIPPET 1 START
from dojo.environments import UniswapV3Env

# SNIPPET 1 END
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=1),
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    pools = ["WETH/USDC-0.05"]
    start_time = dateparser.parse("2024-05-01 09:08:00 UTC")
    end_time = start_time + run_length

    # Agents
    rsi_agent = TotalWealthAgent(
        initial_portfolio={
            "USDC": Decimal(10000),
            "ETH": Decimal(10),
            "WETH": Decimal(100),
        },
        name="RSI_Agent_Arbitrum",
        unit_token="USDC",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ARBITRUM,
        date_range=(start_time, end_time),
        agents=[rsi_agent],
        pools=pools,
        backend_type="forked",
        market_impact="replay",
    )

    # Policies
    rsi_policy = RSIPolicy(
        agent=rsi_agent,
    )

    backtest_run(
        env=env,
        policies=[rsi_policy],
        dashboard_server_port=dashboard_server_port,
        output_file="rsi_arbitrum.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="RSI",
        simulation_description="Investing accoring the the Relative Strenght Indicator (RSI) index.",
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
