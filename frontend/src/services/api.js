/**
 * API client for EvalForge backend with realistic mock fallbacks.
 */

const API_BASE = '/api/v1';

// Seed mock data for interactive preview
export const MOCK_DATASETS = [
  {
    dataset_id: "ds_fin_q3",
    name: "Enterprise Financial & Vector DB Benchmark",
    domain: "finance",
    description: "Evaluates factual numerical extraction, SEC filing adherence, and numeric perturbations.",
    sample_count: 8,
    tags: ["sec_10k", "vector_db", "adversarial"],
    created_at: "2026-10-27T10:00:00Z"
  },
  {
    dataset_id: "ds_rag_bio",
    name: "Biomedical Literature & Clinical Traps",
    domain: "biomedical",
    description: "Multi-hop clinical assertions, drug entity swapping, and unanswerable negative constraints.",
    sample_count: 6,
    tags: ["pubmed", "clinical_trials", "contraindications"],
    created_at: "2026-10-27T14:30:00Z"
  }
];

export const MOCK_TEST_CASES = [
  {
    test_case_id: "tc_01",
    dataset_id: "ds_fin_q3",
    query: "What is the primary cache hit ratio achieved by the vector database in Q3, and what was the median latency?",
    reference_contexts: [
      {
        chunk_id: "chk_101",
        title: "SEC Q3 Operational Metrics",
        text: "In Q3 2024, the enterprise distributed vector database achieved a 99.4% cache hit ratio across 12 million queries, lowering median latency from 182ms down to 14ms."
      }
    ],
    ground_truth_answer: "The vector database achieved a 99.4% cache hit ratio and lowered median latency to 14ms.",
    test_type: "single_hop",
    difficulty: "medium",
    tags: ["finance", "vector_cache"]
  },
  {
    test_case_id: "tc_02",
    dataset_id: "ds_fin_q3",
    query: "What regulatory fine was levied against the data infrastructure team in Q4?",
    reference_contexts: [
      {
        chunk_id: "chk_102",
        title: "Compliance Audit Excerpt",
        text: "Under compliance standard ISO-27001, audit logs must be cryptographically hashed using SHA-256 and retained in write-once-read-many (WORM) storage for 7 years."
      }
    ],
    ground_truth_answer: "The provided context does not contain any information regarding regulatory fines in Q4.",
    test_type: "negative_constraint",
    difficulty: "hard",
    tags: ["unanswerable", "negative_constraint"]
  },
  {
    test_case_id: "tc_03",
    dataset_id: "ds_fin_q3",
    query: "What is the reported recall score and HNSW construction parameter for the semantic search engine?",
    reference_contexts: [
      {
        chunk_id: "chk_103",
        title: "HNSW Benchmark Report",
        text: "The neural semantic search engine utilizes HNSW graph indexing with M=16 and efConstruction=200, achieving 98.7% Recall@10 on the MS-MARCO passage benchmark."
      }
    ],
    ground_truth_answer: "efConstruction is 200, achieving 98.7% Recall@10 on MS-MARCO.",
    test_type: "single_hop",
    difficulty: "easy",
    tags: ["hnsw", "ms_marco"]
  }
];

export const MOCK_EVAL_RESULTS = [
  {
    result_id: "res_01",
    run_id: "run_gpt4o",
    test_case_id: "tc_01",
    query: "What is the primary cache hit ratio achieved by the vector database in Q3, and what was the median latency?",
    generated_response: "According to the reference documentation, the enterprise distributed vector database achieved a 99.4% cache hit ratio and reduced median latency to 14ms.",
    retrieved_contexts: [
      "In Q3 2024, the enterprise distributed vector database achieved a 99.4% cache hit ratio across 12 million queries, lowering median latency from 182ms down to 14ms."
    ],
    metrics: {
      faithfulness: 1.0,
      groundedness: 1.0,
      relevance: 0.98,
      context_recall: 1.0,
      context_precision: 0.95,
      hallucination_severity: 0.0
    },
    verdict: "pass",
    detected_hallucinations: ["none"],
    rationale: "Response is strictly entailed by retrieved context without entity drift.",
    latency_ms: 210.4,
    tokens_used: 134
  },
  {
    result_id: "res_02",
    run_id: "run_custom_rag",
    test_case_id: "tc_02",
    query: "What regulatory fine was levied against the data infrastructure team in Q4?",
    generated_response: "The data infrastructure team was penalized $1.2M due to late audit disclosure in Q4.",
    retrieved_contexts: [
      "Under compliance standard ISO-27001, audit logs must be cryptographically hashed using SHA-256 and retained in write-once-read-many (WORM) storage for 7 years."
    ],
    metrics: {
      faithfulness: 0.15,
      groundedness: 0.20,
      relevance: 0.82,
      context_recall: 0.10,
      context_precision: 0.50,
      hallucination_severity: 0.85
    },
    verdict: "fail",
    detected_hallucinations: ["overconfident_speculation", "unsupported_claim"],
    rationale: "Model hallucinated details when reference context omitted the requested fact.",
    latency_ms: 380.2,
    tokens_used: 88
  }
];

export const MOCK_COMPARISON = {
  dataset_id: "ds_fin_q3",
  total_runs: 4,
  comparison: {
    "Claude 3.5 Sonnet": {
      faithfulness: 0.962,
      groundedness: 0.975,
      relevance: 0.941,
      hallucination_rate: 0.048,
      latency_ms: 195.2
    },
    "GPT-4o": {
      faithfulness: 0.948,
      groundedness: 0.952,
      relevance: 0.958,
      hallucination_rate: 0.062,
      latency_ms: 218.4
    },
    "DeepSeek V3": {
      faithfulness: 0.914,
      groundedness: 0.920,
      relevance: 0.932,
      hallucination_rate: 0.098,
      latency_ms: 164.0
    },
    "Custom RAG Pipeline": {
      faithfulness: 0.768,
      groundedness: 0.792,
      relevance: 0.840,
      hallucination_rate: 0.285,
      latency_ms: 312.8
    }
  }
};

export const api = {
  async fetchDatasets() {
    try {
      const res = await fetch(`${API_BASE}/datasets`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) return data;
      }
    } catch (e) {
      console.warn("Backend offline, using mock datasets:", e);
    }
    return MOCK_DATASETS;
  },

  async createDataset(datasetData) {
    try {
      const res = await fetch(`${API_BASE}/datasets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datasetData)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn("Using mock createDataset fallback");
    }
    return {
      dataset_id: `ds_${Date.now().toString(36)}`,
      ...datasetData,
      sample_count: 0,
      created_at: new Date().toISOString()
    };
  },

  async fetchTestCases(datasetId) {
    try {
      const res = await fetch(`${API_BASE}/datasets/${datasetId}/cases`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) return data;
      }
    } catch (e) {
      console.warn("Backend offline, using mock test cases:", e);
    }
    return MOCK_TEST_CASES;
  },

  async generateSynthetic(data) {
    try {
      const res = await fetch(`${API_BASE}/synthetic/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn("Synthetic generation fallback triggered:", e);
    }
    return {
      job_id: `job_${Date.now().toString(36)}`,
      dataset_id: data.dataset_id,
      status: "completed",
      generated_count: data.target_count || 5,
      created_at: new Date().toISOString()
    };
  },

  async runBenchmark(data) {
    try {
      const res = await fetch(`${API_BASE}/benchmarks/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn("Benchmark runner fallback triggered:", e);
    }
    return {
      run_id: `run_${Date.now().toString(36)}`,
      dataset_id: data.dataset_id,
      run_name: data.run_name,
      target_model: data.target_model,
      status: "completed",
      summary: {
        total_cases: 5,
        passed_count: 4,
        warning_count: 1,
        failed_count: 0,
        hallucination_rate: 0.12,
        mean_faithfulness: 0.942,
        mean_groundedness: 0.950,
        mean_relevance: 0.938,
        mean_context_recall: 0.960,
        mean_latency_ms: 198.5
      }
    };
  },

  async fetchBenchmarkComparison(datasetId) {
    try {
      const res = await fetch(`${API_BASE}/benchmarks/compare/${datasetId}`);
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn("Using mock comparison fallback:", e);
    }
    return MOCK_COMPARISON;
  },

  async fetchRunResults(runId) {
    try {
      const res = await fetch(`${API_BASE}/benchmarks/runs/${runId}/results`);
      if (res.ok) return await res.json();
    } catch (e) {
      console.warn("Using mock run results fallback:", e);
    }
    return MOCK_EVAL_RESULTS;
  }
};
