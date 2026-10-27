"""
API router aggregator for EvalForge v1.
Mounts dataset management, synthetic test generator, and hallucination benchmark endpoints.
"""

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/status", tags=["System"])
async def get_system_status():
    """Returns sub-system status for evaluation engine and synthesis workers."""
    return {
        "status": "ready",
        "supported_strategies": [
            "qa_extraction",
            "multi_hop_reasoning",
            "counterfactual_perturbation",
            "negative_constraint_injection",
            "adversarial_distractor"
        ],
        "hallucination_detectors": [
            "unsupported_claim",
            "contradiction",
            "entity_distortion",
            "invented_citation",
            "overconfident_speculation"
        ]
    }
