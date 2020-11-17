from mock_chain import api
from swarm_lib import DidDocument
from jwcrypto import jwk, jwe
from swarm_sec import SecureBoxCOSE, Keys
import pytest, cbor2


@pytest.fixture
def client():
    api.app.config["TESTING"] = True
    with api.app.test_client() as client:
        yield client


def test_get(client):
    resp = client.get("/dids/123")
    assert resp.status_code == 404

def test_post(client):
    ddo, keys = DidDocument.generate(with_server=True)
    jk = jwk.JWK(**keys[1])
    sig_key = Keys.jwk_to_cwk(jk)
    payload = SecureBoxCOSE.sign1_sign(ddo.to_cbor(), sig_key)
    print(payload)

    resp = client.post("/dids", data=payload, headers={"content-type": "application/cbor"})
    assert resp.status_code == 200
    assert resp.data == b''

    resp = client.get("/dids/%s" % ddo.id.encode(), headers={"accept": "application/cbor"})
    assert resp.status_code == 200
    assert resp.content_type == "application/cbor"
    rddo = DidDocument.from_dict(cbor2.loads(resp.data))
    assert rddo.id.encode() == ddo.id.encode()
