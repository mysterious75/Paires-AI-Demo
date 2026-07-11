import React from 'react';

const Dashboard = ({ metrics, messages }) => {
  if (!metrics) {
    return <div>Loading metrics...</div>;
  }

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Messages Processed</h3>
          <div className="value">{metrics.total_messages_processed || 0}</div>
          <div className="change">+12% from last week</div>
        </div>
        
        <div className="stat-card">
          <h3>Drafts Generated</h3>
          <div className="value">{metrics.total_drafts_generated || 0}</div>
          <div className="change">+8% from last week</div>
        </div>
        
        <div className="stat-card">
          <h3>Approval Rate</h3>
          <div className="value">{((metrics.approval_rate || 0) * 100).toFixed(0)}%</div>
          <div className="change">+5% from last week</div>
        </div>
        
        <div className="stat-card">
          <h3>Avg Quality Score</h3>
          <div className="value">{((metrics.avg_quality_score || 0) * 100).toFixed(0)}%</div>
          <div className="change">+3% from last week</div>
        </div>
        
        <div className="stat-card">
          <h3>Guardrail Pass Rate</h3>
          <div className="value">{((metrics.guardrail_pass_rate || 0) * 100).toFixed(0)}%</div>
          <div className="change">Consistent</div>
        </div>
        
        <div className="stat-card">
          <h3>Classification Accuracy</h3>
          <div className="value">{((metrics.classification_accuracy || 0) * 100).toFixed(0)}%</div>
          <div className="change">+2% from last week</div>
        </div>
      </div>

      <div className="main-grid">
        <div className="card">
          <h2>Recent Messages</h2>
          {messages && messages.length > 0 ? (
            messages.slice(0, 5).map((msg, idx) => (
              <div key={idx} className="message-item">
                <div className="sender">{msg.message.sender}</div>
                <div className="subject">{msg.message.subject}</div>
                <div className="preview">{msg.message.body.substring(0, 100)}...</div>
                <div style={{ marginTop: '8px' }}>
                  <span className={`badge badge-${msg.processing.classification.urgency}`}>
                    {msg.processing.classification.urgency}
                  </span>
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {msg.processing.classification.type}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              Click "Run Demo" to process sample messages
            </div>
          )}
        </div>

        <div className="card">
          <h2>Message Classification Breakdown</h2>
          <ul className="metrics-list">
            {metrics.by_classification && Object.entries(metrics.by_classification).map(([type, count]) => (
              <li key={type}>
                <span className="metric-label">{type.replace(/_/g, ' ')}</span>
                <span className="metric-value">{count}</span>
              </li>
            ))}
          </ul>
          
          <h2 style={{ marginTop: '24px' }}>System Health</h2>
          <ul className="metrics-list">
            <li>
              <span className="metric-label">Avg Response Time</span>
              <span className="metric-value">{metrics.avg_response_time_ms || 0}ms</span>
            </li>
            <li>
              <span className="metric-label">Human Edit Rate</span>
              <span className="metric-value">{((metrics.human_edit_rate || 0) * 100).toFixed(0)}%</span>
            </li>
            <li>
              <span className="metric-label">Extraction Accuracy</span>
              <span className="metric-value">{((metrics.extraction_accuracy || 0) * 100).toFixed(0)}%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
