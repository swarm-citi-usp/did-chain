from flask import Flask, request, make_response, jsonify
from swarm_lib import DidDocument
from swarm_sec import SecureBoxCOSE, Keys
from jwcrypto import jwk, jwe
from cose.keys.cosekey import KeyOps
import base64, cbor2, cose, json

app = Flask(__name__)
chain = {}


@app.route('/dids', methods=["POST"])
def create_did():
    """
    echo '{
        "signature": ""
        "did": "did:sw:WbXxdsyQsCEVnHHS7VzTcP",
        "document": {
            "id": "did:sw:WbXxdsyQsCEVnHHS7VzTcP",
            "authentication": ["#vMXfGkJb"]
        }
    }' | http :7878/dids
    """
    print(">>> post %s" % request.data)
    if request.content_type == "application/cbor":
        ddo_cbor = cbor2.loads(request.data).value[2]
        ddo = DidDocument.from_dict(cbor2.loads(ddo_cbor))
        auth_method = ddo.get_verification_method("authentication")

        valid, _ = SecureBoxCOSE.sign1_verify(request.data, auth_method.as_cwk())
        if valid:
            chain[ddo.id.encode()] = ddo
            resp = make_response(b"", 200)
            resp.headers["content-type"] = "application/cbor"
            return resp
        else:
            resp = make_response(b"", 400)
            resp.headers["content-type"] = "application/cbor"
            return resp


@app.route('/dids/<did>', methods=["GET"])
def resolve_did(did=None):
    """
    http :7878/dids/did:sw:WbXxdsyQsCEVnHHS7VzTcP
    """
    print(">>> get %s" % did)
    if did in chain.keys():
        if "application/cbor" in request.accept_mimetypes:
            ddo = chain[did]
            resp = make_response(ddo.to_cbor(), 200)
            resp.headers["content-type"] = "application/cbor"
            return resp
        else:
            return jsonify({"status": "ok", "document": chain[did].to_dict()}), 200
    else:
        if request.accept_mimetypes == "application/cbor":
            resp = make_response(b"", 404)
            resp.headers["content-type"] = "application/cbor"
            return resp
        else:
            return jsonify({"status": "%s not found" % did}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7878)
