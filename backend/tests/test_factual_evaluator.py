"""
Unit tests for the FactualEvaluator service.
Tests faithfulness scoring, grounding coverage, number distortion detection,
unsupported claim identification, and negative constraint enforcement.
"""

import pytest
from app.services.factual_evaluator import FactualEvaluator
from app.models.benchmark import VerdictStatus, HallucinationType


@pytest.fixture
def evaluator():
    return FactualEvaluator()


def test_perfect_factual_entailment(evaluator):
    query = "What was the Q3 operating margin?"
    contexts = [
        "In Q3 FY2025, operating income reached $4.2B with an operating margin of 32.5%."
    ]
    response = "The operating margin was 32.5% with operating income of $4.2B."
    gt = "The operating margin was 32.5%."

    scores, verdict, hallucinations, rationale = evaluator.evaluate_response(
        query=query,
        generated_response=response,
        retrieved_contexts=contexts,
        ground_truth=gt,
        test_type="single_hop"
    )

    assert verdict == VerdictStatus.PASS
    assert scores.faithfulness >= 0.85
    assert scores.groundedness >= 0.85
    assert HallucinationType.NONE in hallucinations


def test_numeric_entity_distortion_detection(evaluator):
    query = "What was the reported revenue?"
    contexts = [
        "Annual gross revenue totaled $12.5 million for the fiscal period."
    ]
    # Distorted number: $125 million instead of $12.5 million
    distorted_response = "The annual gross revenue totaled $125 million for the fiscal period."

    scores, verdict, hallucinations, rationale = evaluator.evaluate_response(
        query=query,
        generated_response=distorted_response,
        retrieved_contexts=contexts,
        ground_truth="Annual gross revenue was $12.5 million.",
        test_type="adversarial"
    )

    assert HallucinationType.ENTITY_DISTORTION in hallucinations
    assert verdict in [VerdictStatus.WARNING, VerdictStatus.FAIL]
    assert "distortion" in rationale.lower()


def test_negative_constraint_compliance(evaluator):
    query = "Who was the lead architect on the secret project?"
    contexts = [
        "The project specifications list system requirements and encryption keys.",
        "Team members are not disclosed in public repositories."
    ]
    correct_refusal = "Based on the provided context, this information is not mentioned or available."

    scores, verdict, hallucinations, rationale = evaluator.evaluate_response(
        query=query,
        generated_response=correct_refusal,
        retrieved_contexts=contexts,
        ground_truth="Information not available.",
        test_type="negative_constraint"
    )

    assert verdict == VerdictStatus.PASS
    assert scores.faithfulness == 1.0
    assert "negative constraint" in rationale.lower()


def test_negative_constraint_violation_hallucination(evaluator):
    query = "What was the confidential settlement fee?"
    contexts = [
        "The settlement terms are strictly bound by non-disclosure agreements."
    ]
    # Fabricated answer when evidence is omitted
    fabricated_response = "The confidential settlement fee was negotiated at $5.8 million payable over 2 years."

    scores, verdict, hallucinations, rationale = evaluator.evaluate_response(
        query=query,
        generated_response=fabricated_response,
        retrieved_contexts=contexts,
        ground_truth="Information is strictly confidential.",
        test_type="negative_constraint"
    )

    assert HallucinationType.OVERCONFIDENT_SPECULATION in hallucinations
    assert verdict == VerdictStatus.FAIL
    assert scores.faithfulness <= 0.30


def test_unsupported_claim_detection(evaluator):
    query = "What is the primary cluster storage engine?"
    contexts = [
        "The cluster storage uses NVMe SSDs configured in RAID 10."
    ]
    # Response contains arbitrary ungrounded claims about quantum computing
    unsupported_response = "The system uses optical quantum processors manufactured in Zurich."

    scores, verdict, hallucinations, rationale = evaluator.evaluate_response(
        query=query,
        generated_response=unsupported_response,
        retrieved_contexts=contexts,
        ground_truth="NVMe SSDs in RAID 10.",
        test_type="single_hop"
    )

    assert HallucinationType.UNSUPPORTED_CLAIM in hallucinations
    assert verdict == VerdictStatus.FAIL
