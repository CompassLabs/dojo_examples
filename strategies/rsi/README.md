## Relative Strength Index Strategy
The Relative Strength Index (RSI) is a momentum oscillator used in technical analysis to measure the speed and change of price movements of an asset. It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions in a market. 

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

## Example Results
If you would like to view results of this trading strategy that we ran, download `rsi_results.json`, start your Dojo dashboard and load the file.

## Step-by-step Explanation
```Python policy.py
class RSIPolicy(BasePolicy):
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.rsi_period = 14 # block interval to calculate RSI
        self.rsi_values = deque(maxlen=self.rsi_period)
        self.rsi = 0
        self.buying = False
        self.selling = False
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/rsi/policy.py#L14) We create a subclass of `BasePolicy` called `RSIPolicy` which initializes some variables that will be used later on.

```Python policy.py
pool = obs.pools[0] # retrieve the pool
token0, token1 = obs.pool_tokens(pool) # retrieve the tokens in the pool

# calculate RSI
self.rsi_values.append(obs.price(token1, token0, pool)) # add the current price of the token to a list
if len(self.rsi_values) == self.rsi_period: # check if we have reached the block interval to calculate RSI
    delta = np.diff(self.rsi_values) # creates a list of numbers that represent the differences between every adjacent number

    gains = delta[delta > 0] # list with only positive price changes
    losses = -delta[delta < 0] # list with only negative price changes
    if losses.size == 0: # if there have been no price fall, then RSI = 100
        self.rsi = 100
        self.rsi_values.clear()
    elif gains.size == 0: # if there have been no price rise, then RSI = 0
        self.rsi = 0
        self.rsi_values.clear()
    else:
        gain = Decimal(gains.mean()) # calculates average gain
        loss = Decimal(losses.mean()) # calculates average loss
        rs = gain / loss
        self.rsi = 100 - 100 / (1 + rs) # here is the rsi formula
        self.rsi_values.clear()

obs.add_signal("RSI", self.rsi)
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/rsi/policy.py#L26) Signals allow us to easily view data on our Dojo dashboard. In this example, we are adding a signal to monitor the RSI value over time. We can then add bookmarks on the dashboard to view when a trade was made and at what RSI value.

```Python policy.py
def predict(self, obs: UniV3Obs) -> List[BaseAction]:
    pool = obs.pools[0]
    token0, token1 = obs.pool_tokens(pool)

    # make decision
    if self.rsi < 30: # RSI being less than 30 shows us that the token is oversold/undervalued so we buy
        self.buying = True
    elif self.rsi > 70: # RSI being above 70 shows us that the token is undersold/overvalued so we sell
        self.selling = True

    # execute action
    if self.buying:
        self.reset()
        if self.agent.quantity(token0) == Decimal(0): # if we don't have enough balance, do no trades
            return []
        return [ # otherwise, spend all of the other tokens to buy 
            UniV3Trade(
                self.agent, 
                pool, 
                (Decimal(self.agent.quantity(token0)), Decimal(0)))
            ]
    elif self.selling:
        self.reset()
        if self.agent.quantity(token1) == Decimal(0):
            return []
        return [ # if we have enough balance, spend all tokens to buy the other token
            UniV3Trade(
                self.agent, 
                pool, 
                (Decimal(0), Decimal(self.agent.quantity(token1))))
        ]
    return []
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/rsi/policy.py#L49) The RSI value being less than 30 shows us that the token is oversold and undervalued. Therefore, we set the buying variable to True. Then, if the agent doesn't have enough balance to trade, we return an empty list which means do no trades. Otherwise, we return a `UniV3Trade` object specifying the agent, the pool and the amount of each token to buy/sell. In the USDC/WETH pool, returning a `UniV3Trade` object with `quantities=(Decimal(self.agent.quantity(token0)), Decimal(0))` means we are swapping all of our USDC tokens for WETH tokens, essentially buying WETH. The converse is true for selling WETH.

In the `run_strategy.py` file, we create a pool, a Uniswap environment and an agent that implements the RSI policy. 
