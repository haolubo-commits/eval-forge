"""
Unit tests for the SyntheticEngine generation service.
Tests counterfactual perturbations, question extraction, adversarial traps,
and negative constraint generation.
"""

import pytest
from app.services.synthetic_engine import SyntheticEngine
from app.models.dataset import TestType as TestTypeEnum, DifficultyLevel
from app.models.generator import GenerationStrategy


@pytest.fixture
def engine():
    return SyntheticEngine()


def test_default_sample_passages(engine):
    passages = engine._default_sample_passages()
    assert len(passages) >= 4
    for p in passages:
        assert isinstance(p, str)
        assert len(p) > 20


def test_synthesize_single_case_counterfactual(engine):
    passages = engine._default_sample_passages()
    case = engine._synthesize_single_case(
        dataset_id="ds_test",
        index=0,
        strategy=GenerationStrategy.COUNTERFACTUAL_PERTURBATION,
        passages=passages,
        include_traps=True,
        trap_types=["entity_swap", "numeric_distortion"]
    )

    assert case.dataset_id == "ds_test"
    assert len(case.query) > 5
    assert len(case.reference_contexts) >= 1
    assert case.test_type in [TestTypeEnum.ADVERSARIAL, TestTypeEnum.MULTI_HOP, TestTypeEnum.SINGLE_HOP]


def test_synthesize_single_case_negative_constraint(engine):
    passages = engine._default_sample_passages()
    case = engine._synthesize_single_case(
        dataset_id="ds_test",
        index=1,
        strategy=GenerationStrategy.NEGATIVE_CONSTRAINT_INJECTION,
        passages=passages,
        include_traps=True,
        trap_types=["unanswerable_missing_context"]
    )

    assert case.dataset_id == "ds_test"
    assert case.test_type == TestTypeEnum.NEGATIVE_CONSTRAINT
    assert "not contain" in case.ground_truth_answer.lower() or "not provided" in case.ground_truth_answer.lower()


def test_adversarial_trap_injection(engine):
    clean_text = "The system achieved 99.4% uptime across 12 regions with latency under 50ms."
    perturbed = engine._apply_entity_and_numeric_perturbation(clean_text)
    assert isinstance(perturbed, str)
    assert len(perturbed) > 0
    assert perturbed != clean_text
