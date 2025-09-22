#!/bin/bash

# Complete Deployment Script for AI-Powered Startup Evaluation Platform
set -e

echo "🚀 Starting complete deployment of AI-Powered Startup Evaluation Platform"

# Set variables
export PROJECT_ID="startup-ai-evaluator-$(date +%s | tail -c 6)"
export REGION="asia-south1"
export DATASET_ID="startup_evaluation"
export BUCKET_NAME="${PROJECT_ID}-startup-docs"

echo "📋 Project Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Dataset: $DATASET_ID"
echo "  Bucket: $BUCKET_NAME"

# Create GCP project
echo "🏗️ Creating GCP project..."
gcloud projects create $PROJECT_ID --name="AI Startup Evaluator"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com

# Create BigQuery dataset
echo "📊 Creating BigQuery dataset..."
bq mk --dataset $PROJECT_ID:$DATASET_ID

# Create Cloud Storage bucket
echo "🗄️ Creating Cloud Storage bucket..."
gsutil mb gs://$BUCKET_NAME

# Deploy backend
echo "🔧 Deploying backend..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/startup-evaluator-backend backend/
gcloud run deploy startup-evaluator-backend \
  --image gcr.io/$PROJECT_ID/startup-evaluator-backend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars PROJECT_ID=$PROJECT_ID,REGION=$REGION,DATASET_ID=$DATASET_ID

# Deploy frontend
echo "🎨 Deploying frontend..."
cd frontend
npm install
npm run build
cd ..

gcloud builds submit --tag gcr.io/$PROJECT_ID/startup-evaluator-frontend frontend/
gcloud run deploy startup-evaluator-frontend \
  --image gcr.io/$PROJECT_ID/startup-evaluator-frontend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1

echo "✅ Deployment complete!"
echo "🌐 Backend URL: https://startup-evaluator-backend-$(gcloud config get-value project | cut -d- -f4).$REGION.run.app"
echo "🌐 Frontend URL: https://startup-evaluator-frontend-$(gcloud config get-value project | cut -d- -f4).$REGION.run.app"
