import React, { useState, useCallback, useRef } from 'react';
import axios from 'axios';
import './App.css';

interface EvaluationResult {
  startup_id: string;
  overall_score: number;
  recommendation: string;
  confidence_level: string;
  financial_health: {
    score: number;
    details: string;
  };
  team_quality: {
    score: number;
    details: string;
  };
  market_opportunity: {
    score: number;
    details: string;
  };
  product_traction: {
    score: number;
    details: string;
  };
  risk_assessment: {
    score: number;
    details: string;
  };
  peer_comparison: {
    sector_avg: number;
    vs_avg: string;
  };
  realtime_status: string;
  error?: string;
  raw_analysis: string;
}

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const BACKEND_URL = 'https://startup-evaluator-backend-166437193095.asia-south1.run.app';

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a PDF file only.');
      }
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Please upload a PDF file only.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a PDF file to upload.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${BACKEND_URL}/evaluate-startup`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minute timeout for AI processing
      });

      setEvaluation(response.data);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to process PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetUpload = () => {
    setFile(null);
    setEvaluation(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#F44336';
  };

  return (
    <div className="app">

      {/* PDF Upload and Analysis Section - At TOP */}
      <main className="app-main">
        <div className="analysis-section">
          {/* Upload Area */}
          <div className="upload-section">
            <div
              className={`upload-area ${dragActive ? 'drag-active' : ''} ${file ? 'file-selected' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              
              {file ? (
                <div className="file-info">
                  <div className="file-icon">📄</div>
                  <div className="file-details">
                    <h3>{file.name}</h3>
                    <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                  <button 
                    className="remove-file" 
                    onClick={(e) => {
                      e.stopPropagation();
                      resetUpload();
                    }}
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <div className="upload-prompt">
                  <div className="upload-icon">📁</div>
                  <h3>Drop your PDF here or click to browse</h3>
                  <p>Upload startup pitch deck, financial documents, or business plan</p>
                  <div className="supported-formats">
                    <span>Supported: PDF files only</span>
                  </div>
                </div>
              )}
            </div>

            {error && (
              <div className="error-message">
                <span>⚠️ {error}</span>
              </div>
            )}

            <div className="upload-actions">
              <button 
                className="upload-btn" 
                onClick={handleUpload}
                disabled={!file || loading}
              >
                {loading ? 'Processing with AI...' : 'Analyze with AI'}
              </button>
              
              {file && (
                <button 
                  className="reset-btn" 
                  onClick={resetUpload}
                  disabled={loading}
                >
                  Reset
                </button>
              )}
            </div>
          </div>

          {/* Analysis Results */}
          {evaluation && (
            <div className="results-section">
              <div className="results-header">
                <h2>🤖 AI Analysis Complete</h2>
                <div className="analysis-status">
                  <span className="status-badge success">✅ {evaluation.realtime_status}</span>
                  <span className="confidence-level">Confidence: {evaluation.confidence_level}</span>
                </div>
              </div>

              <div className="overall-score-card">
                <div className="score-display">
                  <div 
                    className="score-circle" 
                    style={{ backgroundColor: getScoreColor(evaluation.overall_score) }}
                  >
                    <span className="score-value">{evaluation.overall_score}</span>
                    <span className="score-max">/100</span>
                  </div>
                  <div className="score-label">Overall Investment Score</div>
                </div>
                <div className="recommendation-display">
                  <h3>💡 Investment Recommendation</h3>
                  <p className="recommendation-text">{evaluation.recommendation}</p>
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <h4>💰 Financial Health</h4>
                  <div className="metric-score" style={{ color: getScoreColor(evaluation.financial_health.score) }}>
                    {evaluation.financial_health.score}/100
                  </div>
                  <p className="metric-details">{evaluation.financial_health.details}</p>
                </div>

                <div className="metric-card">
                  <h4>👥 Team Quality</h4>
                  <div className="metric-score" style={{ color: getScoreColor(evaluation.team_quality.score) }}>
                    {evaluation.team_quality.score}/100
                  </div>
                  <p className="metric-details">{evaluation.team_quality.details}</p>
                </div>

                <div className="metric-card">
                  <h4>🌍 Market Opportunity</h4>
                  <div className="metric-score" style={{ color: getScoreColor(evaluation.market_opportunity.score) }}>
                    {evaluation.market_opportunity.score}/100
                  </div>
                  <p className="metric-details">{evaluation.market_opportunity.details}</p>
                </div>

                <div className="metric-card">
                  <h4>🚀 Product Traction</h4>
                  <div className="metric-score" style={{ color: getScoreColor(evaluation.product_traction.score) }}>
                    {evaluation.product_traction.score}/100
                  </div>
                  <p className="metric-details">{evaluation.product_traction.details}</p>
                </div>

                <div className="metric-card">
                  <h4>⚠️ Risk Assessment</h4>
                  <div className="metric-score" style={{ color: getScoreColor(100 - evaluation.risk_assessment.score) }}>
                    {evaluation.risk_assessment.score}/100
                  </div>
                  <p className="metric-details">{evaluation.risk_assessment.details}</p>
                </div>

                <div className="metric-card">
                  <h4>📊 Peer Comparison</h4>
                  <div className="metric-score">
                    {evaluation.peer_comparison.vs_avg}
                  </div>
                  <p className="metric-details">Sector Average: {evaluation.peer_comparison.sector_avg}/100</p>
                </div>
              </div>

              {evaluation.raw_analysis && (
                <div className="ai-analysis-section">
                  <h3>🧠 Detailed AI Analysis</h3>
                  <div className="analysis-content">
                    <p>{evaluation.raw_analysis}</p>
                  </div>
                </div>
              )}

              <div className="action-buttons">
                <button 
                  className="analyze-another-btn" 
                  onClick={resetUpload}
                >
                  🔄 Analyze Another Document
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Platform Information - At BOTTOM */}
      <div className="platform-info">
        <div className="container">
          {/* Hero Section */}
          <section className="hero-section">
            <h1>AI-Powered Startup Evaluator</h1>
            <h2>Comprehensive Investment Analysis Using Google Cloud Platform</h2>
            <p>Upload pitch decks, financial documents, or founder profiles for comprehensive AI-powered investment analysis powered by Google Cloud Platform's advanced AI infrastructure including Vertex AI Gemini, Cloud Vision API, and BigQuery analytics.</p>
          </section>

          {/* AI Capabilities Section */}
          <section className="capabilities-section">
            <h2>🔬 Advanced AI Analysis Capabilities</h2>
            <p>Built on Google Cloud Platform's enterprise-grade AI infrastructure</p>
            
            <div className="capabilities-grid">
              <div className="capability-card">
                <div className="capability-icon">🔍</div>
                <h3>Smart Document Intelligence Engine</h3>
                <p>AI-powered document extraction using Cloud Vision + Gemini</p>
                <ul>
                  <li>OCR processing of pitch decks and financial documents</li>
                  <li>Structured data extraction using Gemini 2.0 Pro</li>
                  <li>Financial metrics parsing and validation</li>
                  <li>Founder and team information extraction</li>
                </ul>
              </div>

              <div className="capability-card">
                <div className="capability-icon">📊</div>
                <h3>Comparative Benchmarking System</h3>
                <p>Sector-wise performance analysis using BigQuery analytics</p>
                <ul>
                  <li>Peer comparison across sector metrics</li>
                  <li>Percentile ranking calculations</li>
                  <li>Revenue multiple analysis</li>
                  <li>Team efficiency benchmarking</li>
                </ul>
              </div>

              <div className="capability-card">
                <div className="capability-icon">⚠️</div>
                <h3>AI Risk Assessment Module</h3>
                <p>Automated red flag detection and investment scoring</p>
                <ul>
                  <li>Multi-factor risk scoring algorithm</li>
                  <li>Financial consistency analysis</li>
                  <li>Market validation assessment</li>
                  <li>Investment readiness evaluation</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Processing Pipeline Section */}
          <section className="pipeline-section">
            <h2>🤖 AI Processing Pipeline</h2>
            <p>Analyzing your document with Google Cloud Platform AI services</p>
            
            <div className="pipeline-steps">
              <div className="pipeline-step">
                <div className="step-icon">📤</div>
                <h4>Uploading to Cloud Storage</h4>
                <p>Securely uploading document to GCS bucket</p>
              </div>
              <div className="pipeline-step">
                <div className="step-icon">👁️</div>
                <h4>Extracting text with Cloud Vision</h4>
                <p>OCR processing to extract text and structured data</p>
              </div>
              <div className="pipeline-step">
                <div className="step-icon">🤖</div>
                <h4>Processing with Gemini AI</h4>
                <p>Advanced AI analysis using Gemini 2.0 for data extraction</p>
              </div>
              <div className="pipeline-step">
                <div className="step-icon">📊</div>
                <h4>Calculating investment score</h4>
                <p>Multi-factor analysis and peer comparison</p>
              </div>
              <div className="pipeline-step">
                <div className="step-icon">💾</div>
                <h4>Storing in BigQuery</h4>
                <p>Saving results to data warehouse</p>
              </div>
            </div>
          </section>

          {/* GCP Architecture Section */}
          <section className="architecture-section">
            <h2>🏗️ Powered by Google Cloud Platform</h2>
            <p>Enterprise-grade AI infrastructure for reliable startup evaluation built with Cloud Shell Editor workflow</p>
            
            <div className="gcp-services">
              <div className="service-card">
                <div className="service-icon">💻</div>
                <h4>Cloud Shell Editor</h4>
                <p>Complete development environment with integrated terminal and file management</p>
              </div>
              <div className="service-card">
                <div className="service-icon">👁️</div>
                <h4>Cloud Vision API</h4>
                <p>Document OCR processing and text extraction with high accuracy</p>
              </div>
              <div className="service-card">
                <div className="service-icon">🤖</div>
                <h4>Vertex AI Gemini</h4>
                <p>Advanced AI model for structured data extraction and analysis</p>
              </div>
              <div className="service-card">
                <div className="service-icon">🗄️</div>
                <h4>BigQuery</h4>
                <p>Enterprise data warehouse for analytics and peer benchmarking</p>
              </div>
              <div className="service-card">
                <div className="service-icon">💾</div>
                <h4>Cloud Storage</h4>
                <p>Secure document storage and processing pipeline</p>
              </div>
              <div className="service-card">
                <div className="service-icon">☁️</div>
                <h4>Cloud Run</h4>
                <p>Serverless container deployment for MCP server</p>
              </div>
              <div className="service-card">
                <div className="service-icon">🔥</div>
                <h4>Firebase Hosting</h4>
                <p>Fast, secure web hosting with global CDN</p>
              </div>
            </div>

            <div className="deployment-info">
              <h3>🔧 Technical Architecture & Deployment</h3>
              <div className="deployment-grid">
                <div className="deployment-item">
                  <strong>Development:</strong> Cloud Shell Editor with integrated terminal and file management
                </div>
                <div className="deployment-item">
                  <strong>Backend:</strong> FastAPI MCP Server deployed on Cloud Run
                </div>
                <div className="deployment-item">
                  <strong>Frontend:</strong> React TypeScript application hosted on Firebase
                </div>
                <div className="deployment-item">
                  <strong>Data Storage:</strong> BigQuery for analytics, Cloud Storage for documents
                </div>
                <div className="deployment-item">
                  <strong>AI Processing:</strong> Vertex AI Gemini + Cloud Vision API
                </div>
                <div className="deployment-item">
                  <strong>Security:</strong> Service account authentication, HTTPS-only communication
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>

    </div>
  );
};

export default App;