import json
import logging
from typing import Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class GithubRepository:
    COLLECTION = "github_cache"

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._col = db[self.COLLECTION]

    async def get_cached(self, username: str) -> Optional[dict]:
        try:
            doc = await self._col.find_one({"username": username.lower()})
            if doc:
                doc.pop("_id", None)
                return doc.get("data")
        except Exception as e:
            logger.warning(f"Mongo cache read failed for {username}: {e}")
        return None

    async def cache(self, username: str, data: dict, ttl: int) -> None:
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            await self._col.update_one(
                {"username": username.lower()},
                {"$set": {"username": username.lower(), "data": data, "expires_at": expires_at}},
                upsert=True,
            )
        except Exception as e:
            logger.warning(f"Mongo cache write failed for {username}: {e}")

    async def invalidate(self, username: str) -> None:
        await self._col.delete_one({"username": username.lower()})                 