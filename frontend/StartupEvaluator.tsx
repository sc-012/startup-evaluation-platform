import React, { useState, useCallback, useRef } from 'react';
import axios from 'axios';
import './StartupEvaluator.css';

interface EvaluationResult {
  startup_id: string;
  timestamp: string;
  extracted_data: {
    company_name?: string;
    sector?: string;
    arr_crore?: number;
    team_size?: number;
    stage?: string;
    valuation_pre_money_crore?: number;
    revenue_model?: string;
    founders?: string[];
    key_metrics?: Record<string, any>;
  };
  sector_comparison: {
    arr_percentile?: number;
    performance_tier?: string;
    team_efficiency?: number;
  };
  risk_assessment: {
    overall_risk_score?: number;
    risk_level?: string;
    red_flags?: string[];
    recommendations?: string[];
  };
  investment_score: number;
  investment_recommendation?: string;
}

const StartupEvaluator: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [processingStep, setProcessingStep] = useState<number>(0);
  const [showSampleData, setShowSampleData] = useState<boolean>(true);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sample evaluation data from the analyzed dataset
  const sampleEvaluations: EvaluationResult[] = [
    {
      startup_id: "we360ai",
      timestamp: new Date().toISOString(),
      extracted_data: {
        company_name: "We360.ai",
        sector: "SaaS/Productivity",
        arr_crore: 6.8,
        team_size: 33,
        stage: "Pre-Series A",
        valuation_pre_money_crore: null,
        revenue_model: "B2B SaaS Subscription",
        founders: ["Founder 1", "Founder 2"],
        key_metrics: {
          paid_users: 28000,
          retention_rate: 96,
          gross_margin: 90,
          growth_rate: 66
        }
      },
      sector_comparison: {
        arr_percentile: 85,
        performance_tier: "Top Performer",
        team_efficiency: 0.206
      },
      risk_assessment: {
        overall_risk_score: 25.0,
        risk_level: "Low",
        red_flags: [],
        recommendations: [
          "📋 Continue international expansion strategy",
          "📋 Maintain high retention rates above 95%",
          "📋 Scale enterprise segment offerings"
        ]
      },
      investment_score: 88,
      investment_recommendation: "✅ **STRONG RECOMMEND** - Excellent SaaS metrics with 96% retention, 6.8Cr ARR, and profitable growth trajectory."
    },
    {
      startup_id: "drdoodley",
      timestamp: new Date().toISOString(),
      extracted_data: {
        company_name: "Dr. Doodley",
        sector: "HealthTech/Pet Care",
        arr_crore: null,
        team_size: 40,
        stage: "Seed",
        revenue_model: "Home visits, Hospital care, Diagnostics",
        founders: ["Founder A", "Founder B"],
        key_metrics: {
          revenue_6m: 1.65,
          pets_treated: 2050,
          hospitals: 2,
          doctors: 12
        }
      },
      sector_comparison: {
        arr_percentile: 45,
        performance_tier: "Average",
        team_efficiency: null
      },
      risk_assessment: {
        overall_risk_score: 45.0,
        risk_level: "Medium",
        red_flags: [
          "⚠️ Capital intensive hospital model",
          "⚠️ Limited scalability of home visits"
        ],
        recommendations: [
          "📋 Validate unit economics per hospital",
          "📋 Optimize home visit efficiency"
        ]
      },
      investment_score: 58,
      investment_recommendation: "🟡 **CONDITIONAL RECOMMEND** - Innovative pet healthcare model with good early traction, but scalability validation needed."
    },
    {
      startup_id: "cashvisory",
      timestamp: new Date().toISOString(),
      extracted_data: {
        company_name: "Cashvisory",
        sector: "FinTech",
        arr_crore: 0.0,
        team_size: 5,
        stage: "Pre-Seed",
        valuation_pre_money_crore: 8.0,
        revenue_model: "Advisory subscription, Insurance distribution",
        founders: ["Founder X", "Founder Y"],
        key_metrics: {
          users_acquired: 13000,
          total_aum: 12.8,
          ltv: 13000,
          cac: 1000
        }
      },
      sector_comparison: {
        arr_percentile: 25,
        performance_tier: "Early Stage",
        team_efficiency: 0.0
      },
      risk_assessment: {
        overall_risk_score: 65.0,
        risk_level: "Medium-High",
        red_flags: [
          "🔴 No current ARR despite 13K users",
          "🔴 Pre-revenue stage with high valuation"
        ],
        recommendations: [
          "📋 Focus on user monetization strategy",
          "📋 Validate revenue model with paying customers"
        ]
      },
      investment_score: 42,
      investment_recommendation: "🟡 **PROCEED WITH CAUTION** - Early stage fintech with strong user base but no revenue. Requires clear monetization plan."
    }
  ];

  const processingSteps = [
    { step: 1, title: "Uploading to Cloud Storage", icon: "📤" },
    { step: 2, title: "Extracting text with Cloud Vision", icon: "👁️" },
    { step: 3, title: "Processing with Gemini AI", icon: "🤖" },
    { step: 4, title: "Calculating investment score", icon: "📊" },
    { step: 5, title: "Storing in BigQuery", icon: "💾" }
  ];

  // File upload handling
  const handleFileUpload = useCallback(async () => {
    if (!file) {
      setError("Please select a file to upload");
      return;
    }

    setLoading(true);
    setError(null);
    setProcessingStep(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate processing steps
      for (let i = 1; i <= 5; i++) {
        setProcessingStep(i);
        await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
      }

      // Fixed: Use environment variable or fallback to localhost for development
      const MCP_SERVER_URL = process.env.REACT_APP_MCP_SERVER_URL || 
                            (process.env.NODE_ENV === 'development' ? 'http://localhost:8080' : 'YOUR_MCP_SERVER_URL');

      const response = await axios.post(
        `${MCP_SERVER_URL}/evaluate`,
        formData,
        {
          headers: {
            'Authorization': 'Bearer demo-token-2025',
            'Content-Type': 'multipart/form-data',
          },
          timeout: 120000, // 2 minute timeout
        }
      );

      setEvaluation(response.data);
      setShowSampleData(false);

    } catch (error: any) {
      console.error('Evaluation failed:', error);
      
      // Enhanced error handling
      let errorMessage = 'Evaluation failed. Please try again.';
      
      if (error.code === 'ECONNREFUSED') {
        errorMessage = 'Cannot connect to the server. Please check if the backend is running.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Authentication failed. Please check your credentials.';
      } else if (error.response?.status === 413) {
        errorMessage = 'File too large. Please upload a file smaller than 10MB.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
      setProcessingStep(0);
    }
  }, [file]);

  // Drag and drop handlers
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
      if (droppedFile.type === 'application/pdf' || droppedFile.type.startsWith('image/')) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a PDF or image file');
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  // Utility functions
  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#34A853';
    if (score >= 60) return '#FBBC04';
    if (score >= 40) return '#FF9800';
    return '#EA4335';
  };

  const getRiskLevelColor = (riskLevel: string): string => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return '#34A853';
      case 'medium': return '#FBBC04';
      case 'medium-high': return '#FF9800';
      case 'high': return '#EA4335';
      default: return '#9AA0A6';
    }
  };

  const formatCurrency = (value: number | null | undefined): string => {
    if (!value) return 'N/A';
    return `₹${value.toFixed(1)}Cr`;
  };

  const viewSampleEvaluation = (sampleEvaluation: EvaluationResult) => {
    setEvaluation(sampleEvaluation);
    setShowSampleData(false);
  };

  return (
    <div className="startup-evaluator">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>🚀 AI-Powered Startup Evaluation Platform</h1>
          <p className="header-subtitle">
            Comprehensive Investment Analysis Using Google Cloud Platform
          </p>
          <div className="header-stats">
            <div className="stat-item">
              <span className="stat-number">3</span>
              <span className="stat-label">Core AI Features</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">5+</span>
              <span className="stat-label">GCP Services</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">100%</span>
              <span className="stat-label">Cloud Native</span>
            </div>
          </div>
        </div>
      </header>

      {/* Core Features Showcase */}
      <section className="features-showcase">
        <div className="feature-cards">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Smart Document Intelligence Engine</h3>
            <p>AI-powered OCR and data extraction using Cloud Vision + Gemini</p>
            <ul>
              <li>Cloud Vision API processing</li>
              <li>Gemini 2.0 structured extraction</li>
              <li>Financial metrics parsing</li>
            </ul>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Comparative Benchmarking System</h3>
            <p>BigQuery-powered sector analysis and peer comparison</p>
            <ul>
              <li>Sector benchmarking</li>
              <li>Percentile rankings</li>
              <li>Performance metrics</li>
            </ul>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚠️</div>
            <h3>AI Risk Assessment Module</h3>
            <p>Multi-factor risk analysis and investment recommendations</p>
            <ul>
              <li>Red flag detection</li>
              <li>Investment scoring</li>
              <li>Due diligence recommendations</li>
            </ul>
          </div>
        </div>
      </section>

      {/* File Upload Section */}
      <section className="upload-section">
        <h2>📄 Upload Startup Document</h2>
        <p>Upload pitch decks, financial documents, or founder profiles for comprehensive AI analysis</p>

        <div
          className={`file-drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="file-input"
            accept=".pdf,image/*"
            onChange={handleFileChange}
          />

          <div className="upload-icon">📄</div>
          <div className="upload-text">
            {file ? (
              <div className="file-selected">
                <strong>{file.name}</strong>
                <span className="file-size">({(file.size / 1024 / 1024).toFixed(1)} MB)</span>
              </div>
            ) : (
              <div>
                <strong>Click to upload or drag and drop</strong>
                <br />
                PDF, JPEG, PNG files (Max 10MB)
              </div>
            )}
          </div>
        </div>

        <button 
          className="upload-btn"
          onClick={handleFileUpload}
          disabled={!file || loading}
        >
          {loading ? '⏳ Processing...' : '🚀 Start AI Analysis'}
        </button>

        {/* Processing Steps */}
        {loading && (
          <div className="processing-steps">
            <h3>Processing Pipeline</h3>
            <div className="steps-container">
              {processingSteps.map((step, index) => (
                <div
                  key={index}
                  className={`processing-step ${processingStep >= step.step ? 'active' : ''} ${processingStep === step.step ? 'current' : ''}`}
                >
                  <div className="step-icon">{step.icon}</div>
                  <div className="step-title">{step.title}</div>
                  {processingStep === step.step && <div className="step-spinner">⏳</div>}
                  {processingStep > step.step && <div className="step-complete">✅</div>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-section">
            <div className="error-message">
              <div className="error-icon">❌</div>
              <div className="error-content">
                <strong>Analysis Failed</strong>
                <p>{error}</p>
                {error.includes('Cannot connect') && (
                  <div className="error-help">
                    <p><strong>Development Mode:</strong> Make sure your backend server is running on localhost:8080</p>
                    <p><strong>Production Mode:</strong> Check your REACT_APP_MCP_SERVER_URL environment variable</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Sample Data Section */}
      {showSampleData && !evaluation && (
        <section className="sample-data-section">
          <h2>📊 Sample Analysis Results</h2>
          <p>Explore pre-analyzed startups from our dataset. Click on any company to view detailed analysis.</p>

          <div className="sample-cards">
            {sampleEvaluations.map((sample, index) => (
              <div 
                key={index}
                className="sample-card"
                onClick={() => viewSampleEvaluation(sample)}
              >
                <div className="sample-header">
                  <h3>{sample.extracted_data.company_name}</h3>
                  <span className="sector-tag">{sample.extracted_data.sector}</span>
                </div>
                <div className="sample-metrics">
                  <div className="sample-score" style={{ color: getScoreColor(sample.investment_score) }}>
                    {sample.investment_score}/100
                  </div>
                  <div className="sample-risk" style={{ color: getRiskLevelColor(sample.risk_assessment.risk_level || '') }}>
                    {sample.risk_assessment.risk_level} Risk
                  </div>
                </div>
                <div className="sample-details">
                  <span>ARR: {formatCurrency(sample.extracted_data.arr_crore)}</span>
                  <span>Team: {sample.extracted_data.team_size}</span>
                  <span>Stage: {sample.extracted_data.stage}</span>
                </div>
                <div className="view-analysis-btn">View Full Analysis →</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Results Section */}
      {evaluation && (
        <section className="results-section">
          <div className="results-header">
            <h2>📊 Analysis Complete</h2>
            <div className="analysis-timestamp">
              Analyzed on {new Date(evaluation.timestamp).toLocaleString()}
            </div>
            <button 
              className="back-btn"
              onClick={() => {
                setEvaluation(null);
                setShowSampleData(true);
                setFile(null);
              }}
            >
              ← Back to Upload
            </button>
          </div>

          <div className="score-card">
            <div className="company-info">
              <h3>{evaluation.extracted_data.company_name}</h3>
              <div className="company-meta">
                <span className="sector-tag">{evaluation.extracted_data.sector}</span>
                <span className="stage-tag">{evaluation.extracted_data.stage}</span>
              </div>
            </div>

            <div className="overall-score">
              <div 
                className="score-circle" 
                style={{ backgroundColor: getScoreColor(evaluation.investment_score) }}
              >
                <span className="score-value">{evaluation.investment_score}</span>
                <span className="score-max">/100</span>
              </div>
              <div className="score-label">Investment Score</div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">📈</span>
                <span className="metric-title">Performance</span>
              </div>
              <div className="metric-value">{evaluation.sector_comparison.arr_percentile || 'N/A'}%</div>
              <div className="metric-label">Sector Percentile</div>
              <div className="metric-subtitle">{evaluation.sector_comparison.performance_tier}</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">⚠️</span>
                <span className="metric-title">Risk</span>
              </div>
              <div 
                className="metric-value risk-badge"
                style={{ backgroundColor: getRiskLevelColor(evaluation.risk_assessment.risk_level || '') }}
              >
                {evaluation.risk_assessment.risk_level}
              </div>
              <div className="metric-label">Risk Assessment</div>
              <div className="metric-subtitle">Score: {evaluation.risk_assessment.overall_risk_score?.toFixed(1)}</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">💰</span>
                <span className="metric-title">Revenue</span>
              </div>
              <div className="metric-value">{formatCurrency(evaluation.extracted_data.arr_crore)}</div>
              <div className="metric-label">Annual Recurring Revenue</div>
              <div className="metric-subtitle">Team: {evaluation.extracted_data.team_size} members</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">⚡</span>
                <span className="metric-title">Efficiency</span>
              </div>
              <div className="metric-value">{evaluation.sector_comparison.team_efficiency?.toFixed(2) || 'N/A'}</div>
              <div className="metric-label">ARR per Employee</div>
              <div className="metric-subtitle">Productivity metric</div>
            </div>
          </div>

          {/* Investment Recommendation */}
          <div className="recommendation-section">
            <h3>💡 Investment Recommendation</h3>
            <div className="recommendation-content">
              <div className="recommendation-text">
                {evaluation.investment_recommendation || `Based on our analysis, this startup scores ${evaluation.investment_score}/100 with ${evaluation.risk_assessment.risk_level?.toLowerCase()} risk level.`}
              </div>
            </div>
          </div>

          {/* Risk Factors */}
          {evaluation.risk_assessment.red_flags && evaluation.risk_assessment.red_flags.length > 0 && (
            <div className="red-flags-section">
              <h3>🚨 Risk Factors & Red Flags</h3>
              <div className="red-flags-grid">
                {evaluation.risk_assessment.red_flags.map((flag, index) => (
                  <div key={index} className="red-flag-item">
                    {flag}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {evaluation.risk_assessment.recommendations && evaluation.risk_assessment.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h3>📋 Due Diligence Recommendations</h3>
              <div className="recommendations-grid">
                {evaluation.risk_assessment.recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <span className="recommendation-number">{index + 1}</span>
                    <span className="recommendation-text">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Metrics Details */}
          {evaluation.extracted_data.key_metrics && Object.keys(evaluation.extracted_data.key_metrics).length > 0 && (
            <div className="key-metrics-section">
              <h3>📊 Extracted Key Metrics</h3>
              <div className="key-metrics-grid">
                {Object.entries(evaluation.extracted_data.key_metrics).map(([key, value]) => (
                  <div key={key} className="key-metric">
                    <span className="key-metric-label">{key.replace(/_/g, ' ').toUpperCase()}</span>
                    <span className="key-metric-value">{typeof value === 'number' ? value.toLocaleString() : value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Startup ID */}
          <div className="startup-id-section">
            <small>Startup ID: {evaluation.startup_id}</small>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="gcp-services">
            <h4>🌐 Powered by Google Cloud Platform</h4>
            <div className="service-tags">
              <span className="service-tag">Cloud Vision</span>
              <span className="service-tag">Vertex AI Gemini</span>
              <span className="service-tag">BigQuery</span>
              <span className="service-tag">Cloud Storage</span>
              <span className="service-tag">Cloud Run</span>
              <span className="service-tag">Firebase</span>
            </div>
          </div>
          <div className="platform-info">
            <p>🚀 AI-Powered Startup Evaluation Platform | Built exclusively with GCP services</p>
            <p>Complete document intelligence, peer benchmarking, and risk assessment in one platform</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default StartupEvaluator;
