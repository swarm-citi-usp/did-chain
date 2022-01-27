# DID Chain

## To run:
See the *setup*, then:

- `SWARM_BASE_DIR=<dir> CHAIN_COLLECTION=[chain name] python3 did_chain/api.py`

- SWARM_BASE_DIR is required
- CHAIN_COLLECTION is optional, and its default value is `chain_testnet`

For example:
- `SWARM_BASE_DIR=~/.swarm_test python3 did_chain/api.py`
- `SWARM_BASE_DIR=~/.swarm_test CHAIN_COLLECTION=chain_mainnet python3 did_chain/api.py`

Then, issue a request get the did document associated to a known did.
For example, if the did of the DID Chain is `did:sw:7UJPYn6cmvNcqv2hWn3TDx`, the request can be sent as follows:
- `http :7878/dids/did:sw:7UJPYn6cmvNcqv2hWn3TDx accept:application/cbor-di`

## To test:
- `pytest --log-cli-level=info`

# Setup
0. Optional: create a virtual environment
```bash
sudo apt install python3-virtualenv
virtualenv venv
source ./venv/bin/activate
```

1. Install deps and did-chain:
```bash
git clone git@github.com:swarm-citi-usp/swarm-sec.git
cd swarm-sec && git checkout develop && pip3 install -e .

git clone git@github.com:swarm-citi-usp/swarm-lib-python.git
cd swarm-lib-python && git checkout develop && pip3 install -e .

git clone git@github.com:swarm-citi-usp/did-chain.git
cd did-chain && pip3 install -e .
```

2. Create the did_chain Swarm agent:
```bash
swarm_manager ~/.swarm_testnet --new_agent did_chain swarm:didChain 7878

# (requires an existing `broker` agent)
# swarm_manager ~/.swarm_testnet --new_agent broker swarm:broker 4000
# SWARM_BASE_DIR=~/.swarm_testnet iex -S mix
swarm_manager ~/.swarm_testnet --setup_trust did_chain broker
```

3. Setup mongodb:
```bash
docker create -it --name DidChain -p 27017:27017 mongo
docker start DidChain
```

4. Finally, export DidChain as a remote agent for inclusion in other devices:
```bash
swarm_manager ~/.swarm_testnet --export_agent did_chain
# then, use the following to import:
# swarm_manager <swarm base dir> --add_remote did_chain
```
