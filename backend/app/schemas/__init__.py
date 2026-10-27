"""
Pydantic API request and response schemas for EvalForge.
"""

from app.schemas.dataset import (
    DatasetCreateRequest,
    DatasetResponse,
    TestCaseCreateRequest,
    TestCaseResponse,
    SyntheticGenerateRequest
)
from app.schemas.benchmark import (
    BenchmarkRunCreateRequest,
    BenchmarkRunResponse,
    EvaluationResultResponse,
    BenchmarkComparisonResponse
)

__all__ = [
    "DatasetCreateRequest",
    "DatasetResponse",
    "TestCaseCreateRequest",
    "TestCaseResponse",
    "SyntheticGenerateRequest",
    "BenchmarkRunCreateRequest",
    "BenchmarkRunResponse",
    "EvaluationResultResponse",
    "BenchmarkComparisonResponse"
]
