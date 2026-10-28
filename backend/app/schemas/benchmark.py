"""
Pydantic API request & response schemas for Benchmarks and Evaluation Results.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.benchmark import (
    BenchmarkStatus,
    VerdictStatus,
    HallucinationType,
    MetricScores,
    BenchmarkSummary
)


class BenchmarkRunCreateRequest(BaseModel):
    dataset_id: str
    run_name: str = Field(..., min_length=2, max_length=100)
    target_model: str = Field("gpt-4o", description="Target model to benchmark")
    pipeline_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "chunk_size": 512,
            "top_k": 3,
            "temperature": 0.2,
            "system_prompt": "You are a factual RAG assistant. Strictly rely only on provided context."
        }
    )


class BenchmarkRunResponse(BaseModel):
    run_id: str
    dataset_id: str
    run_name: str
    target_model: str
    pipeline_config: Dict[str, Any]
    status: BenchmarkStatus
    summary: BenchmarkSummary
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class EvaluationResultResponse(BaseModel):
    result_id: str
    run_id: str
    test_case_id: str
    query: str
    generated_response: str
    retrieved_contexts: List[str]
    metrics: MetricScores
    verdict: VerdictStatus
    detected_hallucinations: List[HallucinationType]
    rationale: str
    latency_ms: float
    tokens_used: int
    created_at: datetime


class BenchmarkComparisonResponse(BaseModel):
    dataset_id: str
    total_runs: int
    runs: List[BenchmarkRunResponse] = Field(default_factory=list)
    comparison: Dict[str, Dict[str, float]]
