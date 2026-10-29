# 🔬 EvalForge Frontend — Evaluation & Hallucination Cockpit

Interactive React dashboard and synthetic benchmarking workbench for evaluating RAG systems, detecting hallucinations, and scoring factual grounding across LLMs.

---

## 🚀 Key Features

1. **Hallucination Matrix & Case Inspector (`<HallucinationMatrix />`)**:
   - Filterable evaluation matrix by verdict: `PASS` (entailed), `WARNING` (minor drift), `FAIL` (hallucination detected).
   - Side-by-side prompt, retrieved context evidence, model response, and verification rationale.
   - Categorized hallucination badges: `unsupported_claim`, `entity_distortion`, `overconfident_speculation`.
   - Sentence-level attribution coverage scores ($S_{\text{faith}}$, $S_{\text{ground}}$, $S_{\text{relev}}$).

2. **Synthetic Data & Adversarial Studio (`<SyntheticStudio />`)**:
   - Automated QA suite generation workbench with customizable synthesis strategies (`qa_extraction`, `multi_hop_reasoning`, `counterfactual_perturbation`, `negative_constraint_injection`).
   - Domain passage presets: SEC 10-K Financial Filings, HNSW Indexing Benchmarks, ISO-27001 Compliance.
   - Adversarial hallucination trap injection (entity swap, numeric drift, unanswerable queries).

3. **Macro KPI Status Bar (`<MetricsBar />`)**:
   - Aggregate Faithfulness ($S_{\text{faith}}$) with color gauge.
   - Groundedness Citation Index ($S_{\text{ground}}$).
   - Answer Relevance score ($S_{\text{relev}}$).
   - Hallucination Rate (% of runs triggering fabrications).
   - Mean evaluation cycle latency (ms).

4. **Multi-Model Benchmark Cockpit (`<BenchmarkCockpit />`)**:
   - Automated benchmark runner with configurable top_k, temperature, and system instructions.
   - Cross-model performance leaderboard comparing **Claude 3.5 Sonnet**, **GPT-4o**, **DeepSeek V3**, and **Custom RAG**.
   - Side-by-side comparison cards and metric progress tracks.

---

## 🛠️ Tech Stack

- **Framework**: React 18 (Functional components & hooks)
- **Bundler & Dev Server**: Vite 5
- **Styling**: Vanilla Modern Glassmorphic CSS (CSS variables, backdrop-filter, radial gradients)
- **Typography**: Plus Jakarta Sans & JetBrains Mono

---

## 🏃 Getting Started

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

The application will be accessible at `http://localhost:5173`.
