import { useState } from 'react';

export default function Home() {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!content.trim()) {
      setError('Please enter content to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content,
          content_type: 'linkedin',
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze content');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Content Strategist MVP</h1>
      <p style={styles.subtitle}>Analyze, strategize, and generate optimized content</p>

      <div style={styles.inputSection}>
        <label style={styles.label}>Paste your content:</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Enter content to analyze..."
          style={styles.textarea}
          disabled={loading}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{...styles.button, opacity: loading ? 0.6 : 1}}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={styles.result}>
          <h2>Analysis Result</h2>
          <div style={styles.resultItem}>
            <strong>Action:</strong> {result.action}
          </div>
          <div style={styles.resultItem}>
            <strong>Reasoning:</strong> {result.reasoning}
          </div>
          <div style={styles.resultItem}>
            <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
          </div>
        </div>
      )}

      <div style={styles.info}>
        <p>API Status: <span style={styles.statusGreen}>Connected</span></p>
        <p>Backend: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '40px 20px',
    fontFamily: 'sans-serif',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh',
  },
  title: {
    color: '#333',
    marginBottom: '8px',
  },
  subtitle: {
    color: '#666',
    marginBottom: '30px',
  },
  inputSection: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: 'bold',
    color: '#333',
  },
  textarea: {
    width: '100%',
    height: '150px',
    padding: '10px',
    marginBottom: '15px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontFamily: 'monospace',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  button: {
    backgroundColor: '#007bff',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  },
  result: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    borderLeft: '4px solid #28a745',
  },
  resultItem: {
    marginBottom: '12px',
    color: '#333',
  },
  error: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '20px',
    border: '1px solid #f5c6cb',
  },
  info: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '4px',
    fontSize: '14px',
    color: '#666',
  },
  statusGreen: {
    color: '#28a745',
    fontWeight: 'bold',
  },
};
