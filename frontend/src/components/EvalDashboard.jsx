import React, { useState, useEffect } from 'react';

const EvalDashboard = () => {
  const [evals, setEvals] = useState([]);
  const [accuracy, setAccuracy] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvalData();
  }, []);

  const fetchEvalData = async () => {
    try {
      const [evalsRes, accuracyRes, perfRes] = await Promise.all([
        fetch('/api/evals/recent?limit=20'),
        fetch('/api/evals/accuracy'),
        fetch('/api/analytics/performance')
      ]);
      
      const evalsData = await evalsRes.json();
      const accuracyData = await accuracyRes.json();
      const perfData = await perfRes.json();
      
      setEvals(evalsData);
      setAccuracy(accuracyData);
      setPerformance(perfData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching eval data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading evaluation data...</div>;
  }

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Classification Accuracy</h3>
          <div className="value">
            {accuracy ? `${(accuracy.classification_accuracy * 100).toFixed(0)}%` : 'N/A'}
          </div>
          <div className="change">Based on {accuracy?.sample_size || 0} samples</div>
        </div>
        
        <div className="stat-card">
          <h3>Extraction Accuracy</h3>
          <div className="value">
            {accuracy ? `${(accuracy.extraction_accuracy * 100).toFixed(0)}%` : 'N/A'}
          </div>
          <div className="change">Entity extraction rate</div>
        </div>
        
        <div className="stat-card">
          <h3>Guardrail Pass Rate</h3>
          <div className="value">
            {performance ? `${(performance.guardrail_pass_rate * 100).toFixed(0)}%` : 'N/A'}
          </div>
          <div className="change">Content safety</div>
        </div>
        
        <div className="stat-card">
          <h3>Human Edit Rate</h3>
          <div className="value">
            {performance ? `${(performance.human_edit_rate * 100).toFixed(0)}%` : 'N/A'}
          </div>
          <div className="change">Drafts requiring edits</div>
        </div>
      </div>

      <div className="main-grid">
        <div className="card">
          <h2>Quality Metrics Explained</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--primary)' }}>
              Relevance Score (30%)
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Measures how well the draft addresses the original message's key points and topics.
              Uses word overlap analysis and topic matching.
            </p>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--primary)' }}>
              Completeness Score (25%)
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Evaluates whether the draft covers all necessary aspects of the reply.
              Considers length, structure, and content coverage.
            </p>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--primary)' }}>
              Tone Score (20%)
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Checks appropriateness of formality, professionalism, and business etiquette.
              Penalizes overly casual or aggressive language.
            </p>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--primary)' }}>
              Professionalism Score (15%)
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Validates proper greetings, closings, and business communication standards.
              Checks for appropriate structure.
            </p>
          </div>
          
          <div>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--primary)' }}>
              Conciseness Score (10%)
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Ensures the draft is appropriately brief without being too short.
              Optimal range: 50-150 words.
            </p>
          </div>
        </div>

        <div className="card">
          <h2>Guardrails System</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>PII Detection</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Automatically detects and masks personally identifiable information:
            </p>
            <ul style={{ fontSize: '13px', color: 'var(--text-secondary)', marginLeft: '20px', marginTop: '8px' }}>
              <li>Social Security Numbers</li>
              <li>Credit Card Numbers</li>
              <li>Phone Numbers</li>
            </ul>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Compliance Checks</h3>
            <ul style={{ fontSize: '13px', color: 'var(--text-secondary)', marginLeft: '20px' }}>
              <li>No guaranteed returns language</li>
              <li>No high-pressure tactics</li>
              <li>Professional tone validation</li>
            </ul>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Content Filtering</h3>
            <ul style={{ fontSize: '13px', color: 'var(--text-secondary)', marginLeft: '20px' }}>
              <li>Inappropriate word detection</li>
              <li>Length validation</li>
              <li>Tone analysis</li>
            </ul>
          </div>
          
          <div>
            <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Risk Scoring</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Each draft receives a risk score (0-1) based on weighted checks:
            </p>
            <ul style={{ fontSize: '13px', color: 'var(--text-secondary)', marginLeft: '20px', marginTop: '8px' }}>
              <li><strong>PII:</strong> 40% weight</li>
              <li><strong>Inappropriate:</strong> 25% weight</li>
              <li><strong>Compliance:</strong> 25% weight</li>
              <li><strong>Length/Tone:</strong> 10% weight</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <h2>Recent Evaluation Results</h2>
        
        {evals.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            No evaluations yet. Run the demo to generate eval data.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Draft ID
                </th>
                <th style={{ textAlign: 'left', padding: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Quality Score
                </th>
                <th style={{ textAlign: 'left', padding: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Guardrails
                </th>
                <th style={{ textAlign: 'left', padding: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody>
              {evals.map((evalItem, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px', fontSize: '13px' }}>
                    {evalItem.draft_id.substring(0, 8)}...
                  </td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="quality-bar" style={{ width: '100px' }}>
                        <div 
                          className="quality-fill" 
                          style={{ 
                            width: `${evalItem.quality_score * 100}%`,
                            background: evalItem.quality_score >= 0.8 ? 'var(--success)' : 
                                       evalItem.quality_score >= 0.6 ? 'var(--warning)' : 'var(--danger)'
                          }}
                        />
                      </div>
                      <span style={{ fontSize: '13px', fontWeight: '500' }}>
                        {(evalItem.quality_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span className={`badge ${evalItem.guardrail_passed ? 'badge-low' : 'badge-high'}`}>
                      {evalItem.guardrail_passed ? 'Passed' : 'Failed'}
                    </span>
                  </td>
                  <td style={{ padding: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {new Date(evalItem.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default EvalDashboard;
