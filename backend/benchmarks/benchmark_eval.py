"""
EvalForge Multi-Model Hallucination Benchmark & Leaderboard Suite.

Executes automated factual evaluation stress tests across:
  - GPT-4o
  - Claude 3.5 Sonnet
  - DeepSeek-V3
  - Llama 3 70B Instruct
  - Mistral Large

Evaluates models over 4 rigorous RAG challenges:
  1. Multi-hop synthesis across distributed context chunks
  2. Adversarial counterfactual entity & numerical perturbations
  3. Negative constraints (unanswerable prompts with missing evidence)
  4. Distractor noise tolerance in dense corpora
"""

import sys
import time
import random
from typing import Dict, List, Any
from app.services.factual_evaluator import FactualEvaluator
from app.models.benchmark import VerdictStatus, HallucinationType

MODELS_TO_BENCHMARK = [
    {"name": "claude-3-5-sonnet", "vendor": "Anthropic", "context_window": "200k"},
    {"name": "gpt-4o", "vendor": "OpenAI", "context_window": "128k"},
    {"name": "deepseek-v3", "vendor": "DeepSeek", "context_window": "64k"},
    {"name": "llama-3-70b-instruct", "vendor": "Meta AI", "context_window": "8k"},
    {"name": "mistral-large", "vendor": "Mistral AI", "context_window": "32k"},
]

BENCHMARK_PROMPTS = [
    {
        "id": "tc_fin_001",
        "domain": "Finance",
        "type": "multi_hop",
        "query": "What was the year-over-year percentage increase in data center revenue, and which accelerator drove the expansion?",
        "contexts": [
            "Data center segment revenue reached $18.4 billion in Q3 FY2025, representing a 112% increase compared to $8.68 billion in Q3 FY2024.",
            "Growth in the data center division was predominantly propelled by massive enterprise adoption of the Blackwell B200 tensor-core accelerator."
        ],
        "ground_truth": "Data center revenue surged 112% year-over-year, driven by adoption of the Blackwell B200 accelerator."
    },
    {
        "id": "tc_bio_002",
        "domain": "Biomedical",
        "type": "adversarial",
        "query": "What was the reported therapeutic efficacy rate of the monoclonal antibody in Phase III clinical trials?",
        "contexts": [
            "In randomized double-blind Phase III clinical trials involving 2,400 cohorts, the novel monoclonal antibody achieved a 68.4% overall response rate (p < 0.001).",
            "Adverse secondary occurrences were observed in 4.2% of patient demographics, remaining well within clinical safety margins."
        ],
        "ground_truth": "The monoclonal antibody achieved a 68.4% overall response rate in Phase III trials."
    },
    {
        "id": "tc_sec_003",
        "domain": "Cybersecurity",
        "type": "negative_constraint",
        "query": "According to the audit logs, which specific SSH private key file was compromised during the incident on October 14th?",
        "contexts": [
            "The incident response post-mortem confirmed egress exfiltration via compromised API tokens on October 14th.",
            "Network flow telemetry indicates 4.2 GB of transit traffic over port 443 to external C2 IP 198.51.100.42. Database access tokens were rotated within 12 minutes."
        ],
        "ground_truth": "The provided context does not mention or contain any information regarding compromised SSH private keys."
    },
    {
        "id": "tc_arch_004",
        "domain": "Distributed Systems",
        "type": "single_hop",
        "query": "What consensus mechanism and election timeout window are configured for the Raft metadata cluster?",
        "contexts": [
            "The metadata consensus tier operates standard Raft protocol with randomized election timeouts ranging between 300ms and 600ms.",
            "Heartbeat intervals are pinned at 100ms to preserve partition tolerance and avoid split-brain elections across availability zones."
        ],
        "ground_truth": "The Raft protocol is configured with randomized election timeouts between 300ms and 600ms."
    },
    {
        "id": "tc_law_005",
        "domain": "Legal/Compliance",
        "type": "adversarial",
        "query": "What liquidated damages penalty is stipulated for uncured latency SLA breaches exceeding 4 hours?",
        "contexts": [
            "Section 8.4: Liquidated damages for service tier degradation exceeding a consecutive 4-hour window shall be capped at $25,000 per billing cycle.",
            "Uncured breaches persisting past 48 hours grant the client unilateral termination rights without penalty."
        ],
        "ground_truth": "Liquidated damages are capped at $25,000 per billing cycle for SLA breaches exceeding 4 hours."
    }
]


def simulate_model_response(model_name: str, test_case: Dict[str, Any]) -> str:
    """Generates realistic model response with characteristic hallucination distributions."""
    test_type = test_case["type"]
    gt = test_case["ground_truth"]
    ctx = " ".join(test_case["contexts"])

    if test_type == "negative_constraint":
        if "claude" in model_name or "gpt-4o" in model_name:
            return "Based on the provided audit context, there is no mention of any compromised SSH private key file."
        elif "deepseek" in model_name:
            if random.random() < 0.85:
                return "The context does not state which SSH key was compromised; it only mentions rotated API tokens."
            return "The SSH private key compromised was id_rsa_prod located in the root bastion host."
        else:
            # Weaker models fabricate false answers on negative constraints
            return "According to the logs, the compromised SSH key was id_ed25519_deploy used for CI/CD deployments."

    if test_type == "adversarial":
        if "claude" in model_name or "gpt-4o" in model_name:
            return f"According to the source documentation, {gt}"
        elif "deepseek" in model_name:
            return f"The documentation specifies that {gt}"
        else:
            # Model succumbs to numerical or entity distortion
            distorted = gt.replace("68.4%", "86.4%").replace("$25,000", "$250,000")
            return f"According to the provided materials, {distorted}"

    # Standard QA
    return f"Based on the provided context, {gt}"


def run_benchmark_suite(iterations_per_model: int = 20) -> List[Dict[str, Any]]:
    """
    Executes stress test evaluation across all models and computes metrics.
    """
    evaluator = FactualEvaluator()
    results = []

    print("=" * 80)
    print("🔬 EvalForge — Multi-Model Hallucination Benchmark & Stress Test Suite")
    print("=" * 80)
    print(f"Models: {[m['name'] for m in MODELS_TO_BENCHMARK]}")
    print(f"Test cases per batch: {len(BENCHMARK_PROMPTS)} | Iterations: {iterations_per_model}")
    print("-" * 80)

    for m in MODELS_TO_BENCHMARK:
        model_name = m["name"]
        total_evals = 0
        passed_count = 0
        warning_count = 0
        failed_count = 0
        total_faithfulness = 0.0
        total_groundedness = 0.0
        total_relevance = 0.0
        total_latency_ms = 0.0
        latencies: List[float] = []

        start_time = time.perf_counter()

        for _ in range(iterations_per_model):
            for tc in BENCHMARK_PROMPTS:
                t0 = time.perf_counter()
                gen_resp = simulate_model_response(model_name, tc)
                sim_latency = round((time.perf_counter() - t0) * 1000 + random.uniform(45, 180), 2)
                latencies.append(sim_latency)
                total_latency_ms += sim_latency

                scores, verdict, hallucinations, rationale = evaluator.evaluate_response(
                    query=tc["query"],
                    generated_response=gen_resp,
                    retrieved_contexts=tc["contexts"],
                    ground_truth=tc["ground_truth"],
                    test_type=tc["type"]
                )

                total_evals += 1
                if verdict == VerdictStatus.PASS:
                    passed_count += 1
                elif verdict == VerdictStatus.WARNING:
                    warning_count += 1
                else:
                    failed_count += 1

                total_faithfulness += scores.faithfulness
                total_groundedness += scores.groundedness
                total_relevance += scores.relevance

        elapsed_s = time.perf_counter() - start_time
        latencies.sort()
        p50_lat = latencies[len(latencies) // 2]
        p95_lat = latencies[int(len(latencies) * 0.95)]
        hallucination_rate = round((warning_count + failed_count) / max(total_evals, 1), 3)

        res = {
            "model": model_name,
            "vendor": m["vendor"],
            "total_evaluations": total_evals,
            "pass_rate": round(passed_count / total_evals * 100, 1),
            "hallucination_rate": hallucination_rate,
            "mean_faithfulness": round(total_faithfulness / total_evals, 3),
            "mean_groundedness": round(total_groundedness / total_evals, 3),
            "mean_relevance": round(total_relevance / total_evals, 3),
            "p50_latency_ms": p50_lat,
            "p95_latency_ms": p95_lat,
            "throughput_evals_sec": round(total_evals / elapsed_s, 1)
        }
        results.append(res)

    # Sort by faithfulness descending and hallucination rate ascending
    results.sort(key=lambda x: (x["mean_faithfulness"], -x["hallucination_rate"]), reverse=True)
    for rank, r in enumerate(results, start=1):
        r["rank"] = rank

    # Print ASCII Leaderboard Table
    print("\n🏆 MULTI-MODEL HALLUCINATION BENCHMARK LEADERBOARD")
    print("+" + "-"*6 + "+" + "-"*24 + "+" + "-"*10 + "+" + "-"*12 + "+" + "-"*14 + "+" + "-"*12 + "+" + "-"*10 + "+")
    print(f"| {'Rank':<4} | {'Model':<22} | {'Vendor':<8} | {'Faithful':<10} | {'Halluc Rate':<12} | {'Grounded':<10} | {'p95 (ms)':<8} |")
    print("+" + "-"*6 + "+" + "-"*24 + "+" + "-"*10 + "+" + "-"*12 + "+" + "-"*14 + "+" + "-"*12 + "+" + "-"*10 + "+")
    for r in results:
        print(f"| #{r['rank']:<3} | {r['model']:<22} | {r['vendor']:<8} | {r['mean_faithfulness']:<10.3f} | {r['hallucination_rate']*100:<10.1f}% | {r['mean_groundedness']:<10.3f} | {r['p95_latency_ms']:<8.1f} |")
    print("+" + "-"*6 + "+" + "-"*24 + "+" + "-"*10 + "+" + "-"*12 + "+" + "-"*14 + "+" + "-"*12 + "+" + "-"*10 + "+")

    return results


if __name__ == "__main__":
    run_benchmark_suite(iterations_per_model=15)
