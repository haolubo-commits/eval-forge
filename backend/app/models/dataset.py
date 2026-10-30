"""
Dataset and TestCase domain models for EvalForge.
Represents evaluation corpora, multi-hop question-answer test suites, and reference contexts.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TestType(str, Enum):
    __test__ = False
    SINGLE_HOP = "single_hop"
    MULTI_HOP = "multi_hop"
    ADVERSARIAL = "adversarial"
    NEGATIVE_CONSTRAINT = "negative_constraint"
    DISTRACTOR_RESISTANT = "distractor_resistant"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ContextChunk(BaseModel):
    chunk_id: str
    title: str = ""
    text: str
    source_uri: Optional[str] = None
    token_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    __test__ = False
    test_case_id: str
    dataset_id: str
    query: str
    reference_contexts: List[ContextChunk] = Field(default_factory=list)
    ground_truth_answer: str
    test_type: TestType = TestType.SINGLE_HOP
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EvalDataset(BaseModel):
    dataset_id: str
    name: str
    domain: str
    description: str = ""
    sample_count: int = 0
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
