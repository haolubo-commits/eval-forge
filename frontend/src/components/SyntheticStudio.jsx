import React, { useState } from 'react';
import { api } from '../services/api';

const PRESET_PASSAGES = {
  sec: "In Q3 2024, the enterprise distributed vector database achieved a 99.4% cache hit ratio across 12 million queries, lowering median latency from 182ms down to 14ms.",
  hnsw: "The neural semantic search engine utilizes HNSW graph indexing with M=16 and efConstruction=200, achieving 98.7% Recall@10 on the MS-MARCO passage benchmark.",
  compliance: "Under compliance standard ISO-27001, audit logs must be cryptographically hashed using SHA-256 and retained in write-once-read-many (WORM) storage for 7 years.",
  agent: "The multi-agent orchestration architecture limits maximum recursion depth to 15 iterations and enforces circuit breaker timeouts of 5000ms per external tool invocation."
};

export default function SyntheticStudio({
  activeDatasetId,
  onCasesGenerated
}) {
  const [strategy, setStrategy] = useState('qa_extraction');
  const [targetCount, setTargetCount] = useState(5);
  const [rawText, setRawText] = useState(PRESET_PASSAGES.sec);
  const [enableTraps, setEnableTraps] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationNotice, setGenerationNotice] = useState(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerationNotice(null);

    try {
      const payload = {
        dataset_id: activeDatasetId,
        strategy,
        target_count: Number(targetCount),
        include_hallucination_traps: enableTraps,
        raw_passages: [rawText]
      };
      const job = await api.generateSynthetic(payload);
      setGenerationNotice(`✓ Successfully synthesized ${job.generated_count || targetCount} test cases with ${strategy} strategy!`);
      if (onCasesGenerated) {
        onCasesGenerated();
      }
    } catch (err) {
      setGenerationNotice(`Error generating synthetic cases: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fade-in">
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        {/* Left Column: Generation Parameters */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700 }}>Synthetic Test Suite Studio</h3>
            <span className="badge badge-trap">Adversarial Engine</span>
          </div>

          <div className="form-group">
            <label className="form-label">Context Synthesis Strategy:</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {[
                { id: 'qa_extraction', label: 'QA Extraction', desc: 'Direct factual QA' },
                { id: 'multi_hop_reasoning', label: 'Multi-Hop Reasoning', desc: 'Cross-passage reasoning' },
                { id: 'counterfactual_perturbation', label: 'Adversarial Perturbation', desc: 'Entity & numeric shifts' },
                { id: 'negative_constraint_injection', label: 'Negative Constraint', desc: 'Omitted facts test' }
              ].map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setStrategy(s.id)}
                  style={{
                    padding: '12px',
                    borderRadius: 'var(--radius-sm)',
                    border: `1px solid ${strategy === s.id ? 'var(--accent-teal)' : 'var(--border-subtle)'}`,
                    background: strategy === s.id ? 'rgba(0, 229, 163, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                    color: strategy === s.id ? '#ffffff' : 'var(--text-muted)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: '13px', color: strategy === s.id ? 'var(--accent-teal)' : 'inherit' }}>
                    {s.label}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '3px' }}>
                    {s.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <label className="form-label" style={{ margin: 0 }}>Reference Corpus Passage:</label>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  type="button"
                  className="btn-secondary"
                  style={{ padding: '3px 8px', fontSize: '11px' }}
                  onClick={() => setRawText(PRESET_PASSAGES.sec)}
                >
                  SEC 10-K
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  style={{ padding: '3px 8px', fontSize: '11px' }}
                  onClick={() => setRawText(PRESET_PASSAGES.hnsw)}
                >
                  HNSW Index
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  style={{ padding: '3px 8px', fontSize: '11px' }}
                  onClick={() => setRawText(PRESET_PASSAGES.compliance)}
                >
                  ISO-27001
                </button>
              </div>
            </div>
            <textarea
              className="textarea-field"
              rows={4}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste raw unstructured documentation or context chunks..."
            />
          </div>

          <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginTop: '16px' }}>
            <div style={{ flex: 1 }}>
              <label className="form-label">Number of Test Cases:</label>
              <input
                type="number"
                className="input-field"
                min={1}
                max={25}
                value={targetCount}
                onChange={(e) => setTargetCount(e.target.value)}
              />
            </div>
            <div style={{ flex: 1.5, display: 'flex', alignItems: 'center', gap: '10px', marginTop: '20px' }}>
              <input
                type="checkbox"
                id="enable-traps"
                checked={enableTraps}
                onChange={(e) => setEnableTraps(e.target.checked)}
                style={{ width: '16px', height: '16px', accentColor: 'var(--accent-teal)' }}
              />
              <label htmlFor="enable-traps" style={{ fontSize: '13px', color: 'var(--text-main)', cursor: 'pointer' }}>
                Inject Adversarial Hallucination Traps
              </label>
            </div>
          </div>

          <div style={{ marginTop: '22px' }}>
            <button
              type="button"
              className="btn-primary"
              disabled={isGenerating}
              onClick={handleGenerate}
              style={{ width: '100%', justifyContent: 'center', padding: '12px' }}
            >
              {isGenerating ? (
                <>⏳ Synthesizing Test Cases...</>
              ) : (
                <>✨ Generate Synthetic QA Suite</>
              )}
            </button>
          </div>

          {generationNotice && (
            <div style={{
              marginTop: '16px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(0, 229, 163, 0.1)',
              border: '1px solid rgba(0, 229, 163, 0.3)',
              fontSize: '12px',
              color: 'var(--accent-teal)'
            }}>
              {generationNotice}
            </div>
          )}
        </div>

        {/* Right Column: Factual Attribution Engine Details */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '14px' }}>
            Attribution &amp; Trap Engine Pipeline
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '18px' }}>
            EvalForge applies systematic perturbations to benchmark LLM resilience against 4 common factual collapse triggers:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-teal)' }}>
              <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-main)' }}>
                1. Atomic Claim Entailment ($S_&#123;faith&#125;$)
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Decomposes model generation into atomic statements and performs exact and semantic token overlap against retrieved context.
              </div>
            </div>

            <div style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-violet)' }}>
              <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-main)' }}>
                2. Negative Constraint Resistance ($S_&#123;neg&#125;$)
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Asks for details intentionally missing from the reference passages. Evaluates whether the model accurately admits absence of evidence.
              </div>
            </div>

            <div style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-rose)' }}>
              <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-main)' }}>
                3. Entity &amp; Numeric Distortion Defense
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Swaps dollar amounts, dates, and technology names to catch models generating based on pretrained parametric memory instead of grounding.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
