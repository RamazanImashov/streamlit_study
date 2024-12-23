# utils/database.py
from pymongo import MongoClient
from datetime import datetime
from cachetools import TTLCache
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client.logistics
        self.shipments = self.db.shipments
        self.cache = TTLCache(maxsize=100, ttl=300)

    async def fetch_shipments(self, date_filter: Optional[datetime] = None) -> List[Dict]:
        try:
            query = {}
            if date_filter:
                query["created_at"] = {
                    "$gte": datetime.combine(date_filter, datetime.min.time()),
                    "$lte": datetime.combine(date_filter, datetime.max.time())
                }
            return list(self.shipments.find(query, {"_id": 0}))
        except Exception as e:
            logger.error(f"Error fetching shipments: {e}")
            raise

    async def add_shipment(self, data: Dict[str, Any]) -> bool:
        try:
            data["created_at"] = datetime.now()
            result = self.shipments.insert_one(data)
            self.cache.clear()
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"Error adding shipment: {e}")
            return False
