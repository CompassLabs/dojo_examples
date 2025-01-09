# Dojo Examples

Welcome to the Dojo trading strategy development and backtesting environment! This repository contains code examples and guidance on how to use the [Dojo](https://www.compasslabs.ai/#dojo) Python package to develop and backtest your own trading strategies.

In order to run these examples, you must have Dojo installed on your machine with a valid license key (or [use the free sample simulations](https://compasslabs.ai/docs/frequently-asked-questions#how-can-i-try-out-dojo-before-buying-it)).

Please refer to the [**Getting Started**](https://www.compasslabs.ai/docs/getting-started) guide in the docs for more detailed instructions on getting set up 🙂

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Authentication](#authentication)
- [Docker Setup](#docker-setup)
- [Contributing](#contributing)
- [Contact](#contact)

## Introduction

Dojo is a powerful Python package developed by [Compass Labs](https://www.compasslabs.ai) that allows traders and quantitative analysts to develop, test, and deploy trading strategies efficiently. With Dojo, you can simulate trading strategies over historical data, analyze performance metrics, and optimize your strategies before deploying them to live markets.

## Features

- **Strategy Development**: Build custom trading strategies using a flexible and intuitive API.
- **Backtesting**: Simulate strategies over historical data to evaluate performance.
- **Performance Analysis**: Generate detailed reports and metrics to understand strategy behavior.

## Installation

We recommend using a virtual environment to manage dependencies:

```
python3 -m venv venv
source venv/bin/activate
```

Clone the Repository

```
git clone https://github.com/CompassLabs/dojo_examples.git
```

Install the Dojo package via pip:

```
pip install dojo-compass
```

Finally, [install Foundry](https://book.getfoundry.sh/getting-started/installation) on your system.

## Authentication

Dojo requires two configurations to run:

1. **A Valid License Key**
2. **An Archive Node URL** available from providers like Infura. 

You can also use the [free sample simulations](https://compasslabs.ai/docs/frequently-asked-questions#how-can-i-try-out-dojo-before-buying-it), in which case you _should_ set an empty archive node URL (e.g. `ETHEREUM_RPC_URL=`) but you _should not_ set a license key.

Set these as environment variables by following our guide [here](https://www.compasslabs.ai/docs/getting-started#3-setup-configuration).

## Docker Setup

We provide a `Dockerfile` to help you containerize your Dojo environment. Using Docker ensures consistency across different development environments and simplifies the setup process.

The Dockerfile builds an image that contains all the necessary dependencies to run Dojo simulations, including Python, Dojo, Foundry, and other required packages.

### Building the Docker Image

To build the Docker image, navigate to the root directory of the repository where the `Dockerfile` is located. You need to pass your `LICENSE_KEY` and at least one of the RPC URLs (`ETHEREUM_RPC_URL` or `ARBITRUM_RPC_URL`) as build arguments.

**Build Command:**

```bash
docker build . --build-arg LICENSE_KEY='your-license-key' --build-arg ETHEREUM_RPC_URL='your-ethereum-rpc-url'
```

**Notes:**

Replace `your-license-key` with your actual Dojo license key.
Replace `your-ethereum-rpc-url` with your Ethereum RPC URL (e.g., from Infura).
If you prefer to use Arbitrum, you can pass `ARBITRUM_RPC_URL` instead of `ETHEREUM_RPC_URL`.
Take note of the image hash (e.g., sha256:...) output at the end of the build process; you'll need it to run the container.

### Running the Docker Container
After building the image, you can run the container using the image hash obtained from the build step.

```
docker run <image-hash-from-build-command>
```

### Running a Trading Strategy on Docker
You can also run other examples by overriding the default command. The following command will run the moving averages trading strategy on the Docker container.

```
docker run <image hash from build command> poetry run python examples/moving_averages/run.py
```

## Contributing

If something isn't working as expected, please [raise an issue](https://github.com/CompassLabs/dojo_examples/issues) in this repository.

## Contact

For questions or support, please contact us at [support@compasslabs.ai](mailto:support@compasslabs.ai) or visit our website [compasslabs.ai](https://www.compasslabs.ai).

Happy trading! 🙂
