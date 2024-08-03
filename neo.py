import logging
from decimal import Decimal

logging.basicConfig(format="%(asctime)s - %(message)s", level=40)

from agents.uniV3_pool_wealth import UniV3PoolWealthAgent
from dateutil import parser as dateparser
from dojo.environments.uniswapV3 import UniV3Quote, UniV3Trade

from dojo.environments import UniV3Env

pool = "USDC/WETH-0.05"
start_time = dateparser.parse("2022-06-21 00:00:00 UTC")
end_time = dateparser.parse("2022-06-21 06:00:00 UTC")

trader_agent = UniV3PoolWealthAgent(
    initial_portfolio={
        "ETH": Decimal(0.2),  # just a bit of ETH to cover fees
        "USDC": Decimal(0),
        "WETH": Decimal(100),  # We will try to trade WETH and track slippage
    },
    name="TraderAgent",
)

lp_agent = UniV3PoolWealthAgent(
    initial_portfolio={"USDC": Decimal(10_000_000), "WETH": Decimal(100)}, # Using this agent to massively increase pool liquidity
    name="LPAgent",
)

# Simulation environment (Uniswap V3)
env = UniV3Env(
    date_range=(start_time, end_time),
    agents=[trader_agent, lp_agent],
    pools=[pool],
    backend_type="forked",
    market_impact="replay",
)

obs = env.reset()
_, tick, _, _, _, _, _ = obs.slot0(pool)
liquidity = obs.liquidity(pool)
price_weth_in_usdc = obs.price(token='WETH', unit='USDC', pool=pool)
fee = obs.pool_fee(pool=pool)

print("---------------")
print("INITIAL")
print(f"tick: {tick}")
print(f"liquidity: {liquidity}")
print(f"price: {float(price_weth_in_usdc)}")
print(f"agent portfolio {trader_agent.portfolio()}")
print("---------------")

without_slippage = trader_agent.portfolio()['WETH'] * price_weth_in_usdc * (1 - fee)

env.step(
    actions=[UniV3Quote(
        agent=lp_agent,
        pool="USDC/WETH-0.05",
        quantities=[Decimal(10_000_000), Decimal(100)],  # Change these parameters to add liqudidity
        tick_range=((tick // 10) * 10, (tick // 10 + 1) * 10),  # Provide liquidity only in a narrow tick range
    )]
)

liquidity_post_lp = obs.liquidity(pool)
print("AFTER LP PROVISION")
print(f"liquidity: {liquidity_post_lp}")
print("---------------")

env.step(
    actions=[UniV3Trade(
        agent=trader_agent,
        pool="USDC/WETH-0.05",
        quantities=[Decimal(0), Decimal(100)],  # Provide liquidity only in the current tick
    )]
)
with_slippage = trader_agent.portfolio()['USDC']
slippage = without_slippage - with_slippage

_, tick_post_trade, _, _, _, _, _ = obs.slot0(pool)
price_weth_in_usdc_post_trade = obs.price(token='WETH', unit='USDC', pool=pool)
print(f"AFTER TRADE")
print(f"tick: {tick_post_trade}")
print(f"price: {float(price_weth_in_usdc_post_trade)}")
print(f"agent portfolio {trader_agent.portfolio()}")
print(f"slippage = {float(slippage)} USDC")
print("---------------")
