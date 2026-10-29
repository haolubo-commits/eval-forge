import React, { useState } from 'react';
import { api } from '../services/api';

export default function BenchmarkCockpit({
  activeDatasetId,
  activeModel,
  comparisonData,
  onRunCompleted
}) {
  const [isRunning, setIsRunning] = useState(false);
  const [runName, setRunName] = useState('Production RAG Evaluation');
  const [topK, setTopK] = useState(3);
  const [temperature, setTemperature] = useState(0.2);
  const [runMessage, setRunMessage] = useState(null);

  const handleStartRun = async () => {
    setIsRunning(true);
    setRunMessage(null);

    try {
      const payload = {
        dataset_id: activeDatasetId,
        run_name: runName,
        target_model: activeModel,
        pipeline_config: {
          chunk_size: 512,
          top_k: Number(topK),
          temperature: Number(temperature)
        }
      };
      const res = await api.runBenchmark(payload);
      setRunMessage(`✓ Benchmark completed! Passed: ${res.summary.passed_count}/${res.summary.total_cases} cases (Mean Faithfulness: ${(res.summary.mean_faithfulness * 100).toFixed(1)}%)`);
      if (onRunCompleted) {
        onRunCompleted(res);
      }
    } catch (e) {
      setRunMessage(`Benchmark run failed: ${e.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const models = comparisonData?.comparison ? Object.entries(comparisonData.comparison) : [];

  return (
    <div className="fade-in">
      {/* Benchmark Trigger Controls */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 700 }}>Benchmark Execution Engine</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Runs dataset test cases against target LLM judge and verifies factual grounding in real-time.
            </p>
          </div>
          <span className="badge badge-pass">Automated Evaluation</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr auto', gap: '16px', alignItems: 'flex-end' }}>
          <div>
            <label className="form-label">Run Name / Experiment Identifier:</label>
            <input
              type="text"
              className="input-field"
              value={runName}
              onChange={(e) => setRunName(e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Top-K Context Chunks:</label>
            <select className="select-control" style={{ width: '100%' }} value={topK} onChange={(e) => setTopK(e.target.value)}>
              <option value="1">Top-1 Chunk</option>
              <option value="3">Top-3 Chunks (Standard)</option>
              <option value="5">Top-5 Chunks</option>
            </select>
          </div>

          <div>
            <label className="form-label">Temperature:</label>
            <input
              type="number"
              step="0.1"
              min="0.0"
              max="1.0"
              className="input-field"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
            />
          </div>

          <div>
            <button
              type="button"
              className="btn-primary"
              disabled={isRunning}
              onClick={handleStartRun}
              style={{ padding: '10px 22px' }}
            >
              {isRunning ? '⏳ Executing Benchmark...' : '🚀 Run Benchmark'}
            </button>
          </div>
        </div>

        {runMessage && (
          <div style={{
            marginTop: '16px',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(0, 229, 163, 0.1)',
            border: '1px solid rgba(0, 229, 163, 0.3)',
            fontSize: '13px',
            color: 'var(--accent-teal)'
          }}>
            {runMessage}
          </div>
        )}
      </div>

      {/* Cross-Model Comparison Matrix */}
      <div>
        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '6px' }}>
          Multi-Model Hallucination &amp; Grounding Leaderboard
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Comparative evaluation results across frontier models on identical synthetic adversarial test suites:
        </p>

        <div className="comparison-grid">
          {models.map(([modelName, stats]) => {
            const faithPct = (stats.faithfulness * 100).toFixed(1);
            const groundPct = (stats.groundedness * 100).toFixed(1);
            const relevPct = (stats.relevance * 100).toFixed(1);
            const hallucPct = (stats.hallucination_rate * 100).toFixed(1);
            const isTopModel = modelName.includes('Claude') || modelName.includes('GPT-4o');

            return (
              <div key={modelName} className="glass-card model-card">
                <div className="model-header">
                  <div className="model-name" style={{ color: isTopModel ? 'var(--accent-teal)' : '#ffffff' }}>
                    {modelName}
                  </div>
                  {modelName.includes('Claude') && (
                    <span className="badge badge-pass">#1 Grounding</span>
                  )}
                  {modelName.includes('DeepSeek') && (
                    <span className="badge badge-warning">#1 Throughput</span>
                  )}
                </div>

                <div className="stat-row">
                  <span className="stat-label">Faithfulness ($S_&#123;faith&#125;$)</span>
                  <span className="stat-val" style={{ color: stats.faithfulness > 0.9 ? 'var(--accent-teal)' : stats.faithfulness > 0.8 ? 'var(--accent-amber)' : 'var(--accent-rose)' }}>
                    {faithPct}%
                  </span>
                </div>

                <div className="stat-row">
                  <span className="stat-label">Sentence Groundedness</span>
                  <span className="stat-val" style={{ color: 'var(--accent-violet)' }}>
                    {groundPct}%
                  </span>
                </div>

                <div className="stat-row">
                  <span className="stat-label">Answer Relevance</span>
                  <span className="stat-val" style={{ color: 'var(--accent-cyan)' }}>
                    {relevPct}%
                  </span>
                </div>

                <div className="stat-row">
                  <span className="stat-label">Hallucination Rate</span>
                  <span className="stat-val" style={{ color: stats.hallucination_rate < 0.1 ? 'var(--accent-teal)' : 'var(--accent-rose)' }}>
                    {hallucPct}%
                  </span>
                </div>

                <div className="stat-row">
                  <span className="stat-label">Average Latency</span>
                  <span className="stat-val" style={{ color: 'var(--text-muted)' }}>
                    {stats.latency_ms.toFixed(0)}ms
                  </span>
                </div>

                <div style={{ marginTop: '6px' }}>
                  <div className="metric-bar-track">
                    <div
                      className="metric-bar-fill"
                      style={{
                        width: `${faithPct}%`,
                        background: stats.faithfulness > 0.9 ? 'var(--accent-teal)' : stats.faithfulness > 0.8 ? 'var(--accent-amber)' : 'var(--accent-rose)'
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
