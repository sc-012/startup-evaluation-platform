#!/bin/bash

# 🚀 Deployment Script for Existing GCP Project
# This script deploys to an existing project with billing enabled

set -e

echo "🚀 AI-POWERED STARTUP EVALUATION PLATFORM - DEPLOYMENT TO EXISTING PROJECT"
echo "=========================================================================="
echo ""

# Set project ID to existing project
export PROJECT_ID="omega-terrain-472716-c4"
export REGION="asia-south1"
export GITHUB_USERNAME="testuser"
export GITHUB_REPO="$GITHUB_USERNAME/startup-evaluator"

echo "📋 Configuration:"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "GitHub Repo: $GITHUB_REPO"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Step 1: Enable APIs
echo "📡 Step 1: Enabling APIs..."
gcloud services enable \
    aiplatform.googleapis.com \
    vision.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    firebase.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com \
    iam.googleapis.com \
    firebasehosting.googleapis.com

# Step 2: Create Service Accounts
echo "👤 Step 2: Creating service accounts..."
gcloud iam service-accounts create startup-evaluator \
    --display-name="AI Startup Evaluator Service Account" \
    --description="Service account for startup evaluation platform"

gcloud iam service-accounts create cloud-build-sa \
    --display-name="Cloud Build Service Account" \
    --description="Service account for Cloud Build operations"

# Grant roles to main service account
for role in \
    "roles/aiplatform.user" \
    "roles/vision.admin" \
    "roles/bigquery.admin" \
    "roles/storage.admin" \
    "roles/firebase.admin" \
    "roles/run.developer" \
    "roles/cloudbuild.builds.builder" \
    "roles/containerregistry.writer" \
    "roles/secretmanager.secretAccessor" \
    "roles/iam.serviceAccountUser"
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

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

# Step 3: Setup BigQuery
echo "🗄️ Step 3: Setting up BigQuery..."
bq mk --dataset --location=US $PROJECT_ID:startup_evaluation

# Create BigQuery tables
bq query --use_legacy_sql=false --project_id=$PROJECT_ID <<EOF
-- Startups master table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.startups\` (
    startup_id STRING NOT NULL,
    company_name STRING,
    sector STRING,
    stage STRING,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    document_source STRING
);

-- Financial metrics table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.financial_data\` (
    startup_id STRING NOT NULL,
    arr_crore FLOAT64,
    mrr_lakh FLOAT64,
    valuation_pre_money_crore FLOAT64,
    team_size INT64,
    funding_raised_crore FLOAT64,
    revenue_model STRING
);

-- Evaluations table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.evaluations\` (
    startup_id STRING NOT NULL,
    investment_score INT64,
    risk_level STRING,
    overall_risk_score FLOAT64,
    analysis_confidence FLOAT64,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Risk assessments table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.risk_assessments\` (
    startup_id STRING NOT NULL,
    red_flags ARRAY<STRING>,
    recommendations ARRAY<STRING>,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
EOF

# Step 4: Setup Cloud Storage
echo "💾 Step 4: Setting up Cloud Storage..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-startup-docs
gsutil iam ch serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-startup-docs

# Step 5: Setup Firebase
echo "🔥 Step 5: Setting up Firebase..."
firebase login --no-localhost
firebase init hosting --project $PROJECT_ID --public build --single-page-app true

# Update .firebaserc
echo '{"projects":{"default":"'$PROJECT_ID'"}}' > frontend/.firebaserc

# Step 6: Initialize Git Repository
echo "🐙 Step 6: Setting up Git repository..."
git init
git add .
git commit -m "Initial commit: AI-Powered Startup Evaluation Platform

Features:
✅ Document Intelligence Engine (Cloud Vision + Gemini)
✅ Comparative Benchmarking System (BigQuery analytics)
✅ AI Risk Assessment Module (Multi-factor analysis)
✅ FastAPI MCP Server (Cloud Run deployment)
✅ React TypeScript Frontend (Firebase Hosting)
✅ Complete CI/CD pipeline

Stack: GCP • Python • React • TypeScript • BigQuery • Gemini AI"

git branch -M main
git remote add origin https://github.com/$GITHUB_REPO.git

# Step 7: Deploy Backend
echo "🚀 Step 7: Deploying backend..."
gcloud builds submit --config cloudbuild.yaml backend/ \
    --substitutions=_PROJECT_ID=$PROJECT_ID,_REGION=$REGION

# Get backend URL
BACKEND_URL=$(gcloud run services describe startup-evaluator-backend \
    --region=$REGION \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"

# Step 8: Deploy Frontend
echo "🎨 Step 8: Deploying frontend..."
cd frontend

# Install dependencies
npm install

# Set environment variable
export REACT_APP_MCP_SERVER_URL=$BACKEND_URL
echo "REACT_APP_MCP_SERVER_URL=$BACKEND_URL" > .env

# Build and deploy
npm run build
firebase deploy --project $PROJECT_ID

cd ..

# Get frontend URL
FRONTEND_URL="https://$PROJECT_ID.web.app"
echo "Frontend URL: $FRONTEND_URL"

# Step 9: Setup CI/CD Pipeline
echo "🔧 Step 9: Setting up CI/CD pipeline..."
gcloud builds triggers create github \
    --repo-name=startup-evaluator \
    --repo-owner=$GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=$PROJECT_ID

# Step 10: Push to GitHub
echo "📤 Step 10: Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Your AI-Powered Startup Evaluation Platform is now deployed!"
echo ""
echo "🔗 Access URLs:"
echo "• Frontend: $FRONTEND_URL"
echo "• Backend API: $BACKEND_URL"
echo "• API Documentation: $BACKEND_URL/docs"
echo "• Health Check: $BACKEND_URL/health"
echo ""
echo "📋 Next Steps:"
echo "1. Test the platform by uploading a sample PDF"
echo "2. Check Cloud Build console for any issues"
echo "3. Monitor logs: gcloud run services logs tail startup-evaluator-backend --region=$REGION"
echo "4. Scale if needed: gcloud run services update startup-evaluator-backend --region=$REGION --min-instances=1 --max-instances=10"
echo ""
echo "🎯 Your platform is ready for startup document analysis!"
