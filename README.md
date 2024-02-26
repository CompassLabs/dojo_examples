[![pipeline status](https://github.com/CompassLabs/dojo_examples/actions/workflows/run_all.yml/badge.svg)](https://github.com/CompassLabs/dojo_examples/actions/workflows/run_all.yml)
[![pipeline status](https://github.com/CompassLabs/dojo_examples/actions/workflows/run_sim_with_dashboard.yml/badge.svg)](https://github.com/CompassLabs/dojo_examples/actions/workflows/run_sim_with_dashboard.yml)
#[![codecov](https://codecov.io/gh/CompassLabs/dojo_examples/branch/main/graph/badge.svg?token=RJWT1KWPWG)](https://codecov.io/gh/CompassLabs/dojo_examples)

[👉 **TRY IT NOW**](https://codesandbox.io/p/github/compasslabs/dojo_examples)

# Dojo Examples 🥷


This repository contains code examples for `dojo` 🎉. In order to run these, you must have `dojo` installed on your machine with a valid license key. Please refer to the [***Getting Started***](https://dojo.compasslabs.ai/tutorial/Getting_Started) guide in the docs for more detailed instructions on getting setup  🙂

## ⬇️ Installation

You'll need to clone this repository directly. For example, if you have SSH authentication, you can run:

```bash
git clone git@github.com:CompassLabs/dojo_examples.git
```


Then, install dojo via pip
```bash
pip install dojo-compass
```

Finally, [install](https://book.getfoundry.sh/getting-started/installation) anvil on your system
```bash
curl -L https://foundry.paradigm.xyz | bash
```
This will install Foundryup, then simply follow the instructions on-screen, which will make the foundryup command available in your CLI.

## 📄 Authentication
You'll need a license key and access to an archive node (e.g. from Infura) to run `dojo`.

Please refere to the [documentation](https://dojo.compasslabs.ai/tutorial/Getting_Started) for details on how to pass these as environment variables.

## 🏎️ Start the demo simulations

This can be run as a CLI with the command:

```bash
cd dojo_examples
python run.py
```


## 😧 If something isn't working...

We're a small team and `dojo` is a very early stage software. If something isn't working as expected, do [raise an issue in this repository](https://github.com/CompassLabs/dojo_examples/issues) and we'll do our best to fix whatever is wrong 🙂

## 📖 Module Guide

- `run.py`: the main runner file containing the simulation loop.
- `agents`: demo agent implementations tracking different metrics.
-  `policies`: demo policy implementations defining how an agent should interact with the environmnet.
