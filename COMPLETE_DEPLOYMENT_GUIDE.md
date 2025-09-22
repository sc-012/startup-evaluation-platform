# 🚀 Complete GitHub + Google Cloud Deployment Guide

## 📋 Prerequisites

### 1. Google Cloud Setup
- [ ] Google Cloud Project with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Required APIs enabled (see below)

### 2. GitHub Setup
- [ ] GitHub account
- [ ] Git installed locally
- [ ] GitHub CLI (optional but recommended)

### 3. Local Development Environment
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Docker installed (for local testing)

---

## 🔧 Step 1: Google Cloud Project Setup

### 1.1 Create and Configure Project
```bash
# Set your project ID (replace with your actual project ID)
export PROJECT_ID="startup-ai-evaluator-$(date +%s)"
export REGION="us-central1"

# Create new project
gcloud projects create $PROJECT_ID --name="Startup AI Evaluator"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (you'll need to do this manually in the console)
echo "Please enable billing for project: $PROJECT_ID"
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
```

### 1.2 Enable Required APIs
```bash
# Enable all required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    vision.googleapis.com \
    aiplatform.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    firebase.googleapis.com \
    firebasehosting.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com

echo "✅ All APIs enabled successfully!"
```

### 1.3 Create Service Account
```bash
# Create service account
gcloud iam service-accounts create startup-evaluator-sa \
    --display-name="Startup Evaluator Service Account" \
    --description="Service account for startup evaluation platform"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/vision.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download service account key
gcloud iam service-accounts keys create service-account.json \
    --iam-account=startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com

echo "✅ Service account created and key downloaded!"
```

---

## 🗄️ Step 2: Database and Storage Setup

### 2.1 Create BigQuery Dataset
```bash
# Create BigQuery dataset
bq mk --dataset \
    --location=US \
    $PROJECT_ID:startup_evaluation

echo "✅ BigQuery dataset created!"
```

### 2.2 Create Cloud Storage Bucket
```bash
# Create storage bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-startup-docs

echo "✅ Cloud Storage bucket created!"
```

---

## 📱 Step 3: GitHub Repository Setup

### 3.1 Initialize Git Repository
```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI-Powered Startup Evaluation Platform"

# Add remote origin (replace with your GitHub username)
read -p "Enter your GitHub username: " GITHUB_USERNAME
git remote add origin https://github.com/$GITHUB_USERNAME/startup-evaluation-platform.git

echo "✅ Git repository initialized!"
```

### 3.2 Create GitHub Repository
```bash
# Create repository on GitHub (requires GitHub CLI)
gh repo create startup-evaluation-platform \
    --public \
    --description="AI-Powered Startup Evaluation Platform on Google Cloud" \
    --source=. \
    --remote=origin \
    --push

echo "✅ GitHub repository created and pushed!"
```

### 3.3 Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GCP_SA_KEY`: Contents of your `service-account.json` file
- `GCP_REGION`: `us-central1`

---

## 🚀 Step 4: Deploy Backend (Cloud Run)

### 4.1 Build and Deploy Backend
```bash
# Build and deploy backend using Cloud Build
gcloud builds submit --config cloudbuild.yaml backend/ \
    --substitutions=_PROJECT_ID=$PROJECT_ID,_REGION=$REGION

echo "✅ Backend deployed to Cloud Run!"
```

### 4.2 Get Backend URL
```bash
# Get the backend service URL
BACKEND_URL=$(gcloud run services describe startup-evaluator-backend \
    --region=$REGION \
    --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"
```

---

## 🎨 Step 5: Deploy Frontend (Firebase Hosting)

### 5.1 Initialize Firebase
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase project
firebase init hosting --project $PROJECT_ID

# Select existing project and configure:
# - Public directory: frontend/build
# - Single-page app: Yes
# - GitHub auto-builds: Yes
```

### 5.2 Build and Deploy Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variable for backend URL
export REACT_APP_MCP_SERVER_URL=$BACKEND_URL

# Build the React app
npm run build

# Deploy to Firebase
firebase deploy --project $PROJECT_ID

cd ..
echo "✅ Frontend deployed to Firebase Hosting!"
```

### 5.3 Get Frontend URL
```bash
# Get the frontend URL
FRONTEND_URL=$(firebase hosting:sites:list --project $PROJECT_ID --json | jq -r '.[0].defaultUrl')

echo "Frontend URL: $FRONTEND_URL"
```

---

## 🔄 Step 6: Setup CI/CD Pipeline

### 6.1 GitHub Actions Workflow
The `.github/workflows/deploy.yml` file is already configured. It will:
- Build and deploy backend on push to main
- Build and deploy frontend on push to main
- Run tests and linting

### 6.2 Test CI/CD Pipeline
```bash
# Make a small change and push to trigger deployment
echo "# Updated $(date)" >> README.md
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main

echo "✅ CI/CD pipeline triggered!"
```

---

## 🧪 Step 7: Test End-to-End Functionality

### 7.1 Test Backend API
```bash
# Test health endpoint
curl $BACKEND_URL/health

# Test with sample data
curl -X POST "$BACKEND_URL/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### 7.2 Test Frontend
1. Open your frontend URL in browser
2. Upload a sample PDF document
3. Verify the evaluation process works
4. Check that results are displayed correctly

### 7.3 Verify Data Storage
```bash
# Check BigQuery tables
bq ls $PROJECT_ID:startup_evaluation

# Check Cloud Storage files
gsutil ls gs://$PROJECT_ID-startup-docs/
```

---

## 📊 Step 8: Monitor and Scale

### 8.1 Monitor Logs
```bash
# View backend logs
gcloud run services logs tail startup-evaluator-backend --region=$REGION

# View build logs
gcloud builds log --region=$REGION
```

### 8.2 Scale Services
```bash
# Scale backend for production
gcloud run services update startup-evaluator-backend \
    --region=$REGION \
    --min-instances=1 \
    --max-instances=10 \
    --cpu=2 \
    --memory=4Gi

echo "✅ Backend scaled for production!"
```

---

## 🔒 Step 9: Security and Production Setup

### 9.1 Configure CORS
Update the backend CORS settings in `backend/mcp_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.web.app"],  # Replace with actual URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 9.2 Set up Custom Domain (Optional)
```bash
# Add custom domain to Firebase Hosting
firebase hosting:channel:deploy production --project $PROJECT_ID
```

### 9.3 Enable Monitoring
```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Set up alerts for errors and performance
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml
```

---

## 🎯 Final Verification Checklist

- [ ] ✅ Backend deployed and accessible at Cloud Run URL
- [ ] ✅ Frontend deployed and accessible at Firebase URL
- [ ] ✅ BigQuery dataset created with proper tables
- [ ] ✅ Cloud Storage bucket created and accessible
- [ ] ✅ Service account has proper permissions
- [ ] ✅ GitHub Actions CI/CD pipeline working
- [ ] ✅ End-to-end document upload and analysis working
- [ ] ✅ Results displayed correctly in frontend
- [ ] ✅ Data stored in BigQuery
- [ ] ✅ Logs accessible and error-free

---

## 🚨 Troubleshooting

### Common Issues:

1. **Permission Denied Errors**
   ```bash
   # Re-authenticate
   gcloud auth login
   gcloud auth application-default login
   ```

2. **API Not Enabled**
   ```bash
   # Enable specific API
   gcloud services enable [API_NAME]
   ```

3. **Build Failures**
   ```bash
   # Check build logs
   gcloud builds log [BUILD_ID]
   ```

4. **CORS Issues**
   - Update CORS settings in backend
   - Ensure frontend URL is correct

5. **Service Account Issues**
   ```bash
   # Recreate service account key
   gcloud iam service-accounts keys create new-key.json \
       --iam-account=startup-evaluator-sa@$PROJECT_ID.iam.gserviceaccount.com
   ```

---

## 📞 Support

- **Google Cloud Console**: https://console.cloud.google.com
- **Firebase Console**: https://console.firebase.google.com
- **GitHub Actions**: Check your repository's Actions tab
- **API Documentation**: Visit `https://your-backend-url/docs`

---

## 🎉 Congratulations!

Your AI-Powered Startup Evaluation Platform is now live on Google Cloud Platform! 

**Access URLs:**
- **Frontend Dashboard**: `https://your-project-id.web.app`
- **Backend API**: `https://startup-evaluator-backend-xxxxx.uc.r.appspot.com`
- **API Docs**: `https://your-backend-url/docs`

The platform is now ready to analyze startup documents and provide AI-powered investment insights!
