"""
Dataset and Test Case CRUD service for EvalForge.
Handles persistence in MongoDB and manages dataset versioning.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.dataset import EvalDataset, TestCase, ContextChunk, TestType, DifficultyLevel
from app.schemas.dataset import DatasetCreateRequest, TestCaseCreateRequest


class DatasetService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is not None:
            return self._db
        return get_database()

    async def create_dataset(self, req: DatasetCreateRequest) -> EvalDataset:
        """Creates a new evaluation dataset in MongoDB."""
        dataset_id = f"ds_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()
        dataset = EvalDataset(
            dataset_id=dataset_id,
            name=req.name,
            domain=req.domain,
            description=req.description,
            sample_count=0,
            tags=req.tags,
            created_at=now,
            updated_at=now
        )
        if self.db is not None:
            await self.db["eval_datasets"].insert_one(dataset.model_dump())
        return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[EvalDataset]:
        """Retrieves an evaluation dataset by ID."""
        if self.db is None:
            return None
        doc = await self.db["eval_datasets"].find_one({"dataset_id": dataset_id}, {"_id": 0})
        if not doc:
            return None
        return EvalDataset(**doc)

    async def list_datasets(self, skip: int = 0, limit: int = 50) -> List[EvalDataset]:
        """Lists evaluation datasets with pagination."""
        if self.db is None:
            return []
        cursor = self.db["eval_datasets"].find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return [EvalDataset(**item) for item in items]

    async def delete_dataset(self, dataset_id: str) -> bool:
        """Deletes a dataset and all associated test cases."""
        if self.db is None:
            return False
        res = await self.db["eval_datasets"].delete_one({"dataset_id": dataset_id})
        if res.deleted_count > 0:
            await self.db["test_cases"].delete_many({"dataset_id": dataset_id})
            await self.db["benchmark_runs"].delete_many({"dataset_id": dataset_id})
            return True
        return False

    async def add_test_case(self, dataset_id: str, req: TestCaseCreateRequest) -> TestCase:
        """Appends a new test case to an evaluation dataset."""
        test_case_id = f"tc_{uuid.uuid4().hex[:10]}"
        case = TestCase(
            test_case_id=test_case_id,
            dataset_id=dataset_id,
            query=req.query,
            reference_contexts=req.reference_contexts,
            ground_truth_answer=req.ground_truth_answer,
            test_type=req.test_type,
            difficulty=req.difficulty,
            tags=req.tags,
            created_at=datetime.utcnow()
        )
        if self.db is not None:
            await self.db["test_cases"].insert_one(case.model_dump())
            await self._refresh_sample_count(dataset_id)
        return case

    async def add_test_cases_batch(self, dataset_id: str, cases: List[TestCase]) -> int:
        """Batch inserts synthesized test cases into MongoDB."""
        if not cases or self.db is None:
            return 0
        docs = [case.model_dump() for case in cases]
        res = await self.db["test_cases"].insert_many(docs)
        inserted = len(res.inserted_ids)
        await self._refresh_sample_count(dataset_id)
        return inserted

    async def list_test_cases(
        self,
        dataset_id: str,
        test_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestCase]:
        """Lists test cases for a dataset with optional filters."""
        if self.db is None:
            return []
        query: Dict[str, Any] = {"dataset_id": dataset_id}
        if test_type:
            query["test_type"] = test_type
        if difficulty:
            query["difficulty"] = difficulty

        cursor = self.db["test_cases"].find(query, {"_id": 0}).sort("created_at", 1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return [TestCase(**item) for item in items]

    async def get_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """Retrieves a single test case by ID."""
        if self.db is None:
            return None
        doc = await self.db["test_cases"].find_one({"test_case_id": test_case_id}, {"_id": 0})
        if not doc:
            return None
        return TestCase(**doc)

    async def delete_test_case(self, test_case_id: str) -> bool:
        """Deletes a test case and updates dataset counter."""
        if self.db is None:
            return False
        case_doc = await self.db["test_cases"].find_one({"test_case_id": test_case_id})
        if not case_doc:
            return False
        dataset_id = case_doc.get("dataset_id")
        res = await self.db["test_cases"].delete_one({"test_case_id": test_case_id})
        if res.deleted_count > 0 and dataset_id:
            await self._refresh_sample_count(dataset_id)
            return True
        return False

    async def _refresh_sample_count(self, dataset_id: str):
        """Updates sample_count in dataset document."""
        if self.db is not None:
            count = await self.db["test_cases"].count_documents({"dataset_id": dataset_id})
            await self.db["eval_datasets"].update_one(
                {"dataset_id": dataset_id},
                {"$set": {"sample_count": count, "updated_at": datetime.utcnow()}}
            )
