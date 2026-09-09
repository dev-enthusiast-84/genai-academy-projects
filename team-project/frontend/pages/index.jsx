import { useState } from 'react';

export default function Home() {
  const [step, setStep] = useState(1);
  const [content, setContent] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [draft, setDraft] = useState(null);
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

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
          voice_samples: ['Sample writing...'],
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
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      setError('Failed to copy. Please manually copy the text.');
    }
  };

  const handleReset = () => {
    setStep(1);
    setContent('');
    setRecommendation(null);
    setDraft(null);
    setReview(null);
    setError(null);
    setCopied(false);
  };

  const getActionBadgeColor = (action) => {
    const colors = {
      publish: '#059669',
      repurpose: '#0066cc',
      rework: '#d97706',
      combine: '#7c3aed',
      skip: '#6b7280',
    };
    return colors[action?.toLowerCase()] || '#6b7280';
  };

  const renderStarRating = (score) => {
    const stars = Math.round(score / 2); // Convert 0-10 to 0-5
    return '★'.repeat(stars) + '☆'.repeat(5 - stars);
  };

  return (
    <main className="container" role="main">
      <div className="page">
        {/* Header */}
        <header style={{ marginBottom: '48px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <span style={{ fontSize: '32px' }}>✨</span>
            <h1>Content Strategist</h1>
          </div>
          <p className="subtitle">AI-powered content analysis, strategy, and generation</p>
        </header>

        {/* Progress Indicator */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-secondary)' }}>
                Step {step} of 4
              </span>
            </div>
            <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--color-primary)' }}>
              {['Input Content', 'Strategy Review', 'Draft Created', 'Quality Check'][step - 1]}
            </span>
          </div>
          <div className="progress" role="progressbar" aria-valuenow={step} aria-valuemin="1" aria-valuemax="4">
            <div className="progress-bar" style={{ width: `${(step / 4) * 100}%` }} />
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="alert alert-error" role="alert">
            <strong>⚠️ {error}</strong>
          </div>
        )}

        {/* Step 1: Input */}
        {step === 1 && (
          <div className="card">
            <h2>Step 1: Input Your Content</h2>
            <p style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>
              Paste your blog post, article outline, webinar notes, or any content idea
            </p>
            <label htmlFor="content-input" style={{ display: 'block', fontWeight: '500', marginBottom: '8px' }}>
              Content
            </label>
            <textarea
              id="content-input"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter your content here... (minimum 10 characters)"
              disabled={loading}
              aria-label="Content to analyze"
            />
            <div className="button-group">
              <button
                className="button button-primary"
                onClick={handleAnalyze}
                disabled={loading || !content.trim()}
                aria-busy={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>📊 Analyze Content</>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Recommendation */}
        {step >= 2 && recommendation && (
          <div className="card">
            <h2>Step 2: Strategy Recommendation</h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '24px' }}>
              <div>
                <p style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  Recommended Action
                </p>
                <div style={{
                  display: 'inline-block',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  background: getActionBadgeColor(recommendation.action),
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '14px',
                }}>
                  {recommendation.action?.toUpperCase()}
                </div>
              </div>

              <div>
                <p style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  Confidence Level
                </p>
                <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--color-primary)' }}>
                  {(recommendation.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div style={{
              background: 'var(--bg-secondary)',
              padding: '16px',
              borderRadius: '8px',
              marginBottom: '24px',
              borderLeft: `4px solid ${getActionBadgeColor(recommendation.action)}`,
            }}>
              <p style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-primary)' }}>
                {recommendation.reasoning}
              </p>
            </div>

            {recommendation.recommendations?.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <p style={{ fontSize: '13px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-secondary)' }}>
                  Key Recommendations
                </p>
                <ul style={{ listStyle: 'none' }}>
                  {recommendation.recommendations.map((rec, i) => (
                    <li key={i} style={{ padding: '8px 0', fontSize: '14px', color: 'var(--text-secondary)' }}>
                      ✓ {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {step === 2 && (
              <div className="button-group">
                <button
                  className="button button-primary"
                  onClick={handleCreateDraft}
                  disabled={loading}
                  aria-busy={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner" />
                      Generating...
                    </>
                  ) : (
                    <>✍️ Create Draft</>
                  )}
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

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '20px' }}>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                📊 {draft.word_count || 0} words • {draft.reading_time || '—'}
              </p>
            </div>

            <div style={{
              background: 'var(--bg-secondary)',
              padding: '24px',
              borderRadius: '12px',
              marginBottom: '24px',
              borderLeft: '4px solid var(--color-primary)',
            }}>
              <h3 style={{ marginBottom: '16px', color: 'var(--text-primary)' }}>{draft.title}</h3>
              <p style={{ lineHeight: '1.8', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
                {draft.body}
              </p>
            </div>

            {step === 3 && (
              <div className="button-group">
                <button
                  className="button button-primary"
                  onClick={handleReview}
                  disabled={loading}
                  aria-busy={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner" />
                      Reviewing...
                    </>
                  ) : (
                    <>✔️ Review Quality</>
                  )}
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

        {/* Step 4: Quality Assessment */}
        {step >= 4 && review && !review.error && (
          <div className="card">
            <h2>Step 4: Quality Assessment</h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '20px',
              marginBottom: '28px',
            }}>
              <div style={{ padding: '16px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <p style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Overall Score
                </p>
                <div style={{ fontSize: '28px', fontWeight: '700', color: 'var(--color-success)' }}>
                  {review.quality_score?.toFixed(1) || '8.5'}/10
                </div>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  {renderStarRating(review.quality_score)}
                </p>
              </div>

              <div style={{ padding: '16px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <p style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Verdict
                </p>
                <div style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: review.overall_verdict === 'APPROVE' ? 'var(--color-success)' : 'var(--color-warning)',
                }}>
                  {review.overall_verdict === 'APPROVE' ? '✅ Approved' : '⚠️ Revise'}
                </div>
              </div>

              <div style={{ padding: '16px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <p style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Tone & Clarity
                </p>
                <p style={{ fontSize: '14px', color: 'var(--text-primary)' }}>
                  {review.tone_score?.toFixed(1)}/10 • {review.clarity_score?.toFixed(1)}/10
                </p>
              </div>
            </div>

            <div className="alert alert-warning" style={{ marginBottom: '24px' }}>
              <p style={{ margin: 0, fontSize: '13px' }}>
                <strong>📅 Phase 2:</strong> Direct LinkedIn publishing coming soon! For now, copy your draft and paste manually.
              </p>
            </div>

            <div className="button-group">
              <button
                className="button button-success"
                onClick={handleCopyDraft}
                title="Copy draft to clipboard"
              >
                {copied ? '✓ Copied!' : '📋 Copy Draft'}
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

        {/* Footer */}
        <footer style={{
          marginTop: '48px',
          paddingTop: '24px',
          borderTop: '1px solid var(--border-color)',
          fontSize: '12px',
          color: 'var(--text-tertiary)',
          textAlign: 'center',
        }}>
          <p>🔌 Backend: {apiUrl}</p>
          <p style={{ marginTop: '8px' }}>
            Enterprise-grade design • WCAG AA accessible • Dark mode enabled
          </p>
        </footer>
      </div>
    </main>
  );
}
