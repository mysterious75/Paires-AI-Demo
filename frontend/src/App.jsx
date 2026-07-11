import React, { useState, useEffect } from 'react';

const API = '';

function App() {
  const [activeSection, setActiveSection] = useState('hero');
  const [demoResult, setDemoResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [message, setMessage] = useState({
    sender: '', sender_email: '', subject: '', body: '', tone: 'professional'
  });
  const [result, setResult] = useState(null);
  const [drafting, setDrafting] = useState(false);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const [dash, vol, perf] = await Promise.all([
        fetch(`${API}/api/evals/dashboard`).then(r => r.json()),
        fetch(`${API}/api/analytics/volume`).then(r => r.json()),
        fetch(`${API}/api/analytics/performance`).then(r => r.json()),
      ]);
      setMetrics({ ...dash, ...vol, ...perf });
    } catch {}
  };

  const runFullDemo = async () => {
    setLoading(true);
    setDemoResult(null);
    try {
      const r = await fetch(`${API}/api/demo/run`, { method: 'POST' });
      setDemoResult(await r.json());
      fetchMetrics();
    } catch (e) {
      setDemoResult({ error: 'Cannot connect to API. Make sure backend is running on port 8000.' });
    }
    setLoading(false);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    setDrafting(true);
    setResult(null);
    try {
      const processRes = await fetch(`${API}/api/messages/inbound`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: message.sender, sender_email: message.sender_email,
          subject: message.subject, body: message.body
        })
      });
      const processed = await processRes.json();

      const draftRes = await fetch(`${API}/api/drafts/generate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message_id: processed.message_id, tone: message.tone })
      });
      const draft = await draftRes.json();

      setResult({ processed, draft });
      fetchMetrics();
    } catch (e) {
      setResult({ error: 'Connection failed. Ensure backend is running.' });
    }
    setDrafting(false);
  };

  const handleApprove = async (draftId, approved) => {
    await fetch(`${API}/api/drafts/${draftId}/approve`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ draft_id: draftId, approved, edits: null, feedback: null })
    });
    fetchMetrics();
    const status = approved ? 'approved' : 'rejected';
    setResult(prev => ({
      ...prev,
      draft: { ...prev.draft, status }
    }));
  };

  const quickSamples = [
    { label: 'Investor Inquiry', sender: 'Sarah Chen', email: 'sarah@sequoia.com', subject: 'Series A Interest', body: 'Hi,\n\nI came across your company and would love to discuss your Series A plans. At Sequoia, we focus on enterprise AI. Would you be available for a call next week?\n\nBest,\nSarah' },
    { label: 'Founder Pitch', sender: 'Marcus Johnson', email: 'marcus@startup.io', subject: 'Raising $8M Series A', body: 'Hi team,\n\nWe are raising $8M Series A at $50M pre-money. Currently at $2M ARR with 80% margins. Looking for investors who understand B2B SaaS. Happy to share our deck.\n\nThanks,\nMarcus' },
    { label: 'Follow-up', sender: 'Emily Rodriguez', email: 'emily@accel.com', subject: 'Following up', body: 'Hi,\n\nJust following up on our conversation last week. Have you had a chance to review our deck? We are getting other interest and would love to move forward soon.\n\nBest,\nEmily' }
  ];

  const classificationBadge = (type) => {
    const map = { investor_inquiry: 'badge-investor', founder_pitch: 'badge-founder', meeting_request: 'badge-meeting', follow_up: 'badge-followup', general_inquiry: 'badge-general' };
    return `badge ${map[type] || 'badge-general'}`;
  };

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setActiveSection(id);
  };

  const Icon = ({ name }) => {
    const icons = {
      brain: '🧠', shield: '🛡️', chart: '📊', message: '💬',
      target: '🎯', zap: '⚡', users: '👥', star: '⭐'
    };
    return <span style={{ fontSize: 28 }}>{icons[name] || '✦'}</span>;
  };

  return (
    <div>
      {/* ===== NAVIGATION ===== */}
      <nav className="nav">
        <div className="nav-inner">
          <a href="#" className="nav-logo" onClick={() => scrollTo('hero')}>Paires AI</a>
          <div className="nav-links">
            <a href="#features" className="nav-link" onClick={(e) => { e.preventDefault(); scrollTo('features'); }}>Features</a>
            <a href="#demo" className="nav-link" onClick={(e) => { e.preventDefault(); scrollTo('demo'); }}>Demo</a>
            <a href="#dashboard" className="nav-link" onClick={(e) => { e.preventDefault(); scrollTo('dashboard'); }}>Dashboard</a>
            <a href="#demo" className="nav-btn" onClick={(e) => { e.preventDefault(); scrollTo('demo'); }}>Try It Now</a>
          </div>
        </div>
      </nav>

      {/* ===== HERO ===== */}
      <section id="hero" className="hero">
        <div className="hero-badge">Applied AI Engineer Demo</div>
        <h1>
          AI That <span className="gradient-text">Fundraises</span> With You
        </h1>
        <p>
          An intelligent messaging agent that reads, classifies, and drafts replies 
          for investor-founder communications. Built for the Paires platform — 
          production-ready, with built-in quality evals and guardrails.
        </p>
        <div className="hero-buttons">
          <button className="btn-primary" onClick={() => scrollTo('demo')}>
            Try the Demo →
          </button>
          <button className="btn-outline" onClick={runFullDemo}>
            Run 5 Sample Messages
          </button>
        </div>
      </section>

      {/* ===== FEATURES ===== */}
      <section id="features" className="section">
        <div className="section-label">What It Does</div>
        <h2 className="section-title">Every conversation, handled intelligently.</h2>
        <p className="section-subtitle">
          From inbound classification to AI-drafted replies, this agent manages the entire messaging layer.
        </p>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(102,126,234,0.15)' }}><Icon name="brain" /></div>
            <h3>Message Classification</h3>
            <p>Auto-detects investor inquiries, founder pitches, meeting requests, and follow-ups. Routes to the right team instantly.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(168,85,247,0.15)' }}><Icon name="target" /></div>
            <h3>Entity Extraction</h3>
            <p>Pulls company names, funding stages, ask amounts, and emails from every message. No manual data entry.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(74,222,128,0.15)' }}><Icon name="message" /></div>
            <h3>AI Reply Drafting</h3>
            <p>Context-aware replies with adjustable tone — professional, warm, or concise. Human-in-the-loop before sending.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(251,191,36,0.15)' }}><Icon name="shield" /></div>
            <h3>Guardrails</h3>
            <p>PII detection, compliance checks, and content filtering ensure every reply meets quality standards.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(96,165,250,0.15)' }}><Icon name="chart" /></div>
            <h3>Quality Metrics</h3>
            <p>Every draft scored on relevance, tone, completeness, and professionalism. Tracked over time.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(244,114,182,0.15)' }}><Icon name="zap" /></div>
            <h3>Batch Processing</h3>
            <p>Process hundreds of messages at once. Built for scale — from 10 to 10,000 conversations.</p>
          </div>
        </div>
      </section>

      {/* ===== STATS ===== */}
      {metrics && (
        <div className="stats-section">
          <div className="section">
            <div className="section-label">Live Metrics</div>
            <div className="stats-grid">
              <div className="stat-item">
                <h2>{metrics.total_messages || 0}</h2>
                <p>Messages Processed</p>
              </div>
              <div className="stat-item">
                <h2>{metrics.total_drafts || 0}</h2>
                <p>Drafts Generated</p>
              </div>
              <div className="stat-item">
                <h2>{((metrics.approval_rate || 0) * 100).toFixed(0)}%</h2>
                <p>Approval Rate</p>
              </div>
              <div className="stat-item">
                <h2>{((metrics.avg_quality_score || 0) * 100).toFixed(0)}%</h2>
                <p>Avg Quality Score</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ===== DEMO ===== */}
      <section id="demo" className="section">
        <div className="section-label">Try It</div>
        <h2 className="section-title">Send a message, see AI in action.</h2>
        <p className="section-subtitle">
          Paste any investor or founder message below. The agent will classify it, extract info, and draft a reply.
        </p>

        <div className="demo-grid">
          {/* Input Form */}
          <div>
            <form onSubmit={handleSend}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="input-group">
                  <label>Sender Name</label>
                  <input type="text" placeholder="Sarah Chen" value={message.sender}
                    onChange={e => setMessage({...message, sender: e.target.value})} required />
                </div>
                <div className="input-group">
                  <label>Sender Email</label>
                  <input type="email" placeholder="sarah@sequoia.com" value={message.sender_email}
                    onChange={e => setMessage({...message, sender_email: e.target.value})} required />
                </div>
              </div>
              <div className="input-group">
                <label>Subject</label>
                <input type="text" placeholder="Series A Investment Interest" value={message.subject}
                  onChange={e => setMessage({...message, subject: e.target.value})} required />
              </div>
              <div className="input-group">
                <label>Tone</label>
                <select value={message.tone} onChange={e => setMessage({...message, tone: e.target.value})}>
                  <option value="professional">Professional</option>
                  <option value="warm">Warm & Friendly</option>
                  <option value="concise">Concise</option>
                  <option value="detailed">Detailed</option>
                  <option value="follow_up">Follow-up</option>
                </select>
              </div>
              <div className="input-group">
                <label>Message Body</label>
                <textarea placeholder="Paste the full message here..." value={message.body}
                  onChange={e => setMessage({...message, body: e.target.value})} required />
              </div>

              {/* Quick Samples */}
              <div style={{ marginBottom: 20 }}>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Quick fill:</p>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {quickSamples.map((s, i) => (
                    <button key={i} type="button" className="btn-outline btn-sm"
                      onClick={() => setMessage({ sender: s.sender, sender_email: s.email, subject: s.subject, body: s.body, tone: 'professional' })}
                      style={{ fontSize: 12 }}>
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              <button type="submit" className="btn-primary" disabled={drafting} style={{ width: '100%', justifyContent: 'center' }}>
                {drafting ? 'Processing...' : 'Process & Draft Reply →'}
              </button>
            </form>
          </div>

          {/* Results */}
          <div>
            {drafting && (
              <div className="loader">
                <div className="spinner" />
                <span style={{ marginLeft: 12, color: 'var(--text-secondary)' }}>AI is thinking...</span>
              </div>
            )}

            {result?.error && (
              <div className="result-card" style={{ border: '1px solid rgba(239,68,68,0.3)' }}>
                <p style={{ color: '#ef4444' }}>{result.error}</p>
              </div>
            )}

            {result?.processed && (
              <div className="result-card" style={{ animation: 'slideUp 0.4s ease' }}>
                <div className="result-header">
                  <span className={classificationBadge(result.processed.classification.type)}>
                    {result.processed.classification.type.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {(result.processed.classification.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>ROUTING</p>
                  <p style={{ fontSize: 14 }}>
                    {result.processed.routing.department} → {result.processed.routing.assign_to}
                  </p>
                </div>

                {result.processed.entities.funding_stage && (
                  <div style={{ marginBottom: 16 }}>
                    <span className={classificationBadge(result.processed.classification.type)}>
                      {result.processed.entities.funding_stage}
                    </span>
                  </div>
                )}
              </div>
            )}

            {result?.draft && !result?.draft.status && (
              <div className="result-card">
                <div className="result-header">
                  <span style={{ fontWeight: 600 }}>AI-Drafted Reply</span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Risk: {result.draft.guardrail_results?.risk_level || 'low'}
                  </span>
                </div>

                <div className="reply-box">{result.draft.drafted_reply}</div>

                <div className="score-bar">
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Quality Score</span>
                  <div className="score-track">
                    <div className="score-fill" style={{ width: `${(result.draft.quality_score * 100)}%` }} />
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 600 }}>
                    {(result.draft.quality_score * 100).toFixed(0)}%
                  </span>
                </div>

                <p style={{ fontSize: 12, color: result.draft.guardrail_results?.passed ? 'var(--accent-green)' : '#ef4444', marginBottom: 12 }}>
                  {result.draft.guardrail_results?.passed ? '✓ All guardrails passed' : '✗ Guardrail issues detected'}
                </p>

                <div className="action-row">
                  <button className="btn-accept btn-sm" onClick={() => handleApprove(result.draft.draft_id, true)}>
                    ✓ Approve
                  </button>
                  <button className="btn-edit btn-sm" onClick={() => {
                    const edits = prompt('Edit the reply:', result.draft.drafted_reply);
                    if (edits) handleApprove(result.draft.draft_id, true);
                  }}>
                    ✎ Edit
                  </button>
                  <button className="btn-reject btn-sm" onClick={() => handleApprove(result.draft.draft_id, false)}>
                    ✗ Reject
                  </button>
                </div>
              </div>
            )}

            {result?.draft?.status && (
              <div className="result-card" style={{ borderColor: result.draft.status === 'approved' ? 'rgba(74,222,128,0.3)' : 'rgba(239,68,68,0.3)' }}>
                <p style={{ fontSize: 14, fontWeight: 600, color: result.draft.status === 'approved' ? 'var(--accent-green)' : '#ef4444' }}>
                  {result.draft.status === 'approved' ? '✓ Draft Approved & Ready to Send' : '✗ Draft Rejected'}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ===== DEMO RESULTS ===== */}
      {demoResult && !demoResult.error && (
        <section className="section">
          <div className="section-label">Demo Run Results</div>
          <h2 className="section-title">{demoResult.messages_processed} messages, fully processed.</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 16 }}>
            {demoResult.results?.map((r, i) => (
              <div key={i} className="feature-card">
                <div className="result-header">
                  <span className={classificationBadge(r.classification.type)}>
                    {r.classification.type.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {(r.classification.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p style={{ fontWeight: 600, marginBottom: 4 }}>{r.sender}</p>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>{r.subject}</p>

                {r.entities.funding_stage && (
                  <span className="badge badge-founder" style={{ marginBottom: 12, display: 'inline-block' }}>
                    {r.entities.funding_stage}
                  </span>
                )}

                <div className="reply-box" style={{ fontSize: 12 }}>{r.drafted_reply}</div>

                <div className="score-bar">
                  <div className="score-track">
                    <div className="score-fill" style={{ width: `${(r.quality_score * 100)}%` }} />
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 600 }}>
                    {(r.quality_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ===== DASHBOARD ===== */}
      <section id="dashboard" className="section">
        <div className="section-label">Quality Metrics</div>
        <h2 className="section-title">Every output, measured.</h2>
        <p className="section-subtitle">
          Quality evals, guardrail passes, and approval rates — tracked in real time.
        </p>

        {metrics && (
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Classification Accuracy</div>
              <div className="metric-value" style={{ color: 'var(--accent-blue)' }}>
                {((metrics.classification_accuracy || 0) * 100).toFixed(0)}%
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Extraction Accuracy</div>
              <div className="metric-value" style={{ color: 'var(--accent-green)' }}>
                {((metrics.extraction_accuracy || 0) * 100).toFixed(0)}%
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Guardrail Pass Rate</div>
              <div className="metric-value" style={{ color: '#a855f7' }}>
                {((metrics.guardrail_pass_rate || 0) * 100).toFixed(0)}%
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Human Edit Rate</div>
              <div className="metric-value" style={{ color: '#fbbf24' }}>
                {((metrics.human_edit_rate || 0) * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        )}

        <div className="features-grid">
          <div className="feature-card">
            <h3 style={{ marginBottom: 16 }}>How Quality Is Scored</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                { label: 'Relevance', weight: '30%', color: '#667eea' },
                { label: 'Completeness', weight: '25%', color: '#764ba2' },
                { label: 'Tone Appropriateness', weight: '20%', color: '#f5576c' },
                { label: 'Professionalism', weight: '15%', color: '#4facfe' },
                { label: 'Conciseness', weight: '10%', color: '#4ade80' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{item.label}</span>
                  <span style={{ fontSize: 13, fontWeight: 600, color: item.color }}>{item.weight}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="feature-card">
            <h3 style={{ marginBottom: 16 }}>Guardrails System</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                { label: 'PII Detection', desc: 'SSN, credit cards, phone numbers' },
                { label: 'Compliance Check', desc: 'No guaranteed returns / pressure tactics' },
                { label: 'Content Filtering', desc: 'Inappropriate language detection' },
                { label: 'Tone Analysis', desc: 'Casual/aggressive tone warnings' },
                { label: 'Length Validation', desc: 'Optimal 50-150 word range' },
              ].map((item, i) => (
                <div key={i}>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>{item.label}</span>
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== CTA ===== */}
      <section className="cta-section">
        <h2 className="section-title">Ready to see it in action?</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 40, fontSize: 18 }}>
          This demo was built for the Paires Applied AI Engineer role.<br />
          Every feature maps to a real production need.
        </p>
        <button className="btn-primary" onClick={runFullDemo}>
          {loading ? 'Running...' : 'Run Complete Demo →'}
        </button>
      </section>

      {/* ===== FOOTER ===== */}
      <div className="footer">
        <p>Built for Paires • Applied AI Engineer Demo • All data processed locally</p>
      </div>
    </div>
  );
}

export default App;
