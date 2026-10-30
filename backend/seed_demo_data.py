"""
seed_demo_data.py — Rich Dataset Seeder for EvalForge.
Populates realistic enterprise evaluation datasets (Finance, Oncology, Distributed Systems),
multi-hop test cases with counterfactual traps, and historical multi-model benchmark runs
(Claude 3.5 Sonnet, GPT-4o, DeepSeek-V3, Llama 3 70B).
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.dataset import EvalDataset, TestCase, ContextChunk, TestType, DifficultyLevel
from app.models.benchmark import (
    BenchmarkRun,
    BenchmarkStatus,
    BenchmarkSummary,
    EvaluationResult,
    VerdictStatus,
    HallucinationType,
    MetricScores
)

SAMPLE_DATASETS = [
    {
        "dataset_id": "ds_sec_finance_2025",
        "name": "SEC 10-K & Q3 Earnings Disclosures",
        "domain": "Finance & Capital Markets",
        "description": "Enterprise SEC filings, GAAP reconciliation disclosures, segment EBIT margin attribution, and debt covenants.",
        "tags": ["finance", "10-k", "gaap", "earnings", "multi-hop"]
    },
    {
        "dataset_id": "ds_oncology_trials",
        "name": "Phase III Oncology Clinical Trials",
        "domain": "Biomedical & Clinical Science",
        "description": "Double-blind randomized oncology trial outcomes, primary endpoints, overall survival rates, and adverse event profiles.",
        "tags": ["biomedical", "fda-trials", "oncology", "grounding", "counterfactual"]
    },
    {
        "dataset_id": "ds_k8s_dist_systems",
        "name": "Kubernetes & Raft Consensus Failures",
        "domain": "Distributed Infrastructure",
        "description": "Post-mortem incident reports, split-brain partition telemetry, Raft quorum leader elections, and eBPF tracing logs.",
        "tags": ["distributed-systems", "raft", "kubernetes", "incident-response", "sre"]
    }
]

TEST_CASES_FINANCE = [
    {
        "test_case_id": "tc_fin_01",
        "query": "What was the year-over-year revenue growth rate in the Data Center segment, and what percentage of operating income did it represent?",
        "ground_truth_answer": "Data Center segment revenue grew 112% year-over-year to $18.4 billion, representing 64.2% of total consolidated operating income.",
        "test_type": TestType.MULTI_HOP,
        "difficulty": DifficultyLevel.HARD,
        "contexts": [
            {
                "chunk_id": "chk_fin_01",
                "title": "Segment Revenue Breakdown",
                "text": "Data Center segment revenue surged 112% year-over-year to $18.4 billion in Q3 FY2025, driven by enterprise accelerated computing clusters."
            },
            {
                "chunk_id": "chk_fin_02",
                "title": "Consolidated Operating Income Reconciliation",
                "text": "Total consolidated operating income for the period stood at $28.66 billion, with Data Center operations contributing $18.40 billion (64.2% of total)."
            }
        ]
    },
    {
        "test_case_id": "tc_fin_02",
        "query": "What was the interest coverage covenant ratio required under the 2028 Credit Facility?",
        "ground_truth_answer": "The credit facility requires the borrower to maintain a minimum consolidated interest coverage ratio of 3.50 to 1.00.",
        "test_type": TestType.ADVERSARIAL,
        "difficulty": DifficultyLevel.MEDIUM,
        "contexts": [
            {
                "chunk_id": "chk_fin_03",
                "title": "Credit Agreement Note 7",
                "text": "Under the terms of the 2028 Senior Revolving Facility, the company must maintain a consolidated interest coverage ratio of not less than 3.50 to 1.00 at the close of each fiscal quarter."
            }
        ]
    },
    {
        "test_case_id": "tc_fin_03",
        "query": "According to Note 14, what was the estimated monetary fine levied by the SEC for algorithmic trading violations?",
        "ground_truth_answer": "The provided context does not mention or disclose any SEC monetary fines or algorithmic trading investigations.",
        "test_type": TestType.NEGATIVE_CONSTRAINT,
        "difficulty": DifficultyLevel.HARD,
        "contexts": [
            {
                "chunk_id": "chk_fin_04",
                "title": "Note 14 — Legal Contingencies",
                "text": "The company is subject to customary commercial litigation arising in ordinary course. Routine patent infringement suits are deemed immaterial to financial position."
            }
        ]
    }
]

TEST_CASES_ONCOLOGY = [
    {
        "test_case_id": "tc_med_01",
        "query": "What was the progression-free survival (PFS) hazard ratio observed in the experimental arm versus standard of care?",
        "ground_truth_answer": "The experimental combination demonstrated a median PFS hazard ratio of 0.62 (95% CI: 0.51-0.75, p < 0.001) compared to control.",
        "test_type": TestType.SINGLE_HOP,
        "difficulty": DifficultyLevel.MEDIUM,
        "contexts": [
            {
                "chunk_id": "chk_med_01",
                "title": "Phase III Trial Efficacy Endpoints",
                "text": "In the intention-to-treat population of 1,180 patients, median progression-free survival reached 14.8 months in the experimental arm versus 8.2 months in standard of care, yielding an unstratified hazard ratio of 0.62 (95% CI: 0.51-0.75, p < 0.001)."
            }
        ]
    },
    {
        "test_case_id": "tc_med_02",
        "query": "What dose reduction protocol was mandated upon patient development of Grade 3 hepatotoxicity?",
        "ground_truth_answer": "The protocol requires withholding the study drug until ALT/AST normalizes to Grade <= 1, followed by a permanent 25% dose reduction to 150mg daily.",
        "test_type": TestType.MULTI_HOP,
        "difficulty": DifficultyLevel.HARD,
        "contexts": [
            {
                "chunk_id": "chk_med_02",
                "title": "Adverse Reaction Management Guidelines",
                "text": "For treatment-emergent Grade 3 elevated transaminases (ALT/AST > 5x ULN), study treatment must be withheld immediately until resolution to Grade 1 or baseline."
            },
            {
                "chunk_id": "chk_med_03",
                "title": "Dose Level Titration Schedule",
                "text": "Upon transaminase recovery following Grade 3 hepatotoxicity, re-initiation is permitted at Dose Level -1 (150 mg once daily, representing a 25% dose reduction from starting dose 200 mg)."
            }
        ]
    }
]

TEST_CASES_INFRA = [
    {
        "test_case_id": "tc_sre_01",
        "query": "What caused the split-brain partition in the etcd Raft cluster on October 18th?",
        "ground_truth_answer": "A silent asymmetric network drop dropped heartbeat RPCs across Zone B, triggering election timeout loops while Zone A and C formed a 2-node quorum.",
        "test_type": TestType.ADVERSARIAL,
        "difficulty": DifficultyLevel.HARD,
        "contexts": [
            {
                "chunk_id": "chk_sre_01",
                "title": "Incident Post-Mortem #482",
                "text": "At 03:14 UTC, a top-of-rack switch misconfiguration caused asymmetric packet drops of gRPC traffic on port 2380 between Zone B and the remaining cluster. Zone B missed leader heartbeats and repeatedly triggered election candidates with elevated terms."
            }
        ]
    }
]


async def seed():
    print(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
    db = client[settings.DATABASE_NAME]

    # Clean existing seed collections
    print("Clearing collections...")
    for col in ["eval_datasets", "test_cases", "benchmark_runs", "eval_results", "generator_jobs"]:
        await db[col].delete_many({})

    # 1. Seed Datasets
    print("Seeding evaluation datasets...")
    for ds_info in SAMPLE_DATASETS:
        dataset = EvalDataset(
            dataset_id=ds_info["dataset_id"],
            name=ds_info["name"],
            domain=ds_info["domain"],
            description=ds_info["description"],
            sample_count=0,
            tags=ds_info["tags"],
            version="1.0.0",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        await db["eval_datasets"].insert_one(dataset.model_dump())

    # 2. Seed Test Cases
    print("Seeding test cases...")
    all_cases = [
        ("ds_sec_finance_2025", TEST_CASES_FINANCE),
        ("ds_oncology_trials", TEST_CASES_ONCOLOGY),
        ("ds_k8s_dist_systems", TEST_CASES_INFRA),
    ]

    for ds_id, cases in all_cases:
        for c in cases:
            contexts = [
                ContextChunk(
                    chunk_id=ctx["chunk_id"],
                    title=ctx["title"],
                    text=ctx["text"],
                    token_count=len(ctx["text"].split())
                )
                for ctx in c["contexts"]
            ]
            tc = TestCase(
                test_case_id=c["test_case_id"],
                dataset_id=ds_id,
                query=c["query"],
                reference_contexts=contexts,
                ground_truth_answer=c["ground_truth_answer"],
                test_type=c["test_type"],
                difficulty=c["difficulty"],
                tags=["verified", ds_id]
            )
            await db["test_cases"].insert_one(tc.model_dump())

        # Update dataset sample count
        count = await db["test_cases"].count_documents({"dataset_id": ds_id})
        await db["eval_datasets"].update_one(
            {"dataset_id": ds_id},
            {"$set": {"sample_count": count}}
        )

    # 3. Seed Benchmark Runs & Evaluation Results
    print("Seeding multi-model benchmark runs (GPT-4o, Claude 3.5 Sonnet, DeepSeek-V3, Llama 3 70B)...")
    models_config = [
        {"model": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet Production Eval", "faith": 0.945, "ground": 0.960, "relev": 0.980, "halluc_rate": 0.055, "lat": 118.4, "pass": 18, "warn": 1, "fail": 1},
        {"model": "gpt-4o", "name": "GPT-4o Omni Factual Benchmark", "faith": 0.925, "ground": 0.940, "relev": 0.970, "halluc_rate": 0.075, "lat": 134.2, "pass": 17, "warn": 2, "fail": 1},
        {"model": "deepseek-v3", "name": "DeepSeek-V3 MoE Stress Run", "faith": 0.890, "ground": 0.910, "relev": 0.940, "halluc_rate": 0.110, "lat": 98.6, "pass": 16, "warn": 3, "fail": 1},
        {"model": "llama-3-70b-instruct", "name": "Llama 3 70B Open Weights Eval", "faith": 0.815, "ground": 0.830, "relev": 0.890, "halluc_rate": 0.185, "lat": 156.8, "pass": 14, "warn": 4, "fail": 2},
    ]

    for m in models_config:
        run_id = f"run_{uuid.uuid4().hex[:10]}"
        run = BenchmarkRun(
            run_id=run_id,
            dataset_id="ds_sec_finance_2025",
            run_name=m["name"],
            target_model=m["model"],
            pipeline_config={"temperature": 0.2, "top_k": 3},
            status=BenchmarkStatus.COMPLETED,
            summary=BenchmarkSummary(
                total_cases=20,
                passed_count=m["pass"],
                warning_count=m["warn"],
                failed_count=m["fail"],
                hallucination_rate=m["halluc_rate"],
                mean_faithfulness=m["faith"],
                mean_groundedness=m["ground"],
                mean_relevance=m["relev"],
                mean_context_recall=0.92,
                mean_latency_ms=m["lat"]
            ),
            created_at=datetime.utcnow() - timedelta(hours=6),
            completed_at=datetime.utcnow() - timedelta(hours=5, minutes=58)
        )
        await db["benchmark_runs"].insert_one(run.model_dump())

        # Seed sample evaluation result
        eval_res = EvaluationResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            test_case_id="tc_fin_01",
            query="What was the year-over-year revenue growth rate in the Data Center segment?",
            generated_response=f"According to the SEC 10-K filing, Data Center segment revenue surged 112% year-over-year to $18.4 billion.",
            retrieved_contexts=["Data Center segment revenue surged 112% year-over-year to $18.4 billion in Q3 FY2025."],
            metrics=MetricScores(
                faithfulness=m["faith"],
                groundedness=m["ground"],
                relevance=m["relev"],
                hallucination_severity=round(1.0 - m["faith"], 3)
            ),
            verdict=VerdictStatus.PASS,
            detected_hallucinations=[HallucinationType.NONE],
            rationale="All extracted figures are fully verified and entailed by retrieved chunks.",
            latency_ms=m["lat"],
            tokens_used=184
        )
        await db["eval_results"].insert_one(eval_res.model_dump())

    client.close()
    print("✅ Demo datasets, test cases, and multi-model benchmark runs successfully seeded!")


if __name__ == "__main__":
    asyncio.run(seed())
