"""Implementation of a custom dataloader."""
import json
from collections import defaultdict
from typing import DefaultDict, Literal, Optional

from dojo.common.constants import Chain
from dojo.dataloaders.base_uniswapV3_loader import BaseUniswapV3Loader
from dojo.dataloaders.formats import (  # UniswapV3Collect,; UniswapV3Initialize,
    UniswapV3Burn,
    UniswapV3Event,
    UniswapV3Mint,
    UniswapV3Swap,
)


class CustomDataLoader(BaseUniswapV3Loader):
    """Load historic data yourself."""

    def __init__(self) -> None:
        """Set up your custom dataloader here.

        :raises ValueError: When the data cannot be loaded.
        """
        self.events: DefaultDict[int, list[UniswapV3Event]] = defaultdict(list)
        with open("amberdata.json", "r") as f:
            for event in json.load(f):
                block = event["blockNumber"]
                match event["action"]:
                    case "Mint":
                        self.events[block].append(
                            UniswapV3Mint(
                                quantities=[event["amount0"], event["amount1"]],
                                tick_range=[event["tickLower"], event["tickUpper"]],
                                liquidity=0,
                                owner=event["owner"],
                                date=event["timestamp"],
                                block=event["blockNumber"],
                                log_index=event["logIndex"],
                                action=event["action"],
                                pool=event["poolAddress"].lower(),
                                gas=0,
                                gas_price=0,
                            )
                        )
                    case "Burn":
                        self.events[block].append(
                            UniswapV3Burn(
                                quantities=[event["amount0"], event["amount1"]],
                                tick_range=[event["tickLower"], event["tickUpper"]],
                                liquidity=0,
                                owner=event["owner"],
                                date=event["timestamp"],
                                block=event["blockNumber"],
                                log_index=event["logIndex"],
                                action=event["action"],
                                pool=event["poolAddress"].lower(),
                                gas=0,
                                gas_price=0,
                            )
                        )
                    case "Swap":
                        self.events[block].append(
                            UniswapV3Swap(
                                quantities=[event["amount0"], event["amount1"]],
                                sqrt_price_limit_x96=2**256 - 1,
                                date=event["timestamp"],
                                block=event["blockNumber"],
                                log_index=event["logIndex"],
                                action=event["action"],
                                pool=event["poolAddress"].lower(),
                                gas=0,
                                gas_price=0,
                            )
                        )
                    case "Collect":
                        # TODO needs to be implemented
                        pass
                    case "Initialize":
                        # TODO needs to be implemented
                        pass
                    case _:
                        raise ValueError(f"Unknown event type: {event['action']}")

    def _load_data(self, chain: Chain, pool_addresses: list[str], from_block: int, to_block: int, subset: Optional[list[Literal["Burn", "Mint", "Swap"]]] = None) -> list[UniswapV3Event]:  # type: ignore[override]
        relevant_events: list[UniswapV3Event] = []
        for block_number in range(from_block, to_block + 1):
            # if subset:
            #     pass
            relevant_events += list(
                filter(
                    lambda event: event["action"] in subset, self.events[block_number]  # type: ignore
                )
            )

        return relevant_events
