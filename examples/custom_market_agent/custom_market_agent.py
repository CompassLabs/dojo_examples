from decimal import Decimal
from typing import Any, Literal

from dojo.actions import UniswapV3ProvideQuantities
from dojo.actions.uniswapV3 import (
    UniswapV3Action,
    UniswapV3Trade,
    UniswapV3WithdrawLiquidity,
)
from dojo.agents import BaseAgent
from dojo.common.constants import Chain
from dojo.config import deployments as deploy_cfg
from dojo.dataloaders import UniswapV3Loader
from dojo.dataloaders.base_uniswapV3_loader import BaseUniswapV3Loader
from dojo.market_agents.uniswapV3 import BaseMarketPolicy
from dojo.observations.uniswapV3 import UniswapV3Observation


class CustomMarketPolicy(BaseMarketPolicy):
    """Custom market policy for UniwapV3."""

    DEFAULT_GAS = 30_500_000

    def __init__(
        self,
        chain: Chain,
        pools: list[str],
        block_range: tuple[int, int],
        dataloader: BaseUniswapV3Loader,
        mode: Literal["standard", "swaps_only"] = "standard",
    ):
        """Initialize the policy.

        :param chain: Agent is for a specific chain.
        :param pools: List of pools that this agent should be active on.
        :param mode: In standard mode, all events are replayed. In swaps_only mode, only
            swaps are replayed.
        :param block_range: Range of blocks to replay.
        """
        super().__init__(
            chain=chain,
            pools=pools,
            block_range=block_range,
            dataloader=dataloader,
            mode=mode,
        )
        self.last_position = None

    def predict(self, obs: UniswapV3Observation) -> list[UniswapV3Action]:
        """Random market policy."""
        block: int = obs.block
        active_tick_range = obs.active_tick_range(pool=self.pools[0])

        if block % 10 == 0:
            return [
                UniswapV3Trade(
                    agent=self.agent,
                    pool=self.pools[0],
                    quantities=(Decimal("10000"), Decimal("0")),
                )
            ]
        if block % 12 == 0 and self.last_position is not None:
            self.last_position = None
            last_position_id = self.agent.erc721_portfolio()["UNI-V3-POS"][-1]
            return [
                UniswapV3WithdrawLiquidity(
                    agent=self.agent,
                    position_id=last_position_id,
                    liquidity=obs.nft_position_info(last_position_id)["liquidity"],
                ),
            ]
        if block % 11 == 0:
            self.last_position = active_tick_range
            return [
                UniswapV3ProvideQuantities(
                    agent=self.agent,
                    pool=self.pools[0],
                    tick_range=active_tick_range,
                    amount0=Decimal(1000),
                    amount1=Decimal(1),
                    auto_trade=False,
                )
            ]
        return []


class CustomMarketAgent(BaseAgent[UniswapV3Observation]):
    """Custom market agent."""

    def __init__(
        self,
        chain: Chain,
        pools: list[str],
        block_range: tuple[int, int],
        mode: Literal["standard", "swaps_only"] = "standard",
        name: str = "MarketAgent",
        Dataloader: type[BaseUniswapV3Loader] = UniswapV3Loader,
    ):
        """Initialize the policy.

        :param chain: Agent is for a specific chain.
        :param pools: List of pools that the agent should be active on.
        :param mode: In standard mode, all events are replayed. In swaps_only mode, only
            swaps are replayed
        :param block_range: Range of blocks to replay.
        """
        initial_portfolio = {
            **{
                token: Decimal(-1)
                for token in deploy_cfg.get_erc20_tokens_per_chain(
                    chain=chain, start_block=block_range[0]
                )
            },
            **{"ETH": Decimal(1000)},
        }

        dataloader = Dataloader()

        policy = CustomMarketPolicy(
            chain=chain,
            pools=pools,
            block_range=block_range,
            mode=mode,
            dataloader=dataloader,
        )

        super().__init__(
            initial_portfolio, name=name, policy=policy, write_results=False
        )

    def reward(self, obs: Any) -> float:
        """Reward is not relevant for the market agent."""
        return 0.0
