#!/bin/bash

# 🚀 AI-POWERED STARTUP EVALUATION PLATFORM - GITHUB + GCP DEPLOYMENT
# Complete deployment script for GitHub integration with Google Cloud Platform

set -e

echo "🚀 AI-POWERED STARTUP EVALUATION PLATFORM - GITHUB + GCP DEPLOYMENT"
echo "=================================================================="
echo "This script will deploy your platform using GitHub and Google Cloud Platform"
echo ""

# Configuration
export PROJECT_ID="${PROJECT_ID:-startup-ai-evaluator-$(date +%s)}"
export REGION="${REGION:-us-central1}"
export GITHUB_REPO="${GITHUB_REPO:-your-username/startup-evaluator}"

echo "📋 Configuration:"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "GitHub Repo: $GITHUB_REPO"
echo ""

# Step 1: Create GCP Project
echo "🔧 Step 1: Setting up GCP project..."
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Link billing account (replace with your billing ID)
read -p "Enter your billing account ID: " BILLING_ACCOUNT
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT

# Step 2: Enable APIs
echo "📡 Step 2: Enabling required APIs..."
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

# Step 3: Create Service Accounts
echo "👤 Step 3: Creating service accounts..."
gcloud iam service-accounts create startup-evaluator \
    --display-name="AI Startup Evaluator Service Account"

gcloud iam service-accounts create cloud-build-sa \
    --display-name="Cloud Build Service Account"

# Grant roles to service accounts
for role in "roles/aiplatform.user" "roles/vision.admin" "roles/bigquery.admin" \
           "roles/storage.admin" "roles/firebase.admin" "roles/run.developer" \
           "roles/cloudbuild.builds.builder" "roles/containerregistry.writer"
do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role"
done

# Grant Cloud Build roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Step 4: Setup BigQuery
echo "🗄️ Step 4: Setting up BigQuery..."
bq mk --dataset $PROJECT_ID:startup_evaluation

# Create BigQuery tables
bq query --use_legacy_sql=false <<EOF
-- Create startups master table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.startups\` (
    startup_id STRING NOT NULL,
    company_name STRING,
    sector STRING,
    stage STRING,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    document_source STRING
);

-- Create financial metrics table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.financial_data\` (
    startup_id STRING NOT NULL,
    arr_crore FLOAT64,
    mrr_lakh FLOAT64,
    valuation_pre_money_crore FLOAT64,
    team_size INT64,
    funding_raised_crore FLOAT64,
    revenue_model STRING
);

-- Create evaluations table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.evaluations\` (
    startup_id STRING NOT NULL,
    investment_score INT64,
    risk_level STRING,
    overall_risk_score FLOAT64,
    analysis_confidence FLOAT64,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Create risk assessments table
CREATE OR REPLACE TABLE \`$PROJECT_ID.startup_evaluation.risk_assessments\` (
    startup_id STRING NOT NULL,
    red_flags ARRAY<STRING>,
    recommendations ARRAY<STRING>,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
EOF

# Step 5: Setup Cloud Storage
echo "💾 Step 5: Setting up Cloud Storage..."
gsutil mb gs://$PROJECT_ID-startup-docs
gsutil iam ch serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-startup-docs

# Step 6: Setup Firebase
echo "🔥 Step 6: Setting up Firebase..."
firebase login --no-localhost
firebase init hosting --project $PROJECT_ID --public build --single-page-app true

# Step 7: Create GitHub Repository
echo "🐙 Step 7: Setting up GitHub repository..."
echo "Please create a new repository on GitHub with the name: startup-evaluator"
echo "Then run the following commands:"
echo ""
echo "git init"
echo "git add ."
echo "git commit -m 'Initial commit: AI-Powered Startup Evaluation Platform'"
echo "git branch -M main"
echo "git remote add origin https://github.com/$GITHUB_REPO.git"
echo "git push -u origin main"
echo ""

# Step 8: Setup Cloud Build Triggers
echo "🔧 Step 8: Setting up Cloud Build triggers..."
gcloud builds triggers create github \
    --repo-name=startup-evaluator \
    --repo-owner=$(echo $GITHUB_REPO | cut -d'/' -f1) \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=$PROJECT_ID

# Step 9: Create environment variables
echo "🔐 Step 9: Creating environment variables..."
gcloud secrets create startup-evaluator-config --data-file=- <<EOF
PROJECT_ID=$PROJECT_ID
REGION=$REGION
DATASET_ID=startup_evaluation
EOF

# Step 10: Deploy initial version
echo "🚀 Step 10: Deploying initial version..."
gcloud builds submit --config cloudbuild.yaml .

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Your AI-Powered Startup Evaluation Platform is now deployed!"
echo ""
echo "🔗 Access URLs:"
echo "• Frontend: https://$PROJECT_ID.web.app"
echo "• Backend API: https://startup-evaluator-backend-xxxxx.uc.r.appspot.com"
echo "• API Documentation: https://startup-evaluator-backend-xxxxx.uc.r.appspot.com/docs"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to GitHub repository"
echo "2. Cloud Build will automatically deploy on every push to main branch"
echo "3. Update frontend environment variables with actual backend URL"
echo "4. Test the complete deployment"
echo ""
echo "🎯 Your platform is ready for startup document analysis!"
