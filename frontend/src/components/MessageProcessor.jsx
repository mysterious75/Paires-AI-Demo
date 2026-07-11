import React, { useState } from 'react';

const MessageProcessor = ({ onMessageProcessed }) => {
  const [formData, setFormData] = useState({
    sender: '',
    sender_email: '',
    subject: '',
    body: ''
  });
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [draft, setDraft] = useState(null);
  const [drafting, setDrafting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);
    
    try {
      const response = await fetch('/api/messages/inbound', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      setResult(data);
      
      // Auto-generate draft
      await generateDraft(data.message_id);
      
    } catch (error) {
      console.error('Error processing message:', error);
    }
    
    setProcessing(false);
  };

  const generateDraft = async (messageId) => {
    setDrafting(true);
    
    try {
      const response = await fetch('/api/drafts/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message_id: messageId, tone: 'professional' })
      });
      
      const data = await response.json();
      setDraft(data);
      
    } catch (error) {
      console.error('Error generating draft:', error);
    }
    
    setDrafting(false);
  };

  const approveDraft = async (approved, edits = null) => {
    if (!draft) return;
    
    try {
      await fetch(`/api/drafts/${draft.draft_id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          draft_id: draft.draft_id, 
          approved, 
          edits 
        })
      });
      
      alert(approved ? 'Draft approved!' : 'Draft rejected');
      onMessageProcessed();
      
    } catch (error) {
      console.error('Error approving draft:', error);
    }
  };

  return (
    <div className="main-grid">
      <div className="card">
        <h2>Process New Message</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px' }}>
              Sender Name
            </label>
            <input
              type="text"
              value={formData.sender}
              onChange={(e) => setFormData({ ...formData, sender: e.target.value })}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border)' }}
              placeholder="John Smith"
              required
            />
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px' }}>
              Sender Email
            </label>
            <input
              type="email"
              value={formData.sender_email}
              onChange={(e) => setFormData({ ...formData, sender_email: e.target.value })}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border)' }}
              placeholder="john@example.com"
              required
            />
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px' }}>
              Subject
            </label>
            <input
              type="text"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border)' }}
              placeholder="Investment Inquiry"
              required
            />
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px' }}>
              Message Body
            </label>
            <textarea
              value={formData.body}
              onChange={(e) => setFormData({ ...formData, body: e.target.value })}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border)', minHeight: '150px' }}
              placeholder="Paste the incoming message here..."
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={processing}
            style={{ width: '100%' }}
          >
            {processing ? 'Processing...' : 'Process Message'}
          </button>
        </form>
        
        {/* Quick Fill Buttons */}
        <div style={{ marginTop: '16px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
          <p style={{ fontSize: '12px', marginBottom: '8px', color: 'var(--text-secondary)' }}>
            Quick Fill with Sample Messages:
          </p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {[
              { label: 'Investor Inquiry', sender: 'Sarah Chen', email: 'sarah@sequoia.com', subject: 'Series A Interest', body: 'Hi, I saw your company and would love to discuss your Series A plans. We at Sequoia are very interested in AI companies with strong unit economics. Would you be available for a call?' },
              { label: 'Founder Pitch', sender: 'Marcus Johnson', email: 'marcus@startup.io', subject: 'Raising $8M Series A', body: 'Hi, we are raising an $8M Series A at $50M pre-money. Currently at $2M ARR with 80% gross margins. Looking for investors who understand enterprise AI. Happy to share our deck.' },
              { label: 'Follow-up', sender: 'Emily Rodriguez', email: 'emily@accel.com', subject: 'Following up', body: 'Hi, following up on our conversation last week. Have you had a chance to review our materials? We are getting other interest and would love to move forward.' }
            ].map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className="btn"
                onClick={() => setFormData({
                  sender: sample.sender,
                  sender_email: sample.email,
                  subject: sample.subject,
                  body: sample.body
                })}
                style={{ fontSize: '12px', padding: '6px 12px' }}
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Processing Results</h2>
        
        {!result && !processing && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            Submit a message to see AI processing results
          </div>
        )}
        
        {processing && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>⏳</div>
            <div>Processing message with AI...</div>
          </div>
        )}
        
        {result && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Classification</h3>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <span className={`badge badge-${result.classification.urgency}`}>
                  {result.classification.urgency} urgency
                </span>
                <span className="badge" style={{ background: '#E3F2FD', color: '#1565C0' }}>
                  {result.classification.type}
                </span>
                <span className="badge" style={{ background: '#F3E5F5', color: '#7B1FA2' }}>
                  {result.classification.sentiment}
                </span>
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                Confidence: {(result.classification.confidence * 100).toFixed(0)}%
                {result.classification.requires_human_review && ' • Requires review'}
              </div>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Extracted Entities</h3>
              <ul className="metrics-list">
                {Object.entries(result.entities)
                  .filter(([key, value]) => value && key !== 'raw_text' && key !== 'confidence_scores')
                  .slice(0, 6)
                  .map(([key, value]) => (
                    <li key={key}>
                      <span className="metric-label">{key.replace(/_/g, ' ')}</span>
                      <span className="metric-value">
                        {Array.isArray(value) ? value.join(', ') : String(value)}
                      </span>
                    </li>
                  ))
                }
              </ul>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Routing</h3>
              <div style={{ padding: '12px', background: '#f8f9fa', borderRadius: '8px', fontSize: '13px' }}>
                <div><strong>Department:</strong> {result.classification.routing_suggestion.department}</div>
                <div><strong>Priority:</strong> {result.classification.routing_suggestion.priority}</div>
                <div><strong>Assign to:</strong> {result.classification.routing_suggestion.assign_to}</div>
              </div>
            </div>
          </div>
        )}

        {draft && (
          <div style={{ marginTop: '24px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>AI-Drafted Reply</h3>
            
            {drafting ? (
              <div style={{ textAlign: 'center', padding: '20px' }}>
                Generating draft...
              </div>
            ) : (
              <>
                <div className="draft-preview">
                  {draft.drafted_reply}
                </div>
                
                <div className="quality-meter">
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Quality Score:</span>
                  <div className="quality-bar">
                    <div 
                      className="quality-fill" 
                      style={{ width: `${draft.quality_score * 100}%` }}
                    />
                  </div>
                  <span style={{ fontSize: '14px', fontWeight: '600' }}>
                    {(draft.quality_score * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div style={{ marginTop: '12px', fontSize: '12px' }}>
                  <span style={{ 
                    color: draft.guardrail_results.passed ? 'var(--success)' : 'var(--danger)',
                    fontWeight: '500'
                  }}>
                    {draft.guardrail_results.passed ? '✓ Guardrails Passed' : '✗ Guardrails Failed'}
                  </span>
                </div>
                
                <div className="action-buttons">
                  <button 
                    className="btn btn-success"
                    onClick={() => approveDraft(true)}
                  >
                    Approve & Send
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      const edits = prompt('Enter edits:', draft.drafted_reply);
                      if (edits) approveDraft(true, edits);
                    }}
                  >
                    Edit & Approve
                  </button>
                  <button 
                    className="btn btn-danger"
                    onClick={() => approveDraft(false)}
                  >
                    Reject
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageProcessor;
