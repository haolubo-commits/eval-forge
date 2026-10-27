"""
Synthetic data generator domain models for EvalForge.
Configures synthetic test case generation pipelines, adversarial perturbations, and hallucination traps.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GenerationStrategy(str, Enum):
    QA_EXTRACTION = "qa_extraction"
    MULTI_HOP_REASONING = "multi_hop_reasoning"
    COUNTERFACTUAL_PERTURBATION = "counterfactual_perturbation"
    NEGATIVE_CONSTRAINT_INJECTION = "negative_constraint_injection"
    ADVERSARIAL_DISTRACTOR = "adversarial_distractor"


class SyntheticJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyntheticGeneratorConfig(BaseModel):
    generator_id: str
    strategy: GenerationStrategy = GenerationStrategy.QA_EXTRACTION
    generator_model: str = "gpt-4o"
    temperature: float = 0.7
    target_count: int = 10
    chunk_overlap: int = 50
    include_hallucination_traps: bool = True
    trap_types: List[str] = Field(
        default_factory=lambda: ["entity_swap", "numeric_shift", "temporal_inversion"]
    )
    prompt_template: Optional[str] = None


class SyntheticJob(BaseModel):
    job_id: str
    dataset_id: str
    config: SyntheticGeneratorConfig
    status: SyntheticJobStatus = SyntheticJobStatus.PENDING
    generated_count: int = 0
    total_requested: int = 10
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
