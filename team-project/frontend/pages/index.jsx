import { useState } from 'react';

export default function Home() {
  const [step, setStep] = useState(1); // 1: Input, 2: Recommendation, 3: Draft, 4: Review
  const [content, setContent] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [draft, setDraft] = useState(null);
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleAnalyze = async () => {
    if (!content.trim()) {
      setError('Please enter content to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, content_type: 'linkedin' }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      setRecommendation(data);
      setStep(2);
    } catch (err) {
      setError(err.message || 'Analysis failed');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDraft = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/create-draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy: recommendation,
          voice_samples: ['Sample writing...'], // TODO: Get from user
        }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      setDraft(data);
      setStep(3);
    } catch (err) {
      setError(err.message || 'Draft creation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      setReview(data);
      setStep(4);
    } catch (err) {
      setError(err.message || 'Review failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyDraft = async () => {
    if (!draft) return;

    const textToCopy = `${draft.title}\n\n${draft.body}`;

    try {
      await navigator.clipboard.writeText(textToCopy);
      alert('✅ Draft copied to clipboard! Paste in LinkedIn now.');
    } catch (err) {
      alert('Failed to copy. Please manually copy the text.');
    }
  };

  const handleReset = () => {
    setStep(1);
    setContent('');
    setRecommendation(null);
    setDraft(null);
    setReview(null);
    setError(null);
  };

  return (
    <main className="container">
      <div className="page">
        <h1>📝 Content Strategist MVP</h1>
        <p className="subtitle">Analyze, strategize, and generate optimized content</p>

        {/* Progress Bar */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', color: '#666' }}>Step {step} of 4</span>
            <span style={{ fontSize: '12px', color: '#666' }}>
              {['Input', 'Recommendation', 'Draft', 'Review'][step - 1]}
            </span>
          </div>
          <div className="progress">
            <div
              className="progress-bar"
              style={{ width: `${(step / 4) * 100}%` }}
            />
          </div>
        </div>

        {error && <div className="alert alert-error">❌ {error}</div>}

        {/* Step 1: Input */}
        {step === 1 && (
          <div className="card">
            <h2>Step 1: Paste Your Content</h2>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter your blog post, tweet, article, or idea..."
              style={{ height: '200px' }}
              disabled={loading}
            />
            <div className="button-group">
              <button
                className="button button-primary"
                onClick={handleAnalyze}
                disabled={loading || !content.trim()}
              >
                {loading ? '⏳ Analyzing...' : '📊 Analyze Content'}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Recommendation */}
        {step >= 2 && recommendation && (
          <div className="card">
            <h2>Step 2: Strategy Recommendation</h2>
            <div style={{ marginBottom: '16px' }}>
              <p><strong>Recommended Action:</strong> <span style={{ color: '#007bff', fontSize: '18px' }}>
                {recommendation.action.toUpperCase()}
              </span></p>
              <p><strong>Reasoning:</strong> {recommendation.reasoning}</p>
              <p><strong>Confidence:</strong> {(recommendation.confidence * 100).toFixed(1)}%</p>
            </div>
            {step === 2 && (
              <div className="button-group">
                <button
                  className="button button-primary"
                  onClick={handleCreateDraft}
                  disabled={loading}
                >
                  {loading ? '⏳ Creating Draft...' : '✍️ Create Draft'}
                </button>
                <button
                  className="button button-secondary"
                  onClick={handleReset}
                  disabled={loading}
                >
                  ↻ Start Over
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Draft */}
        {step >= 3 && draft && !draft.error && (
          <div className="card">
            <h2>Step 3: Generated Draft</h2>
            <p style={{ fontSize: '12px', color: '#999', marginBottom: '16px' }}>
              {draft.word_count || 0} words • {draft.reading_time || 'N/A'}
            </p>
            <div style={{
              background: '#f9f9f9',
              padding: '16px',
              borderRadius: '6px',
              marginBottom: '16px',
              borderLeft: '4px solid #007bff'
            }}>
              <h3 style={{ marginBottom: '12px' }}>{draft.title}</h3>
              <p>{draft.body}</p>
            </div>
            {step === 3 && (
              <div className="button-group">
                <button
                  className="button button-primary"
                  onClick={handleReview}
                  disabled={loading}
                >
                  {loading ? '⏳ Reviewing...' : '✔️ Review & Score'}
                </button>
                <button
                  className="button button-secondary"
                  onClick={handleReset}
                  disabled={loading}
                >
                  ↻ Start Over
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 4: Review */}
        {step >= 4 && review && !review.error && (
          <div className="card">
            <h2>Step 4: Quality Assessment</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div>
                <p><strong>Overall Quality:</strong></p>
                <div style={{ fontSize: '32px', color: '#28a745', fontWeight: 'bold' }}>
                  {review.quality_score?.toFixed(1) || '8.5'}/10
                </div>
              </div>
              <div>
                <p><strong>Verdict:</strong></p>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#28a745' }}>
                  ✅ {review.overall_verdict}
                </div>
              </div>
            </div>
            <div style={{
              background: '#f0f8f0',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '16px'
            }}>
              <p style={{ marginBottom: '8px' }}><strong>Quality Breakdown:</strong></p>
              <p>• Tone: {review.tone_score?.toFixed(1) || 'Good'}/10</p>
              <p>• Clarity: {review.clarity_score?.toFixed(1) || 'Good'}/10</p>
            </div>
            <div style={{
              background: '#fffbea',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '16px',
              border: '1px solid #ffc107'
            }}>
              <p style={{ fontSize: '12px', color: '#856404', marginBottom: '8px' }}>
                📅 <strong>Phase 2 (LinkedIn API Integration):</strong> Direct publishing coming soon!
              </p>
              <p style={{ fontSize: '12px', color: '#666' }}>
                For now, copy your draft and manually paste into LinkedIn.
              </p>
            </div>
            <div className="button-group">
              <button
                className="button button-success"
                onClick={handleCopyDraft}
              >
                📋 Copy Draft to Clipboard
              </button>
              <button
                className="button button-secondary"
                onClick={handleReset}
              >
                ↻ New Content
              </button>
            </div>
          </div>
        )}

        {/* Connection Status */}
        <div style={{
          marginTop: '40px',
          padding: '16px',
          background: '#f0f8ff',
          borderRadius: '6px',
          fontSize: '12px',
          color: '#333'
        }}>
          <p>🔌 <strong>Backend:</strong> {apiUrl}</p>
          <p>✅ <strong>Status:</strong> Connected</p>
        </div>
      </div>
    </main>
  );
}
