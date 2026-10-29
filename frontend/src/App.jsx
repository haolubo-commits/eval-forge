import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsBar from './components/MetricsBar';
import HallucinationMatrix from './components/HallucinationMatrix';
import SyntheticStudio from './components/SyntheticStudio';
import BenchmarkCockpit from './components/BenchmarkCockpit';
import { api, MOCK_DATASETS } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('matrix');
  const [activeModel, setActiveModel] = useState('gpt-4o');
  const [datasets, setDatasets] = useState(MOCK_DATASETS);
  const [activeDatasetId, setActiveDatasetId] = useState(MOCK_DATASETS[0].dataset_id);
  const [testCases, setTestCases] = useState([]);
  const [evalResults, setEvalResults] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load initial data
  const loadData = async (datasetId) => {
    setLoading(true);
    try {
      const dsList = await api.fetchDatasets();
      setDatasets(dsList);

      const targetId = datasetId || (dsList[0] ? dsList[0].dataset_id : activeDatasetId);
      setActiveDatasetId(targetId);

      const [cases, results, comparison] = await Promise.all([
        api.fetchTestCases(targetId),
        api.fetchRunResults("run_gpt4o"),
        api.fetchBenchmarkComparison(targetId)
      ]);

      setTestCases(cases);
      setEvalResults(results);
      setComparisonData(comparison);
    } catch (e) {
      console.error("Error loading application state:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDatasetChange = (id) => {
    setActiveDatasetId(id);
    loadData(id);
  };

  const handleRunCompleted = (runData) => {
    // Refresh results and comparison
    loadData(activeDatasetId);
  };

  return (
    <div className="app-container">
      <Header
        activeModel={activeModel}
        onModelChange={setActiveModel}
        datasets={datasets}
        activeDatasetId={activeDatasetId}
        onDatasetChange={handleDatasetChange}
      />

      <main className="main-content">
        {/* Top Macro Metrics Bar */}
        <MetricsBar summary={comparisonData?.comparison?.[activeModel] || {}} />

        {/* Navigation Tabs */}
        <div className="tabs-navigation">
          <button
            type="button"
            className={`tab-button ${activeTab === 'matrix' ? 'active' : ''}`}
            onClick={() => setActiveTab('matrix')}
          >
            📊 Hallucination Matrix &amp; Attributions
          </button>
          <button
            type="button"
            className={`tab-button ${activeTab === 'synthetic' ? 'active' : ''}`}
            onClick={() => setActiveTab('synthetic')}
          >
            🧪 Synthetic Studio &amp; Traps
          </button>
          <button
            type="button"
            className={`tab-button ${activeTab === 'benchmarks' ? 'active' : ''}`}
            onClick={() => setActiveTab('benchmarks')}
          >
            🏆 Benchmark Cockpit &amp; Leaderboard
          </button>
        </div>

        {/* Tab Views */}
        {activeTab === 'matrix' && (
          <HallucinationMatrix
            evalResults={evalResults}
            testCases={testCases}
          />
        )}

        {activeTab === 'synthetic' && (
          <SyntheticStudio
            activeDatasetId={activeDatasetId}
            onCasesGenerated={() => loadData(activeDatasetId)}
          />
        )}

        {activeTab === 'benchmarks' && (
          <BenchmarkCockpit
            activeDatasetId={activeDatasetId}
            activeModel={activeModel}
            comparisonData={comparisonData}
            onRunCompleted={handleRunCompleted}
          />
        )}
      </main>
    </div>
  );
}
