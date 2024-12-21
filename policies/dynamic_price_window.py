"""Dynamic price window policy."""
import logging

from dojo.agents import UniswapV3Agent

from .price_window import PriceWindowPolicy

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


# SNIPPET dynamic_price_window START
class DynamicPriceWindowPolicy(PriceWindowPolicy):
    """Policy for Dynamic Moving Average Price Window strategy."""

    # upper and lower limit are now parameters of the policy
    def __init__(
        self, agent: UniswapV3Agent, lower_limit: float, upper_limit: float
    ) -> None:  # noqa: D107
        super().__init__(lower_limit=lower_limit, upper_limit=upper_limit)
        self.old_price: float = 0.0
        self.spread: float = self.upper_limit - self.lower_limit
        self.center: float = (self.upper_limit + self.lower_limit) / 2
        self.returns: list[float] = []


# SNIPPET dynamic_price_window END
