from swarm_lib import DidDocument, Wallet, Agent
from jwcrypto import jwk, jwe
from swarm_sec import Keys, SecureBoxCOSE, SecureBoxJOSE
import pytest, cbor2, os, logging

os.environ["SWARM_BASE_DIR"] = "~/.did_chain_unit_test"
os.environ["CHAIN_COLLECTION"] = "unittestnet"

logging.info("Generating new did chain for testing at ~/.swarm_test_did_chain ...")
Wallet.init(os.environ["SWARM_BASE_DIR"])
did_chain_agent, keys = Agent.generate("did_chain", with_server=True, agent_type="swarm:didChain", port=7878)
Wallet.writeAgent(did_chain_agent, keys)
Wallet.writeRemoteAgent(did_chain_agent.to_remote())

from did_chain import api


@pytest.fixture
def client():
    api.did_chain_agent.flask_app.config["TESTING"] = True
    with api.did_chain_agent.flask_app.test_client() as client:
        yield client


def test_get(client):
    resp = client.get("/dids/123")
    assert resp.status_code == 404

ddo, keys = DidDocument.generate(with_server=True)
sig_jwkey = jwk.JWK(**keys[0])
sig_cwkey = Keys.ensure_cwk(sig_jwkey)

def test_post_cbor(client):
    payload = SecureBoxCOSE.sign1_sign(ddo.to_cbor(), sig_cwkey)
    print(payload)

    resp = client.post("/dids", data=payload, headers={"content-type": "application/cbor"})
    assert resp.status_code == 200
    assert resp.data == b''

    resp = client.get("/dids/%s" % ddo.id.encode(), headers={"accept": "application/cbor"})
    assert resp.status_code == 200
    assert resp.content_type == "application/cbor"
    rddo = DidDocument.from_dict(cbor2.loads(resp.data))
    assert rddo.id.encode() == ddo.id.encode()

def test_post_json(client):
    payload = SecureBoxJOSE.sign(ddo.to_json(), sig_jwkey)
    print(payload)

    resp = client.post("/dids", data=payload, headers={"content-type": "application/json"})
    assert resp.status_code == 200
    assert resp.data == b''

    resp = client.get("/dids/%s" % ddo.id.encode(), headers={"accept": "application/json"})
    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    rddo = DidDocument.from_dict(resp.get_json()["didDocument"])
    assert rddo.id.encode() == ddo.id.encode()
