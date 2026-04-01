from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# singletons
_mongo_client: Optional[AsyncIOMotorClient] = None

async def connect_mongo() -> None:
    global _mongo_client
    _mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    logger.info("MongoDB connected")
    await _ensure_indexes()


async def disconnect_mongo() -> None:
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        logger.info("MongoDB disconnected")


def get_db() -> AsyncIOMotorDatabase:
    if _mongo_client is None:
        raise RuntimeError("MongoDB not connected")
    return _mongo_client[settings.MONGODB_DB]

async def _ensure_indexes()-> None:
    db = get_db()
    await db["candidates"].create_index("id", unique=True)
    await db["candidates"].create_index("status")
    await db["candidates"].create_index("created_at")
    await db["github_cache"].create_index("username", unique=True)
    await db["github_cache"].create_index(
        "expires_at", expireAfterSeconds=0 #TTL index
    )
    await db["reports"].create_index("candidate_id")
    await db["jobs"].create_index("id",unique=True)
    logger.info("MongoDB indexes ensured")