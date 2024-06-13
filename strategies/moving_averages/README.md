## Moving Averages Strategy
A moving averages trading strategy involves using MAs to identify market trends. A moving average smooths out price data by creating a constantly updated average price. The average is typically taken over a specific period, such as 10, 20, 50, or 200 days. If the current price is above the moving average, it indicates an uptrend. Conversely, if the current price is below the moving average, it suggests a downtrend.

## How To Run
Run the `start_dashboard.py` script using the following command if you would like to access your dashboard.
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
class MovingAveragePolicy(BasePolicy):
    """Moving average trading policy for a UniV3Env with a single pool.

    :param agent: The agent which is using this policy.
    :param short_window: The short window length for the moving average.
    :param long_window: The long window length for the moving average.
    """
    def __init__(self, agent: BaseAgent, short_window: int, long_window: int) -> None:
        super().__init__(agent=agent)
        self._short_window = short_window
        self._long_window = long_window
        self.long_window = deque(maxlen=long_window)
        self.short_window = deque(maxlen=short_window)
```

[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/moving_averages/policy.py#L13) The `MovingAveragePolicy` is a subclass of `BasePolicy` which has an abstract method called `predict`. The `predict` function is where you tell the agent under which conditions it should buy/sell. 

```Python policy.py
if self._x_to_y_indicated(pool_tokens):
            y_quantity = self.agent.quantity(pool_tokens[1])
            self._clear_windows()
            return [
                UniV3Trade(
                    agent=self.agent,
                    pool=pool,
                    quantities=(Decimal(0), y_quantity),
                )
            ]
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/moving_averages/policy.py#L72) In the Moving Averages strategy, we have 2 helper functions which tell us if the shorter moving average has crossed above or below the longer moving average. If so, we create a `UniV3Trade` object and return it with the required parameters such as quantities, agent and pool.

To run our trading simulation, we need to create instances of agents, environments and policies so we run the `run_strategy.py` file.
