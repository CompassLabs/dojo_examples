"""Run two agents.

One active one passive.
"""
from typing import Any, Optional

from dojo.agents.impersonation_agent import MonitoringAgent
from dojo.agents.uniswapV3 import UniswapV3Agent
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env
from dojo.observations import UniswapV3Observation
from dojo.policies import DoNothingPolicy
from dojo.runners import monitor_run


class TrackPositionsAgent(MonitoringAgent, UniswapV3Agent):
    """An agent that displays health factor as its reward."""

    def __init__(
        self,
        impersonation_address: str,
        token_ids: list[int],
        name: Optional[str] = None,
    ):
        """Initialize the agent."""
        super().__init__(
            name=name,
            impersonation_address=impersonation_address,
            unit_token="USDC",
            policy=DoNothingPolicy(),
        )
        for token_id in token_ids:
            self.add_nft(token="UNI-V3-POS", token_id=token_id)

    def reward(self, obs: UniswapV3Observation) -> float:  # type: ignore
        """Tracks the health factor of the agent."""
        return self.total_wealth(obs=obs, unit_token=self.unit_token)


def main(
    *,
    dashboard_server_port: Optional[int] = 8768,
    simulation_status_bar: bool = False,
    auto_close: bool,
    num_sim_blocks: int = 20,
    **kwargs: dict[str, Any],
) -> None:
    """Running this strategy."""
    pools = ["USDC/WETH-0.05", "USDC/WETH-0.3"]
    chain = Chain.ETHEREUM

    alice = TrackPositionsAgent(
        impersonation_address="0x70168a7a647fcDFfbB06f4539208A5470CfC7ceb",
        token_ids=[676835],
        name="Alice",
    )
    bob = TrackPositionsAgent(
        impersonation_address="0x0156a98F1b82045C10cab22A0640F808fE21beea",
        token_ids=[776800],
        name="Bob",
    )

    # Simulation environment (Uniswap V3)
    env = UniswapV3Env(
        chain=chain,
        agents=[alice, bob],
        block_range=(0, 0),
        pools=pools,
        backend_type="live",
    )

    monitor_run(
        env,
        dashboard_server_port=dashboard_server_port,
        output_file="live_monitor_uniswap.db",
        auto_close=auto_close,
        stop_after_n_blocks=num_sim_blocks,
        simulation_title="Monitoring on Uniswap",
        simulation_description="Monitoring on Uniswap.",
    )


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=True,
        num_sim_blocks=5,
    )
