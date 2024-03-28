# Copyright (C) 2022 Geovane Fedrecheski <geonnave@gmail.com>
#               2022 Universidade de São Paulo
#               2022 LSI-TEC

# This file is part of the SwarmOS project, and it is subject to
# the terms and conditions of the GNU Lesser General Public License v2.1.
# See the file LICENSE in the top level directory for more details.

from pymongo import MongoClient
from swarm_lib import DidDocument
import logging

class ChainDB:
    def __init__(self, collection):
        mongo_config = dotenv.dotenv_values(".env")
        
        self.client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=3000)
        database = "DidChain"
        collection = collection or "chain_testnet"
        logging.debug(f"Initializing ChainDB with {database} {collection}")
        self.cursor = self.client[database]
        self.cursor.authenticate(mongo_config["MONGO_USER"], mongo_config["MONGO_PWD"])
        self.collection = self.cursor[collection]

    def read_chain(self):
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def get_ddo(self, did):
        ddo = self.collection.find_one({"_id": did})
        if ddo:
            return DidDocument.from_dict(ddo)

    def add_self_ddo(self, new_document):
        logging.info('Writing Data')
        try:
            result = self.collection.update_one({"_id": new_document["_id"]}, {"$set": new_document}, upsert=True)
            return True
        except Exception as e:
            logging.exception("Error adding or updating self did document")
            return False

    def add_ddo(self, new_document):
        logging.info('Writing Data')
        try:
            result = self.collection.update_one({"_id": new_document["_id"]}, {"$set": new_document}, upsert=True)
            logging.debug('Document added or updated')
            return True
        except Exception as e:
            logging.exception("Error adding did document")
            return False
