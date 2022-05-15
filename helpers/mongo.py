import logging

import pymongo

from pymongo import MongoClient

from data_models.models import PacketModel

logging.basicConfig(level="INFO")


class MongoPacketFacade:
    def __init__(self, database, collection, username, password):
        self._client = MongoClient(
            host="127.0.0.1",
            port=27017,
            username=username,
            password=password,
        )
        self._database = self._client.get_database(database)
        self._collection = self._database.get_collection(collection)

    def insert(self, data: PacketModel):
        inserted = self._collection.insert_one(data.dict())
        logging.info(
            "Inserted item db=%s, collection=%s, value=%s",
            self._database,
            self._collection,
            inserted
        )
