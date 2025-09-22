# 🚀 AI-Powered Startup Evaluation Platform - GitHub + GCP Deployment Guide

This guide will walk you through deploying the AI-Powered Startup Evaluation Platform on Google Cloud Platform using GitHub for version control and CI/CD.

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] GitHub account
- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] `git` installed locally
- [ ] `firebase` CLI installed (`npm install -g firebase-tools`)

## 🏗️ Architecture Overview

```
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ GitHub Repo     │ │ Cloud Build      │ │ GCP Services    │
│ (Source Code)   │◄──►│ (CI/CD Pipeline)│◄──►│ Cloud Run/Firebase │
└─────────────────┘ └──────────────────┘ └─────────────────┘
```

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Codebase

1. **Organize your files** (already done):
   ```
   startup-evaluator/
   ├── backend/
   │   ├── mcp_server_fixed.py
   │   ├── requirements.txt
   │   ├── startup_dataset.json
   │   └── Dockerfile
   ├── frontend/
   │   ├── StartupEvaluator_fixed.tsx
   │   ├── StartupEvaluator.css
   │   ├── package.json
   │   ├── index.html
   │   ├── style.css
   │   ├── firebase.json
   │   └── .firebaserc
   ├── cloudbuild.yaml
   ├── .gitignore
   └── deploy-github.sh
   ```

2. **Initialize Git repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI-Powered Startup Evaluation Platform"
   ```

### Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `startup-evaluator`
3. Make it public or private (your choice)
4. **Don't** initialize with README, .gitignore, or license (we already have these)

### Step 3: Push Code to GitHub

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/startup-evaluator.git
git push -u origin main
```

### Step 4: Setup Google Cloud Platform

1. **Create GCP Project**:
   ```bash
   export PROJECT_ID="startup-ai-evaluator-$(date +%s)"
   gcloud projects create $PROJECT_ID
   gcloud config set project $PROJECT_ID
   ```

2. **Link Billing Account**:
   ```bash
   gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID
   ```

3. **Enable Required APIs**:
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

### Step 5: Create Service Accounts

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

### Step 6: Setup BigQuery Database

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

### Step 7: Setup Cloud Storage

```bash
# Create bucket
gsutil mb gs://$PROJECT_ID-startup-docs

# Set permissions
gsutil iam ch serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-startup-docs
```

### Step 8: Setup Firebase

```bash
# Login to Firebase
firebase login --no-localhost

# Initialize Firebase hosting
firebase init hosting --project $PROJECT_ID --public build --single-page-app true

# Update .firebaserc with your project ID
echo '{"projects":{"default":"'$PROJECT_ID'"}}' > frontend/.firebaserc
```

### Step 9: Setup Cloud Build Triggers

```bash
# Create Cloud Build trigger
gcloud builds triggers create github \
    --repo-name=startup-evaluator \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=$PROJECT_ID
```

### Step 10: Deploy Initial Version

```bash
# Submit initial build
gcloud builds submit --config cloudbuild.yaml .
```

## 🔧 Configuration Files

### cloudbuild.yaml
This file defines the CI/CD pipeline that:
1. Builds and deploys the backend to Cloud Run
2. Builds and deploys the frontend to Firebase Hosting
3. Runs automatically on every push to main branch

### Environment Variables
The following environment variables are automatically set:
- `PROJECT_ID`: Your GCP project ID
- `REGION`: us-central1
- `DATASET_ID`: startup_evaluation

## 🚀 Deployment Process

Once everything is set up:

1. **Make changes** to your code
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. **Cloud Build automatically**:
   - Builds your backend Docker image
   - Deploys backend to Cloud Run
   - Builds your frontend React app
   - Deploys frontend to Firebase Hosting

## 🔗 Access Your Application

After deployment, you'll have access to:

- **Frontend**: `https://$PROJECT_ID.web.app`
- **Backend API**: `https://startup-evaluator-backend-xxxxx.uc.r.appspot.com`
- **API Documentation**: `https://startup-evaluator-backend-xxxxx.uc.r.appspot.com/docs`
- **Health Check**: `https://startup-evaluator-backend-xxxxx.uc.r.appspot.com/health`

## 🛠️ Management Commands

### View Build Logs
```bash
gcloud builds log --stream
```

### View Cloud Run Logs
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

## 🔒 Security Considerations

1. **Service Account Keys**: Never commit service account keys to GitHub
2. **Environment Variables**: Use Google Secret Manager for sensitive data
3. **CORS**: Configure CORS properly for production
4. **Authentication**: Implement proper JWT authentication
5. **HTTPS**: All communication is HTTPS-only

## 🐛 Troubleshooting

### Common Issues

1. **Build Fails**: Check Cloud Build logs for specific errors
2. **API Not Working**: Verify environment variables and service account permissions
3. **Frontend Not Loading**: Check Firebase hosting configuration
4. **BigQuery Errors**: Ensure tables exist and service account has proper permissions

### Debug Commands

```bash
# Check service status
gcloud run services describe startup-evaluator-backend --region=us-central1

# Check BigQuery tables
bq ls $PROJECT_ID:startup_evaluation

# Check Cloud Storage bucket
gsutil ls gs://$PROJECT_ID-startup-docs
```

## 📊 Monitoring

Set up monitoring for:
- Cloud Run service health
- BigQuery query performance
- Cloud Storage usage
- API response times
- Error rates

## 🎯 Next Steps

1. **Test the deployment** with sample documents
2. **Set up monitoring** and alerting
3. **Implement authentication** for production use
4. **Add more AI models** for enhanced analysis
5. **Scale the infrastructure** based on usage

## 📞 Support

For issues or questions:
1. Check the logs using the commands above
2. Review the API documentation at `/docs` endpoint
3. Check Google Cloud Console for service status
4. Review the GitHub repository for latest updates

---

**🎉 Congratulations! Your AI-Powered Startup Evaluation Platform is now deployed and ready to analyze startup documents!**
