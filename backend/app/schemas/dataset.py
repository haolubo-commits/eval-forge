"""
Pydantic API request & response schemas for Datasets and Test Cases.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.dataset import TestType, DifficultyLevel, ContextChunk
from app.models.generator import GenerationStrategy


class DatasetCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    domain: str = Field("general", description="Evaluation domain (e.g. finance, healthcare, legal, code)")
    description: str = ""
    tags: List[str] = Field(default_factory=list)


class DatasetResponse(BaseModel):
    dataset_id: str
    name: str
    domain: str
    description: str
    sample_count: int
    tags: List[str]
    version: str
    created_at: datetime
    updated_at: datetime


class TestCaseCreateRequest(BaseModel):
    query: str = Field(..., min_length=3)
    reference_contexts: List[ContextChunk] = Field(default_factory=list)
    ground_truth_answer: str = Field(..., min_length=1)
    test_type: TestType = TestType.SINGLE_HOP
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: List[str] = Field(default_factory=list)


class TestCaseResponse(BaseModel):
    test_case_id: str
    dataset_id: str
    query: str
    reference_contexts: List[ContextChunk]
    ground_truth_answer: str
    test_type: TestType
    difficulty: DifficultyLevel
    tags: List[str]
    created_at: datetime


class SyntheticGenerateRequest(BaseModel):
    dataset_id: str
    strategy: GenerationStrategy = GenerationStrategy.QA_EXTRACTION
    target_count: int = Field(5, ge=1, le=50)
    generator_model: str = "gpt-4o"
    temperature: float = Field(0.7, ge=0.0, le=1.5)
    include_hallucination_traps: bool = True
    trap_types: List[str] = Field(default_factory=lambda: ["entity_swap", "numeric_shift", "negative_constraint"])
    raw_passages: List[str] = Field(default_factory=list, description="Raw context text chunks to generate from")
