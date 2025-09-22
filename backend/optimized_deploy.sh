#!/bin/bash

# Optimized GCP Deployment Script for AI-Powered Startup Evaluation Platform
set -e

echo "🚀 Starting optimized GCP deployment..."

# Configuration
export PROJECT_ID="startup-evaluator-$(date +%s | tail -c 6)"
export REGION="asia-south1"
export DATASET_ID="startup_evaluation"
export BUCKET_NAME="${PROJECT_ID}-startup-docs"

echo "📋 Deployment Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Dataset: $DATASET_ID"
echo "  Bucket: $BUCKET_NAME"

# Step 1: Create and configure GCP project
echo "🏗️ Setting up GCP project..."
gcloud projects create $PROJECT_ID --name="AI Startup Evaluator"
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
echo "🔧 Enabling GCP APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Step 3: Create BigQuery dataset
echo "📊 Setting up BigQuery..."
bq mk --dataset $PROJECT_ID:$DATASET_ID

# Step 4: Create Cloud Storage bucket
echo "🗄️ Setting up Cloud Storage..."
gsutil mb gs://$BUCKET_NAME

# Step 5: Deploy Backend (Cloud Run)
echo "🔧 Deploying backend to Cloud Run..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/startup-evaluator-backend .

gcloud run deploy startup-evaluator-backend \
  --image gcr.io/$PROJECT_ID/startup-evaluator-backend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 1 \
  --set-env-vars PROJECT_ID=$PROJECT_ID,REGION=$REGION,DATASET_ID=$DATASET_ID,BUCKET_NAME=$BUCKET_NAME \
  --timeout 900

# Get backend URL
BACKEND_URL=$(gcloud run services describe startup-evaluator-backend --region=$REGION --format="value(status.url)")
echo "✅ Backend deployed: $BACKEND_URL"

# Step 6: Deploy Frontend (Cloud Run)
echo "🎨 Deploying frontend to Cloud Run..."
cd ../frontend

# Update backend URL in frontend
sed -i.bak "s|const BACKEND_URL = .*|const BACKEND_URL = '$BACKEND_URL';|g" src/App.tsx

# Build frontend
npm install
npm run build

# Create Dockerfile for frontend
cat > Dockerfile << 'DOCKERFILE'
FROM nginx:alpine
COPY build/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE

# Create nginx config
cat > nginx.conf << 'NGINX'
events {
    worker_connections 1024;
}
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;
    server {
        listen 8080;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
NGINX

# Deploy frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/startup-evaluator-frontend .

gcloud run deploy startup-evaluator-frontend \
  --image gcr.io/$PROJECT_ID/startup-evaluator-frontend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 5 \
  --min-instances 0

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe startup-evaluator-frontend --region=$REGION --format="value(status.url)")
echo "✅ Frontend deployed: $FRONTEND_URL"

# Step 7: Set up monitoring and logging
echo "📊 Setting up monitoring..."
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Step 8: Create service account for production
echo "🔐 Setting up service account..."
gcloud iam service-accounts create startup-evaluator-sa \
  --display-name="Startup Evaluator Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/vision.user"

echo "🎉 Deployment Complete!"
echo ""
echo "🌐 Application URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo ""
echo "📊 GCP Console:"
echo "  Project: https://console.cloud.google.com/home/dashboard?project=$PROJECT_ID"
echo "  Cloud Run: https://console.cloud.google.com/run?project=$PROJECT_ID"
echo "  BigQuery: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo "  Storage: https://console.cloud.google.com/storage?project=$PROJECT_ID"
echo ""
echo "🔧 Next Steps:"
echo "  1. Test the application at: $FRONTEND_URL"
echo "  2. Upload a PDF to test the evaluation"
echo "  3. Check logs in Cloud Run console"
echo "  4. Monitor costs in GCP Console"
