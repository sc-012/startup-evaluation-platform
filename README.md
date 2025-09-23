# AI-Powered Startup Evaluation Platform

A comprehensive AI-powered startup evaluation platform built on Google Cloud Platform that analyzes startup documents and generates investment insights.

## Features

### Smart Document Intelligence Engine
- **Cloud Vision OCR**: Extract text from pitch decks, financial documents
- **Gemini 2.0 Pro**: AI-powered structured data extraction and validation
- **Multi-format Support**: PDF, JPEG, PNG documents up to 10MB

### Comparative Benchmarking System  
- **BigQuery Analytics**: Sector-wise peer comparison and performance metrics
- **Percentile Ranking**: Performance tier classification against industry peers
- **Efficiency Analysis**: Team productivity and revenue multiple calculations

### AI Risk Assessment Module
- **Multi-factor Analysis**: Financial, market, team, competitive, and growth risks
- **Red Flag Detection**: Automated identification of investment concerns
- **Investment Recommendations**: AI-generated decision support with rationale

## Architecture

```
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ React Frontend  │ │ FastAPI MCP      │ │ GCP Services    │
│ (Firebase)      │◄──►│ Server (Cloud Run)│◄──►│ BigQuery/Vision │
└─────────────────┘ └──────────────────┘ └─────────────────┘
```

## Quick Deployment

### Prerequisites
- Google Cloud Project with billing enabled
- GitHub account
- `gcloud` CLI installed and authenticated

### Automated Deployment
```bash
# Run the automated deployment script
./quick-deploy.sh
```

### Manual Deployment
Follow the detailed guide in `GITHUB_DEPLOYMENT_GUIDE.md`

## Project Structure

```
startup-evaluator/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── mcp_server.py          # Main server logic
│   ├── requirements.txt       # Python dependencies
│   ├── startup_dataset.json   # Sample data
│   └── Dockerfile            # Container configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StartupEvaluator.tsx
│   │   │   └── StartupEvaluator.css
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── firebase.json
│   └── .firebaserc
├── cloudbuild.yaml            # CI/CD pipeline
├── .gitignore
└── README.md
```

## Tech Stack

- **Frontend**: React 18 + TypeScript + CSS3
- **Backend**: Python 3.11 + FastAPI + Uvicorn
- **AI/ML**: Vertex AI Gemini 2.0 + Cloud Vision API
- **Database**: BigQuery + Cloud Firestore
- **Storage**: Cloud Storage
- **Deployment**: Cloud Run + Firebase Hosting
- **CI/CD**: Cloud Build + GitHub Actions

## Usage

### PDF Upload & Analysis
1. Navigate to the deployed frontend URL
2. **Upload Document**: Click "Upload PDF" or drag-and-drop files
3. **AI Processing**: Real-time pipeline with 5 processing steps:
   - Upload to Cloud Storage
   - OCR with Cloud Vision
   - Data extraction with Gemini
   - Investment scoring
   - Storage in BigQuery
4. **Results Dashboard**: Comprehensive evaluation with metrics and recommendations


## Access URLs

After deployment:
- **Frontend**: `https://startup-evaluator-frontend-166437193095.asia-south1.run.app/`
- **Backend API**: `https://startup-evaluator-backend-166437193095.asia-south1.run.app/`
- **API Documentation**: `https://startup-evaluator-backend-166437193095.asia-south1.run.app/docs`
- **Health Check**: `https://startup-evaluator-backend-166437193095.asia-south1.run.app/health`

## Management Commands

```bash
# View logs
gcloud run services logs tail startup-evaluator-backend --region=us-central1

# Update deployment
gcloud run services update startup-evaluator-backend --region=us-central1

# Scale service
gcloud run services update startup-evaluator-backend \
    --region=us-central1 \
    --min-instances=1 \
    --max-instances=10
```

## Security

- **Environment Variables**: NO hardcoded values in backend code
- **Service Account Authentication**: Least-privilege access patterns
- **HTTPS-only Communication**: Secure data transmission
- **Input Validation**: File type and size restrictions
- **Error Handling**: Comprehensive logging and error recovery

## Performance

- **Serverless Scaling**: Auto-scaling Cloud Run instances
- **Processing Time**: 1-2 minutes per document
- **File Support**: PDF, JPEG, PNG up to 10MB
- **Concurrent Users**: Up to 10 simultaneous evaluations
- **Response Time**: <5 seconds for API calls

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- **Google Cloud Platform** for comprehensive AI/ML services
- **Vertex AI Team** for Gemini integration and advanced AI capabilities
- **Firebase Team** for seamless hosting and deployment solutions

---

**Built exclusively with Google Cloud Platform services**

For support and questions, please check the API documentation at `/docs` endpoint or review the deployment logs.
