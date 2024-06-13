## Dollar Cost Averaging Strategy
Dollar Cost Averaging (DCA) is an investment strategy that involves regularly investing a fixed amount of money into a particular asset regardless of the asset's price. 
This means purchasing more shares when prices are low and fewer shares when prices are high. The main objective is to reduce the impact of volatility on the overall purchase and avoid the pitfalls of trying to time the market.

## How To Run
Run the `demo/start_dashboard.py` script using the following command if you would like to access your dashboard.
```bash
poetry run python start_dashboard.py
```

On another terminal window, copy the following command.
```bash 
poetry run python run_strategy.py
```
This command will setup your local blockchain, contracts, accounts and agents. You can then access your Dojo dashboard at http://localhost:8051.

## Step-by-step Explanation
```Python policy.py
class DCAPolicy(BasePolicy):
    def __init__(self, agent: BaseAgent, buying_amount: float, min_dist: int) -> None:
        super().__init__(agent=agent)
        self.buying_amount = buying_amount
        self.min_dist = min_dist
        self.last_trade_block = 0
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/dollar_cost_averaging/policy.py#L10) We create a subclass of `BasePolicy` called `DCAPolicy` which takes in 2 parameters: `buying_amount` and `min_dist`. `buying_amount` specifies the amount of tokens we should trade for the other token, and `min_dist` specifies the time interval in blocks between each trade. On the Ethereum blockchain, the block time is approximately 12 seconds, while the block time on Arbitrum is ~0.26 seconds.

```Python policy.py
pool = obs.pools[0] # retrieves the pool
token0, token1 = obs.pool_tokens(pool) # retrieves the tokens in the pool
portfolio = self.agent.portfolio() # gets the current portfolio of the agent in Dict[str, Decimal] format

token0_balance = portfolio.get(token0, 0) # gets amount of token0 in the portfolio. In the USDC/WETH pool, this would be the amount of USDC.
token1_balance = portfolio.get(token1, 0)

# calculate the value of the portfolio if the agent bought the token all at once
value_if_held = self.agent.initial_portfolio[token0] * Decimal(1.0) + self.agent.initial_portfolio[token1] * obs.price(token1, unit=token0, pool=pool)

# calculate the current value of the portfolio as the agent is dollar cost averaging
dca_value = token0_balance * Decimal(1.0) + token1_balance * obs.price(token1, unit=token0, pool=pool)

wealth_difference = dca_value - value_if_held
obs.add_signal("Wealth Difference", wealth_difference)
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/dollar_cost_averaging/policy.py#L24) Signals allow us to easily view data on our Dojo dashboard. In this example, we are adding a signal to monitor the difference in wealth if the agent bought the token all at once at current price vs. dollar cost averaging. 

```Python policy.py
def predict(self, obs: UniV3Obs) -> List[BaseAction]:
    pool = obs.pools[0]
    token0, token1 = obs.pool_tokens(pool)
    portfolio = self.agent.portfolio()

    if token0 in portfolio:
        if (
            portfolio[token0] >= self.buying_amount
            and obs.block - self.last_trade_block >= self.min_dist
        ):
            self.last_trade_block = obs.block
            return [
                UniV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(Decimal(self.buying_amount), Decimal(0)),
                )
            ]
    return []
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/dollar_cost_averaging/policy.py#L45) Here, we check if we have sufficient funds to purchase tokens and if enough time has passed since our last trade. If both conditions are met, we set the `last_trade_block` to the current block and return a `UniV3Trade` object specifying the buying amount. Otherwise, we return an empty list which means do nothing.

In the `run_strategy.py` file, we create a pool, a Uniswap environment and an agent that implements the dollar cost averaging policy. 
