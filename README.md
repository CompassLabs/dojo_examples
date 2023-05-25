# Dojo code examples

This repository contains code examples for the [Dojo](https://compasslabs.github.io/docs).

### Licensing

You will need a license key, to run `dojo`.  
To get started, you can request a **[trial license](mailto:elisabeth@compasslabs.ai?subject=Dojo%20trial%20license%20request&body=%3C%20Please%20let%20us%20know%20your%20name%20and%20the%20company%20you%20represent.%20We'll%20get%20back%20ASAP%20%3E)**.  
The trial license comes with limitations and is only valid for a limited amount of time on one machine, but it should be enough to get you excited about `dojo`.🥳

### Prerequisites
There's a few more things you need to set up for `dojo`. If you've done some coding in web3 before, chances are you're good to go already!

1. **RPC Node provider**  
   Setup and account with one of the provider, such as [Infura](https://www.infura.io/). You'll need the RPC_URL it provides. e.g. `https://mainnet.infura.io/v3/ac8ee<...>961`
2. **A local ethereum development environment**  
   We suggest Hardhat.  
   `npm install --save-dev hardhat`

### Setup

Setting up dojo shouln't take more than 5 minutes. Follow these steps:

#### 1. Install
`dojo` is provided as a Python package on PyPi.
To install, simply run  
```python3 -m pip install -i http://54.90.104.158:8080 dojo --trusted-host 54.90.104.158```


#### 2. Setup configuration
Create a `.env` file in your main directory.
```md title=".env" {1-4}
RPC_URL=<YOUR URL>
CHAIN=<chain> # one of ethereum, polygon
LICENSE_KEY=<YOUR LICENSE KEY>
```

#### 3. Verify install
If everything is set up correctly, the following command should throw no erros.
```
 python -c "import dojo"
```