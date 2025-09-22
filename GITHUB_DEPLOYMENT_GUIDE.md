# 🚀 Complete GitHub + Google Cloud Deployment Guide

## 📋 Quick Start (5 Minutes)

### Option 1: Automated Deployment
```bash
# Run the automated deployment script
./quick-deploy.sh
```

### Option 2: Manual Step-by-Step
Follow the detailed steps below.

## 🏗️ Architecture

```
GitHub Repository → Cloud Build → Google Cloud Platform
     ↓                ↓              ↓
  Source Code    CI/CD Pipeline   Cloud Run + Firebase
```

## 📁 Project Structure

```
startup-evaluator/
├── backend/
│   ├── mcp_server_fixed.py      # Fixed FastAPI server
│   ├── requirements.txt         # Python dependencies
│   ├── startup_dataset.json     # Sample data
│   └── Dockerfile              # Container configuration
├── frontend/
│   ├── StartupEvaluator_fixed.tsx  # Fixed React component
│   ├── StartupEvaluator.css    # Styling
│   ├── package.json           # Node.js dependencies
│   ├── index.html             # HTML template
│   ├── style.css              # Additional styles
│   ├── firebase.json          # Firebase configuration
│   └── .firebaserc            # Firebase project config
├── .github/workflows/
│   └── deploy.yml             # GitHub Actions workflow
├── cloudbuild.yaml            # Cloud Build configuration
├── .gitignore                 # Git ignore rules
├── deploy-github.sh           # Manual deployment script
├── quick-deploy.sh            # Automated deployment script
└── DEPLOYMENT.md              # Detailed deployment guide
```

## 🚀 Step-by-Step Deployment

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Repository name: `startup-evaluator`
3. Description: `AI-Powered Startup Evaluation Platform`
4. Make it **Public** (for easier setup)
5. **Don't** initialize with README, .gitignore, or license

### Step 2: Push Your Code

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: AI-Powered Startup Evaluation Platform

Features:
✅ Document Intelligence Engine (Cloud Vision + Gemini)
✅ Comparative Benchmarking System (BigQuery analytics)
✅ AI Risk Assessment Module (Multi-factor analysis)
✅ FastAPI MCP Server (Cloud Run deployment)
✅ React TypeScript Frontend (Firebase Hosting)
✅ Complete CI/CD pipeline

Stack: GCP • Python • React • TypeScript • BigQuery • Gemini AI"

# Set main branch
git branch -M main

# Add remote origin (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/startup-evaluator.git

# Push to GitHub
git push -u origin main
```

### Step 3: Setup Google Cloud Platform

#### 3.1 Create Project
```bash
# Set your project ID
export PROJECT_ID="startup-ai-evaluator-$(date +%s)"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Link billing account (replace with your billing ID)
gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID
```

#### 3.2 Enable APIs
```bash
gcloud services enable \
    aiplatform.googleapis.com \
    vision.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    firebase.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com
```

#### 3.3 Create Service Accounts
```bash
# Create main service account
gcloud iam service-accounts create startup-evaluator \
    --display-name="AI Startup Evaluator Service Account"

# Create Cloud Build service account
gcloud iam service-accounts create cloud-build-sa \
    --display-name="Cloud Build Service Account"

# Grant roles to main service account
for role in "roles/aiplatform.user" "roles/vision.admin" "roles/bigquery.admin" \
           "roles/storage.admin" "roles/firebase.admin" "roles/run.developer" \
           "roles/cloudbuild.builds.builder" "roles/containerregistry.writer"
do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role"
done

# Grant roles to Cloud Build service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

### Step 4: Setup Data Infrastructure

#### 4.1 BigQuery Database
```bash
# Create dataset
bq mk --dataset $PROJECT_ID:startup_evaluation

# Create tables
bq query --use_legacy_sql=false <<EOF
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.startups\` (
    startup_id STRING NOT NULL,
    company_name STRING,
    sector STRING,
    stage STRING,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    document_source STRING
);

CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.financial_data\` (
    startup_id STRING NOT NULL,
    arr_crore FLOAT64,
    mrr_lakh FLOAT64,
    valuation_pre_money_crore FLOAT64,
    team_size INT64,
    funding_raised_crore FLOAT64,
    revenue_model STRING
);

CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.evaluations\` (
    startup_id STRING NOT NULL,
    investment_score INT64,
    risk_level STRING,
    overall_risk_score FLOAT64,
    analysis_confidence FLOAT64,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.risk_assessments\` (
    startup_id STRING NOT NULL,
    red_flags ARRAY<STRING>,
    recommendations ARRAY<STRING>,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
EOF
```

#### 4.2 Cloud Storage
```bash
# Create bucket
gsutil mb gs://$PROJECT_ID-startup-docs

# Set permissions
gsutil iam ch serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-startup-docs
```

### Step 5: Setup Firebase

```bash
# Login to Firebase
firebase login --no-localhost

# Initialize Firebase hosting
firebase init hosting --project $PROJECT_ID --public build --single-page-app true

# Update .firebaserc with your project ID
echo '{"projects":{"default":"'$PROJECT_ID'"}}' > frontend/.firebaserc
```

### Step 6: Setup CI/CD Pipeline

#### Option A: Cloud Build (Recommended)
```bash
# Create Cloud Build trigger
gcloud builds triggers create github \
    --repo-name=startup-evaluator \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=$PROJECT_ID
```

#### Option B: GitHub Actions
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Service account key (JSON)
   - `FIREBASE_SERVICE_ACCOUNT`: Firebase service account key
   - `BACKEND_URL`: Your backend URL (will be set after first deployment)

### Step 7: Deploy Initial Version

```bash
# Submit initial build
gcloud builds submit --config cloudbuild.yaml .
```

## 🔗 Access Your Application

After deployment, you'll have:

- **Frontend**: `https://$PROJECT_ID.web.app`
- **Backend API**: Check Cloud Run console for URL
- **API Documentation**: `[Backend URL]/docs`
- **Health Check**: `[Backend URL]/health`

## 🔄 Continuous Deployment

Once set up, every push to the `main` branch will automatically:

1. **Build** the backend Docker image
2. **Deploy** backend to Cloud Run
3. **Build** the frontend React app
4. **Deploy** frontend to Firebase Hosting

## 🛠️ Management Commands

### View Build Logs
```bash
gcloud builds log --stream
```

### View Service Logs
```bash
gcloud run services logs tail startup-evaluator-backend --region=us-central1
```

### Update Environment Variables
```bash
gcloud run services update startup-evaluator-backend \
    --region=us-central1 \
    --set-env-vars="NEW_VAR=value"
```

### Scale Service
```bash
gcloud run services update startup-evaluator-backend \
    --region=us-central1 \
    --min-instances=1 \
    --max-instances=10
```

## 🔒 Security Best Practices

1. **Never commit** service account keys to GitHub
2. **Use Secret Manager** for sensitive environment variables
3. **Configure CORS** properly for production
4. **Implement authentication** for production use
5. **Enable audit logging** for compliance

## 🐛 Troubleshooting

### Common Issues

1. **Build Fails**: Check Cloud Build logs
2. **API Not Working**: Verify service account permissions
3. **Frontend Not Loading**: Check Firebase configuration
4. **BigQuery Errors**: Ensure tables exist and permissions are correct

### Debug Commands

```bash
# Check service status
gcloud run services describe startup-evaluator-backend --region=us-central1

# Check BigQuery tables
bq ls $PROJECT_ID:startup_evaluation

# Check Cloud Storage
gsutil ls gs://$PROJECT_ID-startup-docs

# Check build triggers
gcloud builds triggers list
```

## 📊 Monitoring Setup

1. **Cloud Monitoring**: Set up alerts for service health
2. **Cloud Logging**: Monitor application logs
3. **Error Reporting**: Track and analyze errors
4. **Performance Monitoring**: Monitor API response times

## 🎯 Next Steps

1. **Test the deployment** with sample documents
2. **Set up monitoring** and alerting
3. **Implement authentication** for production
4. **Add more AI models** for enhanced analysis
5. **Scale infrastructure** based on usage

## 📞 Support

- **GitHub Issues**: Create issues in your repository
- **GCP Console**: Check service status and logs
- **Documentation**: Review API docs at `/docs` endpoint

---

## 🎉 Congratulations!

Your AI-Powered Startup Evaluation Platform is now deployed and ready to analyze startup documents using Google Cloud Platform's advanced AI services!

**Key Features Deployed:**
- ✅ Smart Document Intelligence Engine
- ✅ Comparative Benchmarking System  
- ✅ AI Risk Assessment Module
- ✅ Complete CI/CD Pipeline
- ✅ Scalable Cloud Infrastructure

**Ready to analyze startup documents and generate investment insights!** 🚀
