# 🔬 EvalForge — Synthetic Data & RAG Hallucination Benchmark

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%207.0-47A248.svg?style=flat&logo=mongodb)](https://www.mongodb.com)
[![Motor](https://img.shields.io/badge/Async%20Driver-Motor-green.svg?style=flat)](https://motor.readthedocs.io)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **EvalForge** is an enterprise-grade synthetic data generation engine and automated hallucination benchmark platform for Retrieval-Augmented Generation (RAG) and LLM pipelines. It dynamically synthesizes complex multi-hop question-answer suites, injects counterfactual adversarial traps and unanswerable negative constraints, and rigorously benchmarks target models on factual grounding, attribution precision, and hallucination resilience.

---

## 🏗️ Architecture & Hallucination Benchmark Pipeline

```mermaid
graph TD
    Corpus[Unstructured Raw Context Corpora] --> SynthEngine[EvalForge Synthesis Engine]
    
    subgraph Synthesis & Perturbation
        SynthEngine --> QAGen[Multi-Hop QA Extractor]
        SynthEngine --> TrapGen[Adversarial Hallucination Traps]
        TrapGen --> EntitySwap[Entity & Numeric Perturbation]
        TrapGen --> NegConstraint[Negative Constraint / Unanswerable]
        TrapGen --> Distractor[Irrelevant Distractor Injection]
    end

    QAGen --> TestSuites[("MongoDB: test_cases & eval_datasets")]
    EntitySwap --> TestSuites
    NegConstraint --> TestSuites
    Distractor --> TestSuites

    TestSuites --> BenchRunner[Benchmark Runner]
    TargetLLM[Target Model / RAG System] --> BenchRunner

    BenchRunner --> EvalEngine[Factual Verification Engine]
    subgraph Metric Scoring
        EvalEngine --> FaithScore["Faithfulness (Claim-to-Context Entailment)"]
        EvalEngine --> GroundScore["Groundedness (Sentence Citation Coverage)"]
        EvalEngine --> RelevScore["Answer Relevance (Prompt Alignment)"]
        EvalEngine --> HallucDetect["Hallucination Classifier & Severity Index"]
    end

    EvalEngine --> MongoResults[("MongoDB: eval_results & benchmark_runs")]
    MongoResults --> AnalyticsAPI[FastAPI Analytics & Aggregation Engine]
    AnalyticsAPI --> CockpitUI[React Evaluation Cockpit]
```

---

## 🌟 Key Features (4-Day Sprint Roadmap)

- [x] **Day 1: Scaffolding & Architecture**: MongoDB 7.0 async schemas, Motor connection pooling, Pydantic v2 domain models (datasets, test cases, hallucination traps, benchmark runs), application configuration, and FastAPI lifecycle.
- [ ] **Day 2: Core Logic & Evaluation APIs**: Synthetic question generation pipeline, adversarial counterfactual perturbations, multi-dimensional factual scoring algorithms (faithfulness, groundedness, relevance, negative constraint resilience), and benchmark runner endpoints.
- [ ] **Day 3: Frontend UI / Evaluation Cockpit**: Modern React 18 dashboard featuring synthetic dataset builder, hallucination detection matrix, metric radar charts, side-by-side run comparisons, and citation attribution inspector.
- [ ] **Day 4: Benchmarks, Seed Datasets & Docker Compose**: Automated integration test suites, real-world finance & biomedical seed benchmarks, multi-model evaluation leaderboard (GPT-4o vs Claude 3.5 vs DeepSeek), and containerized Docker Compose deployment.

---

## 📐 Hallucination Taxonomy & Evaluation Metrics

EvalForge evaluates RAG generation across 5 formal dimensions:

| Metric | Target Dimension | Objective | Failure Mode Detected |
| :--- | :--- | :--- | :--- |
| **Faithfulness** | $S_{\text{faith}} \in [0, 1]$ | Every atomic claim in the answer must be logically entailed by retrieved context | Unsupported claims, factual fabrications |
| **Groundedness** | $S_{\text{ground}} \in [0, 1]$ | Proportion of sentences with verifiable citation attribution | Free-floating or unbacked assertions |
| **Relevance** | $S_{\text{relev}} \in [0, 1]$ | Semantic alignment between the user question and the answer | Evasive answers, topical drift |
| **Negative Constraint Resilience** | $S_{\text{neg}} \in [0, 1]$ | Accurately declaring ignorance when context lacks sufficient evidence | Overconfident speculation, false premises |
| **Hallucination Severity** | $H_{\text{sev}} \in [0, 1]$ | Aggregate impact score ($0 = \text{clean}$, $1 = \text{catastrophic hallucination}$) | Critical contradictions, entity distortions |

---

## 🚀 Quickstart & Development

### 1. Requirements
- Python 3.11+
- MongoDB 7.0+ (running on `localhost:27017` or via Docker)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run FastAPI Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`
