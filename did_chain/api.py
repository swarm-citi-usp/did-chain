# Copyright (C) 2022 Geovane Fedrecheski <geonnave@gmail.com>
#               2022 Universidade de São Paulo
#               2022 LSI-TEC

# This file is part of the SwarmOS project, and it is subject to 
# the terms and conditions of the GNU Lesser General Public License v2.1. 
# See the file LICENSE in the top level directory for more details.

import logging
from did_chain import ChainDB
from flask import Flask, request, make_response, jsonify
from swarm_lib import DidDocument, Agent, Wallet
from swarm_sec import Keys, SecureBoxCOSE, SecureBoxJOSE
from jwcrypto import jwk, jwe
from cose.keys.cosekey import KeyOps
import base64, cbor2, cose, json, sys, os


Wallet.init(os.environ["SWARM_BASE_DIR"])
did_chain_agent = Agent.from_config("did_chain")
did_chain_agent.enable_flask_app(__name__)
did_chain_agent.flask_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

chain_db = ChainDB(os.environ.get("CHAIN_COLLECTION"))
chain_db.add_self_ddo({"_id": did_chain_agent.id.encode(), **did_chain_agent.did_document.to_dict()})
logging.debug(f"Added or updated chain with self ddo: {json.dumps(chain_db.read_chain(), indent=4)}")


@did_chain_agent.flask_app.route('/dids', methods=["POST"])
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
            chain_db.add_ddo({"_id": ddo.id.encode(), **ddo.to_dict()})
            return "", 200
        else:
            return "", 400
    else:
        ddo_binary = cbor2.loads(request.data).value[2]
        print("DDo binary: %s" % (ddo_binary))
        if request.content_type == "application/cbor":
            ddo = DidDocument.from_cbor(ddo_binary)
            print("DDo from cbor: %s" % ddo.to_dict())
        elif request.content_type == "application/cbor-di":
            ddo = DidDocument.from_cbor_di(ddo_binary)
            print("DDo from cbor-di: %s" % ddo.to_dict())

        auth_method = ddo.get_verification_method("authentication")

        valid, _ = SecureBoxCOSE.sign1_verify(request.data, auth_method.as_cwk())
        if valid:
            chain_db.add_ddo({"_id": ddo.id.encode(), **ddo.to_dict()})
            resp = make_response(b"", 200)
            resp.headers["content-type"] = request.content_type
            return resp
        else:
            resp = make_response(b"", 400)
            resp.headers["content-type"] = request.content_type
            return resp


@did_chain_agent.flask_app.route('/dids/<did>', methods=["GET"])
def resolve_did(did=None):
    """Resolve an existing DID Document.
    
    This route currently does not use DIoTComm. It might, in the future.
    """
    logging.info("<<< get %s %s" % (did, request.accept_mimetypes))
    ddo = chain_db.get_ddo(did)
    logging.info("--- read from db ok")
    response = None
    if ddo:
        if "application/cbor-di" in request.accept_mimetypes:
            response = make_response(ddo.to_cbor_di(), 200)
            response.headers["content-type"] = "application/cbor-di"
        elif "application/cbor" in request.accept_mimetypes:
            response = make_response(ddo.to_cbor(), 200)
            response.headers["content-type"] = "application/cbor"
        else:
            response = jsonify({"status": "ok", "didDocument": ddo.to_dict()}), 200
    else:
        if "application/cbor" in request.accept_mimetypes or "application/cbor-di" in request.accept_mimetypes:
            response = make_response(b"", 404)
            response.headers["content-type"] = "application/cbor"
        else:
            response = jsonify({"status": "%s not found" % did}), 404
    logging.info(">>> sending response")
    return response


if __name__ == "__main__":
    did_chain_agent.register_at_broker()
    did_chain_agent.serve_with_flask(debug=False)
