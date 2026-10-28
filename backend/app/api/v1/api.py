"""
API router aggregator for EvalForge v1.
Mounts dataset management, synthetic test generator, and hallucination benchmark endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints.datasets import router as datasets_router
from app.api.v1.endpoints.synthetic import router as synthetic_router
from app.api.v1.endpoints.benchmarks import router as benchmarks_router

api_router = APIRouter()

# Mount feature routers
api_router.include_router(datasets_router)
api_router.include_router(synthetic_router)
api_router.include_router(benchmarks_router)


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
