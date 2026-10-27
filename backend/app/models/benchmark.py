"""
Benchmark and Evaluation domain models for EvalForge.
Tracks test execution runs, metric scoring (faithfulness, groundedness, relevance),
and hallucination classification breakdowns.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BenchmarkStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VerdictStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class HallucinationType(str, Enum):
    NONE = "none"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    CONTRADICTION = "contradiction"
    ENTITY_DISTORTION = "entity_distortion"
    INVENTED_CITATION = "invented_citation"
    OVERCONFIDENT_SPECULATION = "overconfident_speculation"


class MetricScores(BaseModel):
    faithfulness: float = 1.0  # 0.0 - 1.0 (factual adherence to context)
    groundedness: float = 1.0  # 0.0 - 1.0 (sentence-level citation backing)
    relevance: float = 1.0     # 0.0 - 1.0 (alignment with user prompt)
    context_recall: float = 1.0  # 0.0 - 1.0 (context sufficiency)
    context_precision: float = 1.0  # 0.0 - 1.0 (signal to noise)
    hallucination_severity: float = 0.0  # 0.0 (clean) - 1.0 (severe hallucination)


class EvaluationResult(BaseModel):
    result_id: str
    run_id: str
    test_case_id: str
    query: str
    generated_response: str
    retrieved_contexts: List[str] = Field(default_factory=list)
    metrics: MetricScores = Field(default_factory=MetricScores)
    verdict: VerdictStatus = VerdictStatus.PASS
    detected_hallucinations: List[HallucinationType] = Field(default_factory=list)
    rationale: str = ""
    latency_ms: float = 0.0
    tokens_used: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BenchmarkSummary(BaseModel):
    total_cases: int = 0
    passed_count: int = 0
    warning_count: int = 0
    failed_count: int = 0
    hallucination_rate: float = 0.0
    mean_faithfulness: float = 0.0
    mean_groundedness: float = 0.0
    mean_relevance: float = 0.0
    mean_context_recall: float = 0.0
    mean_latency_ms: float = 0.0


class BenchmarkRun(BaseModel):
    run_id: str
    dataset_id: str
    run_name: str
    target_model: str
    pipeline_config: Dict[str, Any] = Field(default_factory=dict)
    status: BenchmarkStatus = BenchmarkStatus.QUEUED
    summary: BenchmarkSummary = Field(default_factory=BenchmarkSummary)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
