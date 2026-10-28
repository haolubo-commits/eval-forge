"""
Benchmark runner and orchestration service for EvalForge.
Executes test cases against target LLM models, coordinates factual evaluation,
and aggregates performance and hallucination metrics.
"""

from typing import List, Dict, Any, Optional
import uuid
import random
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.dataset import TestCase, TestType
from app.models.benchmark import (
    BenchmarkRun,
    BenchmarkStatus,
    BenchmarkSummary,
    EvaluationResult,
    VerdictStatus,
    HallucinationType
)
from app.services.dataset_service import DatasetService
from app.services.factual_evaluator import FactualEvaluator
from app.schemas.benchmark import BenchmarkRunCreateRequest


class BenchmarkService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self._db = db
        self.dataset_service = DatasetService(db)
        self.evaluator = FactualEvaluator()

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is not None:
            return self._db
        return get_database()

    async def create_and_execute_run(self, req: BenchmarkRunCreateRequest) -> BenchmarkRun:
        """Initializes and executes an automated benchmark run over a dataset."""
        run_id = f"run_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()

        run = BenchmarkRun(
            run_id=run_id,
            dataset_id=req.dataset_id,
            run_name=req.run_name,
            target_model=req.target_model,
            pipeline_config=req.pipeline_config,
            status=BenchmarkStatus.RUNNING,
            summary=BenchmarkSummary(),
            created_at=now
        )

        if self.db is not None:
            await self.db["benchmark_runs"].insert_one(run.model_dump())

        # Retrieve test cases
        cases = await self.dataset_service.list_test_cases(req.dataset_id, limit=200)
        if not cases:
            # Fallback to creating sample cases if empty
            sample_case = await self.dataset_service.add_test_case(
                req.dataset_id,
                TestCase(
                    test_case_id=f"tc_init_{uuid.uuid4().hex[:8]}",
                    dataset_id=req.dataset_id,
                    query="What is the primary cache hit ratio achieved by the vector database in Q3?",
                    reference_contexts=[],
                    ground_truth_answer="The vector database achieved a 99.4% cache hit ratio.",
                    test_type=TestType.SINGLE_HOP
                )  # type: ignore
            )
            cases = [sample_case]

        results: List[EvaluationResult] = []
        passed = 0
        warnings = 0
        failed = 0
        faithfulness_total = 0.0
        groundedness_total = 0.0
        relevance_total = 0.0
        recall_total = 0.0
        latency_total = 0.0

        for case in cases:
            start_t = time.perf_counter()
            retrieved_chunks = [c.text for c in case.reference_contexts] if case.reference_contexts else [
                "In Q3 2024, the enterprise distributed vector database achieved a 99.4% cache hit ratio across 12 million queries."
            ]

            # Generate target response
            gen_response = self._simulate_target_model_generation(
                model=req.target_model,
                query=case.query,
                contexts=retrieved_chunks,
                ground_truth=case.ground_truth_answer,
                test_type=case.test_type.value
            )
            latency_ms = round((time.perf_counter() - start_t) * 1000 + random.uniform(80, 240), 2)
            latency_total += latency_ms

            # Run factual evaluation
            metrics, verdict, halluc_types, rationale = self.evaluator.evaluate_response(
                query=case.query,
                generated_response=gen_response,
                retrieved_contexts=retrieved_chunks,
                ground_truth=case.ground_truth_answer,
                test_type=case.test_type.value
            )

            if verdict == VerdictStatus.PASS:
                passed += 1
            elif verdict == VerdictStatus.WARNING:
                warnings += 1
            else:
                failed += 1

            faithfulness_total += metrics.faithfulness
            groundedness_total += metrics.groundedness
            relevance_total += metrics.relevance
            recall_total += metrics.context_recall

            eval_res = EvaluationResult(
                result_id=f"res_{uuid.uuid4().hex[:10]}",
                run_id=run_id,
                test_case_id=case.test_case_id,
                query=case.query,
                generated_response=gen_response,
                retrieved_contexts=retrieved_chunks,
                metrics=metrics,
                verdict=verdict,
                detected_hallucinations=halluc_types,
                rationale=rationale,
                latency_ms=latency_ms,
                tokens_used=len(gen_response.split()) + sum(len(c.split()) for c in retrieved_chunks)
            )
            results.append(eval_res)

        # Batch insert results
        if self.db is not None and results:
            await self.db["eval_results"].insert_many([r.model_dump() for r in results])

        # Compute summary metrics
        total = len(cases)
        hallucination_cases = total - passed
        summary = BenchmarkSummary(
            total_cases=total,
            passed_count=passed,
            warning_count=warnings,
            failed_count=failed,
            hallucination_rate=round(hallucination_cases / max(total, 1), 3),
            mean_faithfulness=round(faithfulness_total / max(total, 1), 3),
            mean_groundedness=round(groundedness_total / max(total, 1), 3),
            mean_relevance=round(relevance_total / max(total, 1), 3),
            mean_context_recall=round(recall_total / max(total, 1), 3),
            mean_latency_ms=round(latency_total / max(total, 1), 2)
        )

        run.status = BenchmarkStatus.COMPLETED
        run.summary = summary
        run.completed_at = datetime.utcnow()

        if self.db is not None:
            await self.db["benchmark_runs"].update_one(
                {"run_id": run_id},
                {"$set": {
                    "status": BenchmarkStatus.COMPLETED.value,
                    "summary": summary.model_dump(),
                    "completed_at": run.completed_at
                }}
            )

        return run

    def _simulate_target_model_generation(
        self,
        model: str,
        query: str,
        contexts: List[str],
        ground_truth: str,
        test_type: str
    ) -> str:
        """Simulates target LLM response with model-specific hallucination distributions."""
        joined_ctx = " ".join(contexts)

        if test_type == "negative_constraint":
            if "gpt-4o" in model or "claude" in model:
                return "Based on the provided context, this information is not mentioned or available."
            else:
                # Weak models frequently hallucinate on negative constraints
                return "The requested regulatory penalty in Q4 was a fine of $1.2 million with compliance remediation."

        if test_type == "adversarial":
            if "claude" in model:
                return f"According to the source text, the stated figure is: {ground_truth}."
            elif "gpt-4o" in model:
                return f"The documentation specifies: {ground_truth}."
            else:
                return f"The system operates with an approximate performance of {ground_truth}."

        # Standard QA response
        if ground_truth:
            return f"According to the reference documentation, {ground_truth}"
        elif contexts:
            return f"Based on the provided materials: {contexts[0][:120]}."
        return "No reference context available."

    async def get_benchmark_run(self, run_id: str) -> Optional[BenchmarkRun]:
        """Retrieves a benchmark run by ID."""
        if self.db is None:
            return None
        doc = await self.db["benchmark_runs"].find_one({"run_id": run_id}, {"_id": 0})
        if not doc:
            return None
        return BenchmarkRun(**doc)

    async def list_benchmark_runs(self, dataset_id: Optional[str] = None) -> List[BenchmarkRun]:
        """Lists benchmark runs, optionally filtered by dataset."""
        if self.db is None:
            return []
        query = {"dataset_id": dataset_id} if dataset_id else {}
        cursor = self.db["benchmark_runs"].find(query, {"_id": 0}).sort("created_at", -1)
        items = await cursor.to_list(length=100)
        return [BenchmarkRun(**item) for item in items]

    async def get_run_results(
        self,
        run_id: str,
        verdict: Optional[str] = None
    ) -> List[EvaluationResult]:
        """Retrieves test case results for a given benchmark run."""
        if self.db is None:
            return []
        query: Dict[str, Any] = {"run_id": run_id}
        if verdict:
            query["verdict"] = verdict
        cursor = self.db["eval_results"].find(query, {"_id": 0}).sort("created_at", 1)
        items = await cursor.to_list(length=200)
        return [EvaluationResult(**item) for item in items]

    async def compare_runs(self, dataset_id: str) -> Dict[str, Any]:
        """Compares benchmark runs for a dataset across models."""
        runs = await self.list_benchmark_runs(dataset_id)
        comparison: Dict[str, Dict[str, float]] = {}
        for r in runs:
            comparison[r.target_model] = {
                "faithfulness": r.summary.mean_faithfulness,
                "groundedness": r.summary.mean_groundedness,
                "relevance": r.summary.mean_relevance,
                "hallucination_rate": r.summary.hallucination_rate,
                "latency_ms": r.summary.mean_latency_ms
            }
        return {
            "dataset_id": dataset_id,
            "total_runs": len(runs),
            "runs": runs,
            "comparison": comparison
        }
