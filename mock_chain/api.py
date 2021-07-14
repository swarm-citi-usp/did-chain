from flask import Flask, request, make_response, jsonify
from swarm_lib import DidDocument, Agent, Storage
from swarm_sec import Keys, SecureBoxCOSE, SecureBoxJOSE
from jwcrypto import jwk, jwe
from cose.keys.cosekey import KeyOps
import base64, cbor2, cose, json, sys, os

"""
# Setup for the the `did_chain` agent
```
swarm_manager ~/.swarm_demo --new_agent did_chain swarm:didChain 7878

# (requires an existing `broker` agent)
swarm_manager ~/.swarm_test --setup_trust did_chain broker
```
"""

if "SWARM_BASE_DIR" in os.environ:
    Storage.init(os.environ["SWARM_BASE_DIR"], relative_to_home=False)
else:
    Storage.init(".swarm_test")

did_chain = Agent.from_config("did_chain")
did_chain.enable_flask_app(__name__)
did_chain.flask_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
chain = {}
chain[did_chain.id.encode()] = did_chain.did_document


@did_chain.flask_app.route('/dids', methods=["POST"])
def create_did():
    """Anchor a new DID Document.

    Note that this route does not use DIoTComm, due to the fact that
    in DIoTComm, the procedure is to look up the keys in the blockchain,
    which is not possible here since this is the blockchain itself.
    """
    print(">>> post %s %s %s" % (len(request.data), request.content_type, request.data))
    if request.content_type == "application/json":
        ddo_b64url = json.loads(request.data)["payload"]
        ddo_str = SecureBoxJOSE.from_b64url(ddo_b64url).decode("utf-8")
        ddo = DidDocument.from_dict(json.loads(ddo_str))
        auth_method = ddo.get_verification_method("authentication")
        print(auth_method.as_jwk())
        valid, _ = SecureBoxJOSE.verify(request.data, auth_method.as_jwk())
        if valid:
            chain[ddo.id.encode()] = ddo
            return "", 200
        else:
            return "", 400
    else:
        ddo_binary = cbor2.loads(request.data).value[2]
        print("DDo binary: %s" % ddo_binary)
        if request.content_type == "application/cbor":
            ddo = DidDocument.from_cbor(ddo_binary)
        elif request.content_type == "application/cbor-di":
            ddo = DidDocument.from_cbor_di(ddo_binary)
            print("DDo from cbor-di: %s" % ddo.to_dict())

        auth_method = ddo.get_verification_method("authentication")

        valid, _ = SecureBoxCOSE.sign1_verify(request.data, auth_method.as_cwk())
        if valid:
            chain[ddo.id.encode()] = ddo
            resp = make_response(b"", 200)
            resp.headers["content-type"] = request.content_type
            return resp
        else:
            resp = make_response(b"", 400)
            resp.headers["content-type"] = request.content_type
            return resp


@did_chain.flask_app.route('/dids/<did>', methods=["GET"])
def resolve_did(did=None):
    """Resolve an existing DID Document.
    
    This route currently does not use DIoTComm. It might, in the future.
    """
    print(">>> get %s %s" % (did, request.accept_mimetypes))
    if did in chain.keys():
        ddo = chain[did]
        if "application/cbor-di" in request.accept_mimetypes:
            resp = make_response(ddo.to_cbor_di(), 200)
            resp.headers["content-type"] = "application/cbor-di"
            return resp
        elif "application/cbor" in request.accept_mimetypes:
            resp = make_response(ddo.to_cbor(), 200)
            resp.headers["content-type"] = "application/cbor"
            return resp
        else:
            return jsonify({"status": "ok", "didDocument": ddo.to_dict()}), 200
    else:
        if "application/cbor" in request.accept_mimetypes:
            resp = make_response(b"", 404)
            resp.headers["content-type"] = "application/cbor"
            return resp
        else:
            return jsonify({"status": "%s not found" % did}), 404


if __name__ == "__main__":
    did_chain.register_at_broker()
    did_chain.serve_with_flask(debug=True)
