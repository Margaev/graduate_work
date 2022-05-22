import logging
from typing import Optional
from datetime import datetime
from functools import lru_cache

import pymongo

from pymongo import MongoClient

logging.basicConfig(level="INFO")


class MongoManager:
    def __init__(self, host: str, port: int, database: str, collection: str, username: str, password: str):
        self._client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
        )
        self._database = self._client.get_database(database)
        self._collection = self._database.get_collection(collection)

    def insert(self, data: dict):
        inserted = self._collection.insert_one(data)
        logging.info(
            "Inserted item db=%s, collection=%s, value=%s",
            self._database,
            self._collection,
            inserted
        )

    def upsert(self, find_filter: dict, update: dict):
        inserted = self._collection.update_one(find_filter, update, upsert=True)
        logging.info(
            "Inserted item db=%s, collection=%s, value=%s",
            self._database,
            self._collection,
            inserted
        )

    def find(self, find_filter: Optional[dict], *args, **kwargs):
        return self._collection.find(find_filter, *args, **kwargs)

    def find_ip_packets_count_per_minute(self, start_time: int, end_time: int, ascending: bool = True):
        return self.find(
            {"timestamp": {"$gte": start_time, "$lte": end_time}}
        ).sort("timestamp", pymongo.ASCENDING if ascending else pymongo.DESCENDING)

    def get_median_ip_packets_count_per_minute(self, start_time: int, end_time: int):
        return self.find(
            {"timestamp": {"$gte": start_time, "$lte": end_time}}
        ).sort(
            "packets_count", pymongo.ASCENDING
        ).skip(
            self._collection.count_documents({}) // 2
        ).limit(1)[0]["packets_count"]

    def find_tcp_ack_syn_count_per_minute(self, start_time: int, end_time: int, ascending: bool = True):
        return self.find(
            {"timestamp": {"$gte": start_time, "$lte": end_time}}
        ).sort("timestamp", pymongo.ASCENDING if ascending else pymongo.DESCENDING)
