from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from app.models.report_model import Report

class ReportRepository:
    COLLECTION = "Reports"
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db[self.COLLECTION]
        
    async def create(self, report: Report) -> str:
        await self._col.insert_one(report.dict())
        return report.id
    
    async def find_by_candidate(self, candidate_id: str) -> Optional[Report]:
        doc = await self._col.find_one(
            {"candidate_id": candidate_id},
            sort=[("generated_at", -1)]
        )
        if doc:
            doc.pop("_id", None)
            return Report(**doc)
        return None
    
    async def find_by_candidate(self, candidate_id: str) -> Optional[Report]:
        doc = await self._col.find_one(
            {"candidate_id": candidate_id},
            sort=[("generated_at", -1)]
        )
        if doc:
            doc.pop("_id", None)
            return Report(**doc)
        return None
    
    async def list_by_candidate(self, candidate_id: str) -> List[Report]:
        cursor = self._col.find({"candidate_id": candidate_id}).sort("generated_at", -1)
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(Report(**doc))
        return results
