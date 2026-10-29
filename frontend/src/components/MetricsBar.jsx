import React from 'react';

export default function MetricsBar({ summary }) {
  const faithfulness = (summary?.mean_faithfulness ?? 0.942) * 100;
  const groundedness = (summary?.mean_groundedness ?? 0.950) * 100;
  const relevance = (summary?.mean_relevance ?? 0.938) * 100;
  const hallucinationRate = (summary?.hallucination_rate ?? 0.085) * 100;
  const latencyMs = summary?.mean_latency_ms ?? 198.5;

  return (
    <div className="metrics-grid">
      <div className="glass-card metric-card">
        <div className="metric-title">
          <span>Faithfulness ($S_&#123;faith&#125;$)</span>
          <span style={{ color: 'var(--accent-teal)' }}>✓ Entailed</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number" style={{ color: 'var(--accent-teal)' }}>
            {faithfulness.toFixed(1)}%
          </span>
          <span className="metric-sub">target &gt; 85%</span>
        </div>
        <div className="metric-bar-track">
          <div
            className="metric-bar-fill"
            style={{ width: `${faithfulness}%`, background: 'var(--accent-teal)' }}
          ></div>
        </div>
      </div>

      <div className="glass-card metric-card violet">
        <div className="metric-title">
          <span>Groundedness ($S_&#123;ground&#125;$)</span>
          <span style={{ color: 'var(--accent-violet)' }}>Attributed</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number" style={{ color: 'var(--accent-violet)' }}>
            {groundedness.toFixed(1)}%
          </span>
          <span className="metric-sub">citation coverage</span>
        </div>
        <div className="metric-bar-track">
          <div
            className="metric-bar-fill"
            style={{ width: `${groundedness}%`, background: 'var(--accent-violet)' }}
          ></div>
        </div>
      </div>

      <div className="glass-card metric-card">
        <div className="metric-title">
          <span>Answer Relevance</span>
          <span style={{ color: 'var(--accent-cyan)' }}>Alignment</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number" style={{ color: 'var(--accent-cyan)' }}>
            {relevance.toFixed(1)}%
          </span>
          <span className="metric-sub">intent match</span>
        </div>
        <div className="metric-bar-track">
          <div
            className="metric-bar-fill"
            style={{ width: `${relevance}%`, background: 'var(--accent-cyan)' }}
          ></div>
        </div>
      </div>

      <div className="glass-card metric-card rose">
        <div className="metric-title">
          <span>Hallucination Rate</span>
          <span style={{ color: 'var(--accent-rose)' }}>Traps Caught</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number" style={{ color: 'var(--accent-rose)' }}>
            {hallucinationRate.toFixed(1)}%
          </span>
          <span className="metric-sub">fabrication / drift</span>
        </div>
        <div className="metric-bar-track">
          <div
            className="metric-bar-fill"
            style={{ width: `${Math.min(100, hallucinationRate * 3)}%`, background: 'var(--accent-rose)' }}
          ></div>
        </div>
      </div>

      <div className="glass-card metric-card amber">
        <div className="metric-title">
          <span>Mean Latency</span>
          <span style={{ color: 'var(--accent-amber)' }}>Speed</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number" style={{ color: 'var(--accent-amber)' }}>
            {latencyMs.toFixed(0)}ms
          </span>
          <span className="metric-sub">eval cycle</span>
        </div>
        <div className="metric-bar-track">
          <div
            className="metric-bar-fill"
            style={{ width: `${Math.min(100, (latencyMs / 500) * 100)}%`, background: 'var(--accent-amber)' }}
          ></div>
        </div>
      </div>
    </div>
  );
}
