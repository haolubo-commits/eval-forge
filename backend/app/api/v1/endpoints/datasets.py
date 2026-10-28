"""
Dataset and Test Case management endpoints for EvalForge.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.services.dataset_service import DatasetService
from app.schemas.dataset import (
    DatasetCreateRequest,
    DatasetResponse,
    TestCaseCreateRequest,
    TestCaseResponse
)

router = APIRouter(prefix="/datasets", tags=["Datasets"])
dataset_service = DatasetService()


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(req: DatasetCreateRequest):
    """Creates a new evaluation dataset."""
    return await dataset_service.create_dataset(req)


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Lists evaluation datasets ordered by creation time."""
    return await dataset_service.list_datasets(skip=skip, limit=limit)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str):
    """Retrieves dataset details and metadata."""
    dataset = await dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_200_OK)
async def delete_dataset(dataset_id: str):
    """Deletes an evaluation dataset and all associated test cases."""
    success = await dataset_service.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return {"message": f"Dataset '{dataset_id}' deleted successfully."}


@router.post("/{dataset_id}/cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def add_test_case(dataset_id: str, req: TestCaseCreateRequest):
    """Appends an individual test case with reference context to a dataset."""
    dataset = await dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return await dataset_service.add_test_case(dataset_id, req)


@router.get("/{dataset_id}/cases", response_model=List[TestCaseResponse])
async def list_test_cases(
    dataset_id: str,
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200)
):
    """Retrieves test cases belonging to a dataset with optional filtering."""
    dataset = await dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return await dataset_service.list_test_cases(
        dataset_id=dataset_id,
        test_type=test_type,
        difficulty=difficulty,
        skip=skip,
        limit=limit
    )


@router.delete("/{dataset_id}/cases/{test_case_id}", status_code=status.HTTP_200_OK)
async def delete_test_case(dataset_id: str, test_case_id: str):
    """Deletes a test case from a dataset."""
    success = await dataset_service.delete_test_case(test_case_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Test case '{test_case_id}' not found.")
    return {"message": f"Test case '{test_case_id}' deleted successfully."}
