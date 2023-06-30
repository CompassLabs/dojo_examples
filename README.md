# Dojo Examples

This repository contains code examples for `dojo`. In order to run these, you must have `dojo` installed on your machine with a valid license key. Please refer to the [docs](https://compasslabs.github.io/docs) for more detailed instructions on this.

## Installation

You'll need to clone this repository directly. For example, if you have SSH authentication, you can run:

```bash
git clone git@github.com:CompassLabs/dojo_examples.git
```


Then, install dojo via pip
```bash
pip install dojo
```

Finally, install hardhad on your system
```bash
npm install --save-dev hardhat
```


## Authentithication
To run dojo, you'll need to set these environment variables:

Please refere to the [documentation](https://dojo.compasslabs.ai) for details.

## Start the demo simulations

This can be run as a CLI with the command:

```
cd dojo_examples
python run.py
```


## If something isn't working...

We're a small team and `dojo` is a very early stage software. If something isn't working as expected, do [raise an issue in this repository](https://github.com/CompassLabs/dojo_examples/issues) and we'll do our best to fix whatever is wrong 🙂

## Module Guide

- `run.py`: the main runner file containing the simulation loop.
- `agents`: demo agent implementations tracking different metrics.
-  `policies`: demo policy implementations defining how an agent should interact with the environmnet.
