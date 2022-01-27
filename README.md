# DID Chain

## To run:
See the *setup*, then:

- `SWARM_BASE_DIR=<dir> CHAIN_COLLECTION=[chain name] python3 mock_chain/api.py`

- SWARM_BASE_DIR is required
- CHAIN_COLLECTION is optional, and its default value is `chain_testnet`

For example:
- `SWARM_BASE_DIR=~/.swarm_test python3 mock_chain/api.py`
- `SWARM_BASE_DIR=~/.swarm_test CHAIN_COLLECTION=chain_mainnet python3 mock_chain/api.py`

Then, issue a request get the did document associated to a known did.
For example, if the did of the DID Chain is `did:sw:7UJPYn6cmvNcqv2hWn3TDx`, the request can be sent as follows:
- `http :7878/dids/did:sw:7UJPYn6cmvNcqv2hWn3TDx accept:application/cbor-di`

## To test:
- `pytest --log-cli-level=info`

# Setup
1. Install requirements: `pip install -r requirements.txt`

2. Create the did_chain Swarm agent:
```bash
swarm_manager ~/.swarm_test --new_agent did_chain swarm:didChain 7878

# (requires an existing `broker` agent)
swarm_manager ~/.swarm_test --setup_trust did_chain broker
```

3. Setup mongodb:
```bash
docker create -it --name DidChain -p 27017:27017 mongo
docker start DidChain
```
