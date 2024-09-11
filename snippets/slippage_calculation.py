import logging
import sys
from decimal import Decimal

logging.basicConfig(
    level=logging.ERROR,  # Log only Errors from dojo itself.
    handlers=[logging.StreamHandler()],
    format="%(asctime)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


sys.path.append("..")
from agents.uniswapV3_pool_wealth import UniswapV3PoolWealthAgent
from dateutil import parser as dateparser

from dojo.actions.uniswapV3 import UniswapV3Quote, UniswapV3Trade
from dojo.common.constants import Chain
from dojo.environments import UniswapV3Env

POOL = "SAFE/WETH-0.1"
start_time = dateparser.parse("2024-06-21 00:00:00 UTC")
end_time = dateparser.parse("2024-06-21 06:00:00 UTC")


initial_portfolio = initial_portfolio = {
    "ETH": Decimal(0.2),  # just a bit of ETH to cover fees
    "SAFE": Decimal(0),
    "WETH": Decimal(100),  # We will try to trade WETH and track slippage
}
trader_agent = UniswapV3PoolWealthAgent(
    initial_portfolio=initial_portfolio,
    name="TraderAgent",
)

lp_agent = UniswapV3PoolWealthAgent(
    initial_portfolio={
        "SAFE": Decimal(100_000),
        "WETH": Decimal(1000),
        "ETH": Decimal(0.2),
    },  # Using this agent to massively increase pool liquidity
    name="LPAgent",
)

# Simulation environment (Uniswap V3)
env = UniswapV3Env(
    date_range=(start_time, end_time),
    chain=Chain.ETHEREUM,
    agents=[trader_agent, lp_agent],
    pools=[POOL],
    backend_type="forked",
    market_impact="replay",
)

obs = env.reset()
_, tick, _, _, _, _, _ = obs.slot0(POOL)
liquidity = obs.liquidity(POOL)
token0, token1 = obs.tokens()
price_1_in_0 = obs.price(token=token1, unit=token0, pool=POOL)
fee = obs.pool_fee(pool=POOL)
tick_spacing = obs.tick_spacing(POOL)

current_tick_range = obs.active_tick_range(POOL)

logger.info(
    "--------------------------------------------------------------------------------------------------------"
)
logger.info("INITIAL")
logger.info(f"tick: {tick}")
logger.info(f"liquidity: {liquidity}")
logger.info(f"pool_price: {float(price_1_in_0)}")
logger.info(f"current_tick_range: {current_tick_range}")
logger.info(f"agent portfolio {trader_agent.portfolio()}")
logger.info(
    "--------------------------------------------------------------------------------------------------------"
)

without_slippage = trader_agent.portfolio()[token1] * price_1_in_0 * (1 - fee)


# Provide LP in current tick range
env.step(
    actions=[
        UniswapV3Quote(
            agent=lp_agent,
            pool=POOL,
            quantities=(
                Decimal(10_000),
                Decimal(10),
            ),  # Change these parameters to add liqudidity
            tick_range=current_tick_range,
        )
    ]
)


liquidity_post_lp = obs.liquidity(POOL)
logger.info("AFTER LP PROVISION")
logger.info(f"liquidity: {liquidity_post_lp}")
logger.info(
    "--------------------------------------------------------------------------------------------------------"
)

env.step(
    actions=[
        UniswapV3Trade(
            agent=trader_agent,
            pool=POOL,
            quantities=(
                Decimal(0),
                Decimal(100),  # Trade all token1 to token0
            ),
        )
    ]
)
with_slippage = trader_agent.portfolio()[token0]
slippage = without_slippage - with_slippage

_, tick_post_trade, _, _, _, _, _ = obs.slot0(POOL)
price_1_in_0_post_trade = obs.price(token=token1, unit=token0, pool=POOL)

trader_agent.portfolio()
post_portfolio = trader_agent.portfolio()
effective_price = (post_portfolio[token0] - initial_portfolio[token0]) / (
    initial_portfolio[token1] - post_portfolio[token1]
)

post_trade_tick_range = obs.active_tick_range(POOL)
logger.info(f"AFTER TRADE")
logger.info(f"tick: {tick_post_trade}")
logger.info(f"pool_price: {float(price_1_in_0_post_trade)}")
logger.info(f"agent portfolio {trader_agent.portfolio()}")
logger.info(f"tick range {post_trade_tick_range}")
logger.info(
    "--------------------------------------------------------------------------------------------------------"
)
logger.info(f"effective trade price = {float(effective_price)}")
logger.info(f"slippage = {round(float(1-effective_price/price_1_in_0),2)*100} %")
# We expect to slippage to decrease if more LP is provided.
