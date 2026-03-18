import json
import logging
from typing import Optional
from datetime import datetime, timedelta

from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class GithubRepository:
    COLLECTION = "github_cache"
    
    def  __init__(self, db: AsyncIOMotorDatabase, redis: Redis):
        self._db = db
        self._redis = redis
        self._col = db[self.COLLECTION]
        
    def _key(self, username: str) -> str:
        return f"gh:user:{username.lower()}"
    
    async def get_cached(self, username: str) -> Optional[dict]:
        try:
            raw = await self._redis.get(self._key(username))
            if raw:
                return json.loads(raw)    
        except Exception as e:
            logger.warning(f"Redis read failed for {username}: {e}")
        
        try:
            doc = await self._col.find_one({"username": username.lower()})    
            if doc:
                doc.pop("_id", None)
                return doc.get("data")
        except Exception as e:
            logger.warning(f"Mongo cache read failed for {username}: {e}")
        return None
    
    
    async def cache(self, username: str, data: dict, ttl: int) -> None:
        serialized = json.dumps(data, default=str) 
        try:
            await self._redis.setex(self._key(username), ttl, serialized)
        except Exception as e:
            logger.warning(f"Redis write failed for {username}: {e}")
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
        await self._redis.delete(self._key(username))
        await self._col.delete_one({"username": username.lower()})                 