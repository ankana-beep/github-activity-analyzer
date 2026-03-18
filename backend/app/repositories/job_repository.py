from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from app.models.job_model import Job

class JobRepository:
    COLLECTION = "jobs"
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[self.COLLECTION]
        
    async def create(self, job: Job) -> str:
        await self._col.insert_one(job.dict())
        return job.id
    
    async def find_by_id(self, job_id: str) -> Optional[Job]:
        doc = await self._col.find_one({"id": job_id})
        if doc:
            doc.pop("_id", None)
            return Job(**doc)
        return None
    
    async def list_all(self, limit: int = 50) -> List[Job]:
        cursor = self._col.find().sort("created_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(Job(**doc))
        return results  
    
    async def delete(self, job_id: str) -> None:
        await self._col.delete_one({"id": job_id})      
    
     