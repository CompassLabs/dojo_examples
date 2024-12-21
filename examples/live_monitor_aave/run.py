"""Run a strategy on AAVE."""
from typing import Any, Optional

from policy import AAVEv3Policy

# SNIPPET 1 START
from dojo.agents.impersonation_agent import MonitoringAgent

# SNIPPET 1 END
from dojo.common.constants import Chain
from dojo.environments import AAVEv3Env
from dojo.environments.aaveV3 import AAVEv3Observation
from dojo.runners import monitor_run


# SNIPPET 2 START
class TrackHealthFactorAgent(MonitoringAgent):
    """An agent that displays health factor as its reward."""

    def __init__(
        self,
        impersonation_address: str,
        name: Optional[str] = None,
    ):
        """Initialize the agent."""
        super().__init__(
            name=name,
            impersonation_address=impersonation_address,
            unit_token="USDC",
            policy=AAVEv3Policy(),
        )

    # SNIPPET 2 END
    def reward(self, obs: AAVEv3Observation) -> float:
        """Tracks the health factor of the agent."""
        return obs.get_user_account_data_base(self.account.address).healthFactor  # type: ignore[union-attr]


def main(
    *,
    dashboard_server_port: Optional[int],
    simulation_status_bar: bool,
    auto_close: bool,
    num_sim_blocks: int = 20,
    **kwargs: dict[str, Any]
) -> None:
    """Running this strategy."""
    chain = Chain.ETHEREUM

    # SNIPPET 3 START
    agent1 = TrackHealthFactorAgent(
        impersonation_address="0x9c1d67674dE93b71ea16893C95dDA6f4D266a2bC",
        name="Alice",
    )
    # SNIPPET 3 END
    agent2 = TrackHealthFactorAgent(
        impersonation_address="0xE6ad0f991Ddc8630Cc03c972Fd5eA62DB8828525",
        name="Bob",
    )
    agent3 = TrackHealthFactorAgent(
        impersonation_address="0x23A5e45f9556Dc7ffB507DB8a3CFb2589bC8aDAD",
        name="Claire",
    )

    # SNIPPET 4 START
    env = AAVEv3Env(
        chain=chain,
        agents=[agent2, agent1, agent3],
        backend_type="live",  # `monitor_run` needs live backend
    )
    # SNIPPET 4 END

    # SNIPPET 5 START
    monitor_run(
        env,
        dashboard_server_port=dashboard_server_port,
        output_file="live_monitor_aave.db",
        auto_close=auto_close,
        stop_after_n_blocks=num_sim_blocks,
        simulation_title="Monitoring on AAVE",
        simulation_description="Monitoring on AAVE.",
    )
    # SNIPPET 5 END


if __name__ == "__main__":
    import dojo.config.logging_config

    dojo.config.logging_config.set_normal_logging_config_and_print_explanation()
    main(
        dashboard_server_port=8768,
        simulation_status_bar=True,
        auto_close=False,
        num_sim_blocks=10,
    )
