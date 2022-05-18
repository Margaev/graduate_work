import logging
from typing import Optional
from datetime import datetime
from functools import lru_cache

import pymongo

from pymongo import MongoClient

from data_models.models import PacketModel

logging.basicConfig(level="INFO")


class MongoPacketFacade:
    def __init__(self, database: str, collection: str, username: str, password: str):
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

    def find(self, find_filter: Optional[dict], *args, **kwargs):
        self._collection.find(find_filter, *args, **kwargs)

    # @lru_cache
    def _find_packets_within_time_range(self, date_from_timestamp: int, date_to_timestamp: int):
        find_filter = {
            "timestamp": {
                "$gte": date_from_timestamp,
                "$lte": date_to_timestamp,
            },
            "networking_protocol": "IP",
        }
        return self._collection.count_documents(filter=find_filter)

    def find_num_of_ip_packets_per_minute(self, dtm: datetime):
        date_from = dtm.replace(second=0)
        date_to = dtm.replace(second=59)
        date_from_timestamp = int(date_from.timestamp())
        date_to_timestamp = int(date_to.timestamp())
        return self._find_packets_within_time_range(date_from_timestamp, date_to_timestamp)
