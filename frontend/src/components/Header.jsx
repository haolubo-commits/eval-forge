import React from 'react';

export default function Header({
  activeModel,
  onModelChange,
  datasets,
  activeDatasetId,
  onDatasetChange
}) {
  return (
    <header className="header-container">
      <div className="brand-section">
        <div className="brand-logo-icon">🔬</div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="brand-title">EvalForge</span>
            <span className="brand-badge">RAG Hallucination Benchmark</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Synthetic Test Suite Generator & Factual Attribution Verification
          </div>
        </div>
      </div>

      <div className="header-controls">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>Active Dataset:</span>
          <select
            className="select-control"
            value={activeDatasetId}
            onChange={(e) => onDatasetChange(e.target.value)}
          >
            {datasets.map((d) => (
              <option key={d.dataset_id} value={d.dataset_id}>
                {d.name} ({d.sample_count || 0} cases)
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>Target Model:</span>
          <select
            className="select-control"
            value={activeModel}
            onChange={(e) => onModelChange(e.target.value)}
          >
            <option value="gpt-4o">GPT-4o (OpenAI)</option>
            <option value="claude-3-5-sonnet">Claude 3.5 Sonnet (Anthropic)</option>
            <option value="deepseek-chat">DeepSeek V3 (DeepSeek)</option>
            <option value="custom-rag-pipeline">Custom Enterprise RAG</option>
          </select>
        </div>

        <div className="status-pill">
          <div className="status-dot"></div>
          <span>Engine Active</span>
        </div>
      </div>
    </header>
  );
}
