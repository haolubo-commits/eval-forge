"""
Domain models for EvalForge: Datasets, Synthetic Generation, and Hallucination Benchmarks.
"""

from app.models.dataset import EvalDataset, TestCase, ContextChunk, TestType, DifficultyLevel
from app.models.generator import SyntheticGeneratorConfig, SyntheticJob, GenerationStrategy
from app.models.benchmark import (
    BenchmarkRun,
    BenchmarkStatus,
    EvaluationResult,
    VerdictStatus,
    MetricScores,
    HallucinationType
)

__all__ = [
    "EvalDataset",
    "TestCase",
    "ContextChunk",
    "TestType",
    "DifficultyLevel",
    "SyntheticGeneratorConfig",
    "SyntheticJob",
    "GenerationStrategy",
    "BenchmarkRun",
    "BenchmarkStatus",
    "EvaluationResult",
    "VerdictStatus",
    "MetricScores",
    "HallucinationType"
]
