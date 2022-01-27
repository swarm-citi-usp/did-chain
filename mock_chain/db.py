from pymongo import MongoClient
from swarm_lib import DidDocument
import logging

class ChainDB:
    def __init__(self, collection):
        self.client = MongoClient("mongodb://localhost:27017/")
        database = "DidChain"
        collection = collection or "chain_testnet"
        logging.debug(f"Initializing ChainDB with {database} {collection}")
        cursor = self.client[database]
        self.collection = cursor[collection]

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
            result = self.collection.insert_one(new_document)
            return True
        except Exception as e:
            logging.exception("Error adding did document")
            return False
