"""
Synthetic test case generation engine for EvalForge.
Generates multi-hop QA pairs, counterfactual perturbations, and adversarial hallucination traps
from raw context corpora.
"""

from typing import List, Dict, Any, Optional
import re
import uuid
import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.dataset import TestCase, ContextChunk, TestType, DifficultyLevel
from app.models.generator import (
    SyntheticGeneratorConfig,
    SyntheticJob,
    SyntheticJobStatus,
    GenerationStrategy
)
from app.schemas.dataset import SyntheticGenerateRequest


class SyntheticEngine:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is not None:
            return self._db
        return get_database()

    async def generate_test_cases(self, req: SyntheticGenerateRequest) -> SyntheticJob:
        """Runs the synthetic test case generation pipeline for a dataset."""
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        config = SyntheticGeneratorConfig(
            generator_id=f"gen_{uuid.uuid4().hex[:8]}",
            strategy=req.strategy,
            generator_model=req.generator_model,
            temperature=req.temperature,
            target_count=req.target_count,
            include_hallucination_traps=req.include_hallucination_traps,
            trap_types=req.trap_types
        )
        job = SyntheticJob(
            job_id=job_id,
            dataset_id=req.dataset_id,
            config=config,
            status=SyntheticJobStatus.RUNNING,
            generated_count=0,
            total_requested=req.target_count,
            created_at=datetime.utcnow()
        )

        if self.db is not None:
            await self.db["generator_jobs"].insert_one(job.model_dump())

        # Synthesize test cases from passages
        passages = req.raw_passages if req.raw_passages else self._default_sample_passages()
        generated_cases: List[TestCase] = []

        try:
            for idx in range(req.target_count):
                case = self._synthesize_single_case(
                    dataset_id=req.dataset_id,
                    index=idx,
                    strategy=req.strategy,
                    passages=passages,
                    include_traps=req.include_hallucination_traps,
                    trap_types=req.trap_types
                )
                generated_cases.append(case)

            # Insert generated cases into database
            if self.db is not None and generated_cases:
                await self.db["test_cases"].insert_many([c.model_dump() for c in generated_cases])
                # Update dataset sample count
                total_cases = await self.db["test_cases"].count_documents({"dataset_id": req.dataset_id})
                await self.db["eval_datasets"].update_one(
                    {"dataset_id": req.dataset_id},
                    {"$set": {"sample_count": total_cases, "updated_at": datetime.utcnow()}}
                )

            # Update job as completed
            job.status = SyntheticJobStatus.COMPLETED
            job.generated_count = len(generated_cases)
            job.completed_at = datetime.utcnow()

            if self.db is not None:
                await self.db["generator_jobs"].update_one(
                    {"job_id": job_id},
                    {"$set": {
                        "status": SyntheticJobStatus.COMPLETED.value,
                        "generated_count": len(generated_cases),
                        "completed_at": job.completed_at
                    }}
                )

        except Exception as e:
            job.status = SyntheticJobStatus.FAILED
            job.error_message = str(e)
            if self.db is not None:
                await self.db["generator_jobs"].update_one(
                    {"job_id": job_id},
                    {"$set": {
                        "status": SyntheticJobStatus.FAILED.value,
                        "error_message": str(e)
                    }}
                )

        return job

    def _synthesize_single_case(
        self,
        dataset_id: str,
        index: int,
        strategy: GenerationStrategy,
        passages: List[str],
        include_traps: bool,
        trap_types: List[str]
    ) -> TestCase:
        """Synthesizes an individual QA pair with context and ground truth."""
        case_id = f"tc_syn_{uuid.uuid4().hex[:10]}"
        selected_passage = passages[index % len(passages)]
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', selected_passage) if s.strip()]

        if strategy == GenerationStrategy.MULTI_HOP_REASONING and len(passages) >= 2:
            second_passage = passages[(index + 1) % len(passages)]
            chunk1 = ContextChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                title="Primary Evidence A",
                text=selected_passage,
                token_count=len(selected_passage.split())
            )
            chunk2 = ContextChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                title="Corroborating Evidence B",
                text=second_passage,
                token_count=len(second_passage.split())
            )
            query = f"Synthesize findings across Evidence A and Evidence B regarding the core factors: {sentences[0] if sentences else 'key metric'}?"
            answer = f"Evidence A indicates that {sentences[0] if sentences else 'the primary condition holds'}, while Evidence B extends this by establishing the subsequent outcome."
            test_type = TestType.MULTI_HOP
            difficulty = DifficultyLevel.HARD
            contexts = [chunk1, chunk2]

        elif strategy == GenerationStrategy.NEGATIVE_CONSTRAINT_INJECTION:
            chunk = ContextChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                title="Restricted Context",
                text=selected_passage,
                token_count=len(selected_passage.split())
            )
            query = f"What specific regulatory penalty was imposed on the organization in Q4 according to the passage?"
            answer = "The provided context does not contain any information regarding regulatory penalties in Q4."
            test_type = TestType.NEGATIVE_CONSTRAINT
            difficulty = DifficultyLevel.HARD
            contexts = [chunk]

        elif strategy == GenerationStrategy.COUNTERFACTUAL_PERTURBATION and include_traps:
            perturbed_text = self._apply_entity_and_numeric_perturbation(selected_passage)
            chunk = ContextChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                title="Perturbed Baseline",
                text=perturbed_text,
                token_count=len(perturbed_text.split())
            )
            query = f"Based strictly on the provided text, what is the exact reported metric or outcome?"
            answer = f"According to the provided text, the reported metric is: {sentences[0] if sentences else 'as stated in context'}."
            test_type = TestType.ADVERSARIAL
            difficulty = DifficultyLevel.HARD
            contexts = [chunk]

        else:  # Default QA_EXTRACTION
            chunk = ContextChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                title="Factual Source Passage",
                text=selected_passage,
                token_count=len(selected_passage.split())
            )
            focus_sentence = sentences[0] if sentences else selected_passage
            query = f"According to the documentation, what is the primary conclusion regarding: {focus_sentence[:60]}...?"
            answer = focus_sentence
            test_type = TestType.SINGLE_HOP
            difficulty = DifficultyLevel.MEDIUM
            contexts = [chunk]

        return TestCase(
            test_case_id=case_id,
            dataset_id=dataset_id,
            query=query,
            reference_contexts=contexts,
            ground_truth_answer=answer,
            test_type=test_type,
            difficulty=difficulty,
            tags=["synthetic", strategy.value],
            created_at=datetime.utcnow()
        )

    def _apply_entity_and_numeric_perturbation(self, text: str) -> str:
        """Perturbs numbers and named entities to generate adversarial traps."""
        # Shift numbers by randomized multipliers
        def shift_num(match):
            val = float(match.group(0))
            return f"{round(val * 1.5, 2):g}"

        perturbed = re.sub(r'\b\d+(\.\d+)?\b', shift_num, text)
        # Swap known tech entities if present
        replacements = {
            "OpenAI": "Anthropic",
            "PostgreSQL": "MongoDB",
            "PyTorch": "TensorFlow",
            "FastAPI": "Flask",
            "99.9%": "84.2%"
        }
        for k, v in replacements.items():
            if k in perturbed:
                perturbed = perturbed.replace(k, v)
        return perturbed

    def _default_sample_passages(self) -> List[str]:
        """Provides default domain passages if no raw corpus is supplied."""
        return [
            "In Q3 2024, the enterprise distributed vector database achieved a 99.4% cache hit ratio across 12 million queries, lowering median latency from 182ms down to 14ms.",
            "The neural semantic search engine utilizes HNSW graph indexing with M=16 and efConstruction=200, achieving 98.7% Recall@10 on the MS-MARCO passage benchmark.",
            "Under compliance standard ISO-27001, audit logs must be cryptographically hashed using SHA-256 and retained in write-once-read-many (WORM) storage for 7 years.",
            "The multi-agent orchestration architecture limits maximum recursion depth to 15 iterations and enforces circuit breaker timeouts of 5000ms per external tool invocation."
        ]
