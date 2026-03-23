from motor.motor_asyncio import AsyncIOMotorClient, AyncIOMotorCollection, AsyncIOMotorDatabase
from redis.asyncio import Redis
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# singletons
_mongo_client: AsyncIOMotorClient | None = None
_redis_client: Redis | None = None

async def connect_mongo() -> None:
    global _mongo_client
    _mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    logger.info("MongoDB connected")
    await _ensure_indexes()


async def disconnect_mongo() -> None:
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        logger.info("MongoDB disconnected")


async def connect_redis() -> None:
    global _redis_client
    _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info("Redis connected")
    

async def disconnect_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.close()   
        logger.info("Redis disconnected")  
        
def get_db() -> AsyncIOMotorDatabase:
    if _mongo_client is None:
        raise RuntimeError("MongoDB not connected")
    return _mongo_client[settings.MONGODB_DB]


def get_redis() -> Redis:
    if _redis_client is None:
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