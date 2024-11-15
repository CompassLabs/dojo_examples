"""Run the active LP strategy."""
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional

from dateutil import parser as dateparser
from policy import ActiveConcentratedLP

from dojo.agents.uniswapV3 import TotalWealthAgent
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(days=1),
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    # SNIPPET 1 START
    pools = ["USDC/WETH-0.05"]
    start_time = dateparser.parse("2023-05-01 00:00:00 UTC")
    end_time = start_time + run_length

    agent2 = TotalWealthAgent(
        initial_portfolio={
            "USDC": Decimal(1_000_000),
            "WETH": Decimal(2_000),
            "ETH": Decimal(10),
        },
        name="LPAgent",
        unit_token="USDC",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=Chain.ETHEREUM,
        date_range=(start_time, end_time),
        agents=[agent2],
        pools=pools,
        backend_type="local",
        market_impact="replay_trades_only",
    )

    active_lp_policy = ActiveConcentratedLP(agent=agent2, lp_width=2)

    backtest_run(
        env,
        [active_lp_policy],
        dashboard_server_port=dashboard_server_port,
        output_file="active_lp.db",
        auto_close=auto_close,
        simulation_status_bar=simulation_status_bar,
        simulation_title="Active liquidity provisioning",
        simulation_description="Keep liquidity in the active tick range.",
    )
    # SNIPPET 1 END


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
