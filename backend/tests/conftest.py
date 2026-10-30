"""
Pytest configuration and shared test fixtures for EvalForge.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.models.dataset import EvalDataset, TestCase, ContextChunk, TestType, DifficultyLevel
from app.models.benchmark import BenchmarkRun, BenchmarkStatus, BenchmarkSummary, MetricScores


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def sample_dataset():
    """Provides a sample evaluation dataset model instance."""
    return EvalDataset(
        dataset_id="ds_test_finance",
        name="Enterprise SEC Filing Benchmark",
        domain="Finance",
        description="Q3 FY2025 multi-hop earnings and balance sheet disclosures.",
        sample_count=12,
        tags=["10-K", "earnings", "rag-benchmark"],
        version="1.0.0"
    )


@pytest.fixture
def sample_test_case():
    """Provides a sample test case with verified reference contexts."""
    return TestCase(
        test_case_id="tc_sample_001",
        dataset_id="ds_test_finance",
        query="What was the net cloud segment revenue in Q2 and what was the YoY growth rate?",
        reference_contexts=[
            ContextChunk(
                chunk_id="chunk_001",
                title="Q2 Earnings Report",
                text="Cloud Infrastructure revenue expanded to $14.2 billion, registering 34% YoY growth.",
                source_uri="sec.gov/edgar/data/0001018724/q2-2025"
            ),
            ContextChunk(
                chunk_id="chunk_002",
                title="Segment Performance",
                text="Enterprise cloud subscriptions accounted for 78% of all recurring cloud contracts."
            )
        ],
        ground_truth_answer="Cloud segment revenue was $14.2 billion, achieving 34% YoY growth.",
        test_type=TestType.MULTI_HOP,
        difficulty=DifficultyLevel.MEDIUM,
        tags=["finance", "cloud", "revenue"]
    )


@pytest.fixture
def sample_benchmark_run():
    """Provides a sample completed benchmark run instance."""
    return BenchmarkRun(
        run_id="run_test_001",
        dataset_id="ds_test_finance",
        run_name="Claude 3.5 Sonnet Precision Run",
        target_model="claude-3-5-sonnet",
        pipeline_config={"temperature": 0.1, "top_k": 3},
        status=BenchmarkStatus.COMPLETED,
        summary=BenchmarkSummary(
            total_cases=10,
            passed_count=9,
            warning_count=1,
            failed_count=0,
            hallucination_rate=0.10,
            mean_faithfulness=0.92,
            mean_groundedness=0.94,
            mean_relevance=0.96,
            mean_latency_ms=115.4
        )
    )
