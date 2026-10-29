import React, { useState } from 'react';

export default function HallucinationMatrix({
  evalResults = [],
  testCases = []
}) {
  const [filterVerdict, setFilterVerdict] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCaseId, setSelectedCaseId] = useState(null);

  const filteredResults = evalResults.filter((r) => {
    if (filterVerdict !== 'all' && r.verdict !== filterVerdict) return false;
    if (searchQuery && !r.query.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="fade-in">
      {/* Controls & Filter Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['all', 'pass', 'warning', 'fail'].map((v) => (
            <button
              key={v}
              type="button"
              className={`tab-button ${filterVerdict === v ? 'active' : ''}`}
              onClick={() => setFilterVerdict(v)}
              style={{ textTransform: 'capitalize', padding: '6px 14px', fontSize: '13px' }}
            >
              {v === 'all' ? 'All Results' : v}
              {v === 'pass' && ' (✓)'}
              {v === 'fail' && ' (✕)'}
            </button>
          ))}
        </div>

        <div style={{ width: '320px' }}>
          <input
            type="text"
            className="input-field"
            placeholder="Search test case queries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Results Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {filteredResults.length === 0 ? (
          <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-dim)' }}>
            No test evaluations match the current filter.
          </div>
        ) : (
          filteredResults.map((item) => {
            const isPass = item.verdict === 'pass';
            const isFail = item.verdict === 'fail';
            const badgeClass = isPass ? 'badge-pass' : isFail ? 'badge-fail' : 'badge-warning';

            return (
              <div key={item.result_id} className="glass-card" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className={`badge ${badgeClass}`}>
                      {item.verdict.toUpperCase()}
                    </span>
                    <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                      ID: {item.test_case_id}
                    </span>
                    {item.detected_hallucinations?.map((h) => (
                      <span key={h} className="badge badge-trap">
                        {h}
                      </span>
                    ))}
                  </div>
                  <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                    ⏱️ {item.latency_ms}ms | 🪙 {item.tokens_used} tokens
                  </div>
                </div>

                <div style={{ marginBottom: '14px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>
                    EVALUATION QUERY / PROMPT:
                  </div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: '#ffffff' }}>
                    {item.query}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '14px' }}>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-teal)', marginBottom: '4px' }}>
                      RETRIEVED CONTEXT EVIDENCE:
                    </div>
                    <div className="code-preview" style={{ maxHeight: '110px' }}>
                      {item.retrieved_contexts?.join('\n---\n')}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '4px' }}>
                      TARGET MODEL GENERATED RESPONSE:
                    </div>
                    <div className="code-preview" style={{ maxHeight: '110px', color: isFail ? '#ff7979' : '#a5b4fc' }}>
                      {item.generated_response}
                    </div>
                  </div>
                </div>

                <div style={{
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  background: isFail ? 'rgba(255, 71, 87, 0.08)' : 'rgba(0, 229, 163, 0.06)',
                  border: `1px solid ${isFail ? 'rgba(255, 71, 87, 0.2)' : 'rgba(0, 229, 163, 0.2)'}`,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-main)' }}>
                    <strong>Verification Rationale:</strong> {item.rationale}
                  </div>
                  <div style={{ display: 'flex', gap: '12px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
                    <span>Faith: <strong>{((item.metrics?.faithfulness ?? 1) * 100).toFixed(0)}%</strong></span>
                    <span>Ground: <strong>{((item.metrics?.groundedness ?? 1) * 100).toFixed(0)}%</strong></span>
                    <span>Relev: <strong>{((item.metrics?.relevance ?? 1) * 100).toFixed(0)}%</strong></span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
