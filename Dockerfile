# Build the image like so:
# $ docker build . --build-arg LICENSE_KEY=... --build-arg ETHEREUM_RPC_URL=...
# Take note of the image hash at the end!

# And then run like this:
# $ docker run <image hash from build command>

# You can also run other examples by overriding the default command. For example:
# $ docker run <image hash from build command> poetry run python examples/moving_averages/run.py
FROM python:3.12.7-slim AS basesys

RUN apt update

RUN apt install -y gcc python3-dev lsof curl git

RUN apt install -y pipx
RUN pipx install poetry --system-site-packages
RUN ln -s /root/.local/bin/poetry /bin/poetry

RUN curl -L https://foundry.paradigm.xyz | bash 
RUN /root/.foundry/bin/foundryup
RUN ln -s /root/.foundry/bin/anvil /bin/anvil

FROM basesys AS basepackages

RUN mkdir /code
WORKDIR /code

RUN poetry init -n --python=3.12.7
RUN poetry add dojo-compass

FROM basepackages AS copyinexamples

WORKDIR /code
COPY . .

FROM copyinexamples AS setupsecrets

ARG LICENSE_KEY
ARG ETHEREUM_RPC_URL=no-eth-rpc-url-set
ARG ARBITRUM_RPC_URL=no-arb-rpc-url-set

WORKDIR /code

RUN test -n "$LICENSE_KEY" || (echo "You need to pass in a LICENSE_KEY with [--build-arg]!" && exit 1)
RUN test -n "$ETHEREUM_RPC_URL" || test -n "$ARBITRUM_RPC_URL"
RUN if [ "$ETHEREUM_RPC_URL" = "no-eth-rpc-url-set" ] && [ "$ARBITRUM_RPC_URL" = "no-arb-rpc-url-set" ]; then (echo "You need to pass in one of the RPC_URLs with [--build-arg]!" && exit 1); fi

RUN echo LICENSE_KEY=$LICENSE_KEY > .env
RUN echo ETHEREUM_RPC_URL=$ETHEREUM_RPC_URL >> .env
RUN echo ARBITRUM_RPC_URL=$ARBITRUM_RPC_URL >> .env

FROM setupsecrets

WORKDIR /code

CMD poetry run python examples/rsi/run.py --run-length 30m --log-level Info --no-simulation-status-bar
