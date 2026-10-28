"""
Synthetic data generation endpoints for EvalForge.
Generates multi-hop QA pairs, counterfactual perturbations, and hallucination traps.
"""

from fastapi import APIRouter, HTTPException, status
from app.services.synthetic_engine import SyntheticEngine
from app.services.dataset_service import DatasetService
from app.schemas.dataset import SyntheticGenerateRequest
from app.models.generator import SyntheticJob
from app.db.mongodb import get_database

router = APIRouter(prefix="/synthetic", tags=["Synthetic Generator"])
synthetic_engine = SyntheticEngine()
dataset_service = DatasetService()


@router.post("/generate", response_model=SyntheticJob, status_code=status.HTTP_201_CREATED)
async def generate_synthetic_data(req: SyntheticGenerateRequest):
    """Triggers synthetic test suite generation for a target dataset."""
    dataset = await dataset_service.get_dataset(req.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Target dataset '{req.dataset_id}' not found.")

    job = await synthetic_engine.generate_test_cases(req)
    return job


@router.get("/jobs/{job_id}", response_model=SyntheticJob)
async def get_synthetic_job(job_id: str):
    """Retrieves status and output statistics for a synthetic generation job."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    doc = await db["generator_jobs"].find_one({"job_id": job_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return SyntheticJob(**doc)
