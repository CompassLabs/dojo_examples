### Arbitrage Strategy
Arbitrage is taking advantage of the price difference of the same asset in two different markets (pools in our example). The arbitrage agent calculates the difference in price for an asset and buys from the pool where it's valued less and sells at a pool where it's valued more.

### How To Run
Run the `demo/start_dashboard.py` script using the following command if you would like to access your dashboard.
```bash
poetry run python start_dashboard.py
```

On another terminal window, copy the following command.
```bash 
poetry run python run_strategy.py
```
This command will setup your local blockchain, contracts, accounts and agents. You can then access your Dojo dashboard at http://localhost:8051.

### Step-by-step Explanation
```Python policy.py
class ArbitragePolicy(BasePolicy):
    def __init__(self, agent: BaseAgent) -> None:
        super().__init__(agent=agent)
        self.block_last_trade = -1
        self.min_block_dist = 20
        self.min_signal = 1.901
        self.tradeback_via_pool = None
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/arbitrage/policy.py#L10-L20) We create a new class called `ArbitragePolicy` which is a subclass of `BasePolicy`. We set additional variables such as `block_last_trade` and `min_block_dist` which ensure that trades are not too recent as this would cause a higher price impact.

```Python policy.py
def compute_signal(self, obs: UniV3Obs) -> Tuple[Decimal, Decimal]:
    pools = obs.pools
    pool_tokens_0 = obs.pool_tokens(pool=pools[0])
    pool_tokens_1 = obs.pool_tokens(pool=pools[1])
    assert (
        pool_tokens_0 == pool_tokens_1
    ), "This policy arbitrages same token pools with different fee levels."

    price_0 = obs.price(
        token=pool_tokens_0[0], unit=pool_tokens_0[1], pool=pools[0]
    )
    price_1 = obs.price(
        token=pool_tokens_0[0], unit=pool_tokens_0[1], pool=pools[1]
    )
    ratio = price_0 / price_1
    obs.add_signal(
        "Ratio",
        float(ratio),
    )
    signals = (
        ratio * (1 - obs.pool_fee(pools[0])) * (1 - obs.pool_fee(pools[1])),
        1 / ratio * (1 - obs.pool_fee(pools[0])) * (1 - obs.pool_fee(pools[1])),
    )

    obs.add_signal(
        "CalculatedProfit",
        float(max(signals)),
    )

    return signals
```
[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/arbitrage/policy.py#L26) This method calculates potential arbitrage signals between two pools. It first ensures that two pools trade the same token. It retrieves prices for the tokens in both pools and calculates the price ratio. It also adjusts this ratio by accounting for the fees in both pools to compute the net arbitrage signals.

```Python policy.py
def predict(self, obs: UniV3Obs) -> List[BaseAction]:
    pools = obs.pools
    pool_tokens_0 = obs.pool_tokens(pool=pools[0])
    pool_tokens_1 = obs.pool_tokens(pool=pools[1])
    assert (
        pool_tokens_0 == pool_tokens_1
    ), "This policy arbitrages same token pools with different fee levels."

    # Agent will always be in USDC
    amount_0 = self.agent.quantity(pool_tokens_0[0])
    amount_1 = self.agent.quantity(pool_tokens_0[1])

    # Since we don't support multihop yet, we need to trade this way for now.
    if self.tradeback_via_pool is not None:
        action = UniV3Trade(
            agent=self.agent,
            pool=self.tradeback_via_pool,
            quantities=(Decimal(0), amount_1),
        )
        self.tradeback_via_pool = None
        return [action]

    signals = self.compute_signal(obs)
    earnings = max(signals)
    index_pool_first = signals.index(max(signals))
    pool = obs.pools[index_pool_first]

    # Don't trade if the last trade was too recent
    if (
        earnings < self.min_signal
        or obs.block - self.block_last_trade < self.min_block_dist
    ):
        return []

    # Make first trade
    self.tradeback_via_pool = (
        obs.pools[0] if index_pool_first == 1 else obs.pools[1]
    )
    self.block_last_trade = obs.block
    return [
        UniV3Trade(
            agent=self.agent,
            pool=pool,
            quantities=(amount_0, Decimal(0)),
        )
    ]
```

[🔗](https://github.com/CompassLabs/dojo/blob/strategies/demo/strategies/arbitrage/policy.py#L59) Afterwards, we return a `UniV3Trade` object containing our order to buy/sell, specifying the pool, the quantity and the agent. If the last trade was too recent or no profit would be made, we return an empty list meaning no trade is being made.

In the `run_strategy.py` file, we create two pools, a Uniswap environment and an agent to implement the arbitrage strategy. 
