"""
Hallucination benchmark and evaluation endpoints for EvalForge.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.services.benchmark_service import BenchmarkService
from app.services.dataset_service import DatasetService
from app.schemas.benchmark import (
    BenchmarkRunCreateRequest,
    BenchmarkRunResponse,
    EvaluationResultResponse,
    BenchmarkComparisonResponse,
    LeaderboardResponse
)

router = APIRouter(prefix="/benchmarks", tags=["Hallucination Benchmarks"])
benchmark_service = BenchmarkService()
dataset_service = DatasetService()


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_multi_model_leaderboard():
    """Aggregates and ranks target LLMs across faithfulness, groundedness, and hallucination resilience."""
    return await benchmark_service.get_model_leaderboard()


@router.post("/runs", response_model=BenchmarkRunResponse, status_code=status.HTTP_201_CREATED)
async def create_benchmark_run(req: BenchmarkRunCreateRequest):
    """Executes an automated hallucination benchmark run across dataset test cases."""
    dataset = await dataset_service.get_dataset(req.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{req.dataset_id}' not found.")
    run = await benchmark_service.create_and_execute_run(req)
    return run


@router.get("/runs", response_model=List[BenchmarkRunResponse])
async def list_benchmark_runs(
    dataset_id: Optional[str] = Query(None, description="Filter runs by dataset ID")
):
    """Lists completed and active hallucination benchmark runs."""
    return await benchmark_service.list_benchmark_runs(dataset_id=dataset_id)


@router.get("/runs/{run_id}", response_model=BenchmarkRunResponse)
async def get_benchmark_run(run_id: str):
    """Retrieves full execution summary and aggregated scores for a benchmark run."""
    run = await benchmark_service.get_benchmark_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Benchmark run '{run_id}' not found.")
    return run


@router.get("/runs/{run_id}/results", response_model=List[EvaluationResultResponse])
async def get_run_results(
    run_id: str,
    verdict: Optional[str] = Query(None, description="Filter results by verdict: pass, warning, fail")
):
    """Retrieves test-case-level evaluation results with hallucination type breakdowns."""
    run = await benchmark_service.get_benchmark_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Benchmark run '{run_id}' not found.")
    return await benchmark_service.get_run_results(run_id=run_id, verdict=verdict)


@router.get("/compare/{dataset_id}", response_model=BenchmarkComparisonResponse)
async def compare_dataset_runs(dataset_id: str):
    """Generates cross-model benchmark comparison across runs for a given dataset."""
    dataset = await dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return await benchmark_service.compare_runs(dataset_id=dataset_id)
