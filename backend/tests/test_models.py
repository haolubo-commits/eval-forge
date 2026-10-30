"""
Unit tests for EvalForge domain models and schemas.
"""

import pytest
from app.models.dataset import EvalDataset, TestCase as TestCaseModel, ContextChunk, TestType as TestTypeEnum, DifficultyLevel
from app.models.benchmark import (
    BenchmarkRun,
    BenchmarkStatus,
    VerdictStatus,
    HallucinationType,
    MetricScores,
    EvaluationResult
)
from app.models.generator import SyntheticJob, SyntheticJobStatus, GenerationStrategy


def test_eval_dataset_initialization():
    ds = EvalDataset(
        dataset_id="ds_123",
        name="Biomedical Drug Trial QA",
        domain="Biomedical",
        description="Clinical trial outcome corpus",
        sample_count=25
    )
    assert ds.dataset_id == "ds_123"
    assert ds.domain == "Biomedical"
    assert ds.version == "1.0.0"
    assert ds.sample_count == 25


def test_test_case_validation():
    chunk = ContextChunk(
        chunk_id="chk_1",
        title="Abstract",
        text="Target molecule binds to KRAS G12D with sub-nanomolar affinity."
    )
    case = TestCaseModel(
        test_case_id="tc_kras_1",
        dataset_id="ds_123",
        query="What is the binding affinity to KRAS G12D?",
        reference_contexts=[chunk],
        ground_truth_answer="Sub-nanomolar affinity.",
        test_type=TestTypeEnum.SINGLE_HOP,
        difficulty=DifficultyLevel.EASY
    )
    assert case.test_case_id == "tc_kras_1"
    assert len(case.reference_contexts) == 1
    assert case.test_type == TestTypeEnum.SINGLE_HOP
    assert case.difficulty == DifficultyLevel.EASY


def test_metric_scores_defaults():
    scores = MetricScores()
    assert scores.faithfulness == 1.0
    assert scores.groundedness == 1.0
    assert scores.hallucination_severity == 0.0


def test_evaluation_result_model():
    res = EvaluationResult(
        result_id="res_001",
        run_id="run_001",
        test_case_id="tc_001",
        query="Verify cluster status",
        generated_response="The cluster is healthy and operational.",
        retrieved_contexts=["All 3 nodes report status READY."],
        metrics=MetricScores(faithfulness=0.95, groundedness=0.98),
        verdict=VerdictStatus.PASS,
        detected_hallucinations=[HallucinationType.NONE],
        rationale="Entailed by node status report.",
        latency_ms=120.5
    )
    assert res.verdict == VerdictStatus.PASS
    assert res.latency_ms == 120.5
    assert HallucinationType.NONE in res.detected_hallucinations


def test_benchmark_status_enums():
    assert BenchmarkStatus.RUNNING.value == "running"
    assert BenchmarkStatus.COMPLETED.value == "completed"
    assert VerdictStatus.WARNING.value == "warning"
    assert HallucinationType.ENTITY_DISTORTION.value == "entity_distortion"
    assert GenerationStrategy.COUNTERFACTUAL_PERTURBATION.value == "counterfactual_perturbation"
