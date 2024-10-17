# type: ignore
from decimal import Decimal
from enum import Enum

from dojo.actions.gmxV2.deposit.models import GmxDeposit
from dojo.actions.gmxV2.withdrawal.models import GmxWithdrawal
from dojo.agents import BaseAgent
from dojo.environments.gmxV2 import GmxV2Observation
from dojo.policies import BasePolicy


class State(Enum):
    NO_POSITION = 0
    POSITION_OPEN = 1
    FINISH = 2


class GmxV2Policy(BasePolicy):
    """Example gmx policy."""

    def __init__(self, agent: BaseAgent) -> None:
        """Initialize the policy."""
        super().__init__(agent=agent)
        self.state = State.NO_POSITION
        self.count = 0

    def fit(self):
        pass

    def predict(self, obs: GmxV2Observation) -> list[GmxDeposit]:
        self.count += 1
        total_trader_pnl = 0
        gm_token_value, market_pool_value_info = obs.get_market_token_price_for_traders(
            "WETH:WETH:USDC", True
        )
        index_token_price = obs.index_token_price(market_key="WETH:WETH:USDC")
        long_token_price = obs.long_token_price(market_key="WETH:WETH:USDC")
        short_token_price = obs.short_token_price(market_key="WETH:WETH:USDC")
        net_pnl = obs.get_net_pnl(market_key="WETH:WETH:USDC", maximize=True)
        long_pnl = obs.get_pnl(market_key="WETH:WETH:USDC", is_long=True, maximize=True)
        short_pnl = obs.get_pnl(
            market_key="WETH:WETH:USDC", is_long=False, maximize=True
        )
        long_open_interest_with_pnl = obs.get_open_interest_with_pnl(
            market_key="WETH:WETH:USDC", is_long=True, maximize=True
        )
        short_open_interest_with_pnl = obs.get_open_interest_with_pnl(
            market_key="WETH:WETH:USDC", is_long=False, maximize=True
        )
        market_info = obs.get_market_info(market_key="WETH:WETH:USDC")

        obs.add_signal("net pnl", net_pnl)
        obs.add_signal("long pnl", long_pnl)
        obs.add_signal("short pnl", short_pnl)
        obs.add_signal("long open interest with pnl", long_open_interest_with_pnl)
        obs.add_signal("short open interest with pnl", short_open_interest_with_pnl)
        obs.add_signal("gm token value", gm_token_value)
        obs.add_signal("index token price", index_token_price)
        obs.add_signal("long token price", long_token_price)
        obs.add_signal("short token price", short_token_price)
        total_trader_pnl = self.agent.reward(obs)

        index_token_price = obs.index_token_price(market_key="WETH:WETH:USDC")
        # SNIPPET 1 START
        if gm_token_value < Decimal(1.5) and self.state == State.NO_POSITION:
            self.state = State.POSITION_OPEN
            return [
                GmxDeposit(
                    agent=self.agent,
                    market_key="WETH:WETH:USDC",
                    initial_long_token_symbol="WETH",
                    initial_short_token_symbol="USDC",
                    long_token_usd=Decimal(100),
                    short_token_usd=Decimal(100),
                    observations=obs,
                )
            ]

        if self.state is State.POSITION_OPEN and self.count > 30:
            self.state = State.FINISH
            return [
                GmxWithdrawal(
                    agent=self.agent,
                    market_key="WETH:WETH:USDC",
                    gm_token_amount=Decimal(100),
                )
            ]
        # SNIPPET 1 END

        obs.add_signal("Current trader pnl", total_trader_pnl)

        return []
