#!/bin/bash

# 🚀 Quick Deployment Script for AI-Powered Startup Evaluation Platform
# This script automates the entire deployment process

set -e

echo "🚀 AI-POWERED STARTUP EVALUATION PLATFORM - QUICK DEPLOYMENT"
echo "============================================================="
echo ""

# Get user inputs
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your GCP billing account ID: " BILLING_ACCOUNT
read -p "Enter your desired project ID (or press Enter for auto-generated): " PROJECT_ID_INPUT

# Set project ID
if [ -z "$PROJECT_ID_INPUT" ]; then
    export PROJECT_ID="startup-ai-evaluator-$(date +%s)"
else
    export PROJECT_ID="$PROJECT_ID_INPUT"
fi

export REGION="us-central1"
export GITHUB_REPO="$GITHUB_USERNAME/startup-evaluator"

echo ""
echo "📋 Configuration:"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "GitHub Repo: $GITHUB_REPO"
echo ""

# Step 1: Create GCP Project
echo "🔧 Step 1: Creating GCP project..."
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT

# Step 2: Enable APIs
echo "📡 Step 2: Enabling APIs..."
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

# Grant roles
for role in "roles/aiplatform.user" "roles/vision.admin" "roles/bigquery.admin" \
           "roles/storage.admin" "roles/firebase.admin" "roles/run.developer" \
           "roles/cloudbuild.builds.builder" "roles/containerregistry.writer"
do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role"
done

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Step 4: Setup BigQuery
echo "🗄️ Step 4: Setting up BigQuery..."
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

# Step 5: Setup Cloud Storage
echo "💾 Step 5: Setting up Cloud Storage..."
gsutil mb gs://$PROJECT_ID-startup-docs
gsutil iam ch serviceAccount:startup-evaluator@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$PROJECT_ID-startup-docs

# Step 6: Setup Firebase
echo "🔥 Step 6: Setting up Firebase..."
firebase login --no-localhost
firebase init hosting --project $PROJECT_ID --public build --single-page-app true

# Update .firebaserc
echo '{"projects":{"default":"'$PROJECT_ID'"}}' > frontend/.firebaserc

# Step 7: Setup Cloud Build Trigger
echo "🔧 Step 7: Setting up Cloud Build trigger..."
gcloud builds triggers create github \
    --repo-name=startup-evaluator \
    --repo-owner=$GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=$PROJECT_ID

# Step 8: Deploy Initial Version
echo "🚀 Step 8: Deploying initial version..."
gcloud builds submit --config cloudbuild.yaml .

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Your AI-Powered Startup Evaluation Platform is now deployed!"
echo ""
echo "🔗 Access URLs:"
echo "• Frontend: https://$PROJECT_ID.web.app"
echo "• Backend API: Check Cloud Run console for URL"
echo "• API Documentation: [Backend URL]/docs"
echo ""
echo "📋 Next Steps:"
echo "1. Create GitHub repository: https://github.com/new"
echo "2. Repository name: startup-evaluator"
echo "3. Push your code:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/$GITHUB_REPO.git"
echo "   git push -u origin main"
echo ""
echo "4. Cloud Build will automatically deploy on every push to main"
echo "5. Update frontend environment variables with actual backend URL"
echo ""
echo "🎯 Your platform is ready for startup document analysis!"
