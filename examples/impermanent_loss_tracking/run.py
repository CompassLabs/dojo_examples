import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import logging
import os
import sys
from decimal import Decimal

from agents.uniswapV3_impermanent_loss import ImpermanentLossAgent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from datetime import timedelta
from typing import Any, Optional

from dateutil import parser as dateparser
from policies.passiveLP import PassiveConcentratedLP

from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.runners import backtest_run

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    run_length: timedelta = timedelta(minutes=10),
    **kwargs: dict[str, Any],
) -> None:
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

    # Policies
    liquidity_policy = PassiveConcentratedLP(
        agent=impermanent_loss_agent,
        lower_price_bound=0.95,
        upper_price_bound=1.05,
    )

    backtest_run(
        env=env,
        policies=[liquidity_policy],
        simulation_status_bar=simulation_status_bar,
        dashboard_server_port=dashboard_server_port,
        output_file="impermanent_loss_tracking.db",
        auto_close=auto_close,
        simulation_title="Impermanent Loss Tracking",
        simulation_description="Comparing a passive LP agent to a HODL agent to measure IL.",
    )


if __name__ == "__main__":
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        run_length=timedelta(hours=2),
    )
