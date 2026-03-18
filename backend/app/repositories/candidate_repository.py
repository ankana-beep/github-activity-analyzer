from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from app.models.candidate_model import Candidate


class CandidateRepository:
    COLLECTION = "candidates"
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[self.COLLECTION]
        
    async def create(self, candidate: Candidate) -> str:
        await self._col.insert_one(candidate.dict())    
        return candidate.id
    
    async def find_by_id(self, candidate_id: str) -> Optional[Candidate]:
        doc = await self._col.find_one({"id": candidate_id})
        if doc:
            doc.pop("_id", None)
            return Candidate(**doc)
        return None
    
    async def update(self, candidate_id: str, patch: dict) -> None:
        patch["updated_at"] = datetime.utcnow()
        await self._col.update_one({"id": candidate_id}, {"set": patch})
        
    async def list_recent(self, limit: int = 20) -> List[Candidate]:
        cursor = self._col.find().sort("created_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(Candidate(**doc))
        return results    