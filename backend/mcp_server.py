from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import vision, storage, bigquery, aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel
import uvicorn
import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
import os
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Startup Evaluator MCP Server",
    description="Secure MCP server for AI-powered startup evaluation using GCP services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# GCP Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "startup-ai-evaluator")
REGION = os.getenv("REGION", "us-central1")
DATASET_ID = os.getenv("DATASET_ID", "startup_evaluation")
BUCKET_NAME = f"{PROJECT_ID}-startup-docs"

# Models
class EvaluationResponse(BaseModel):
    startup_id: str
    timestamp: str
    extracted_data: Dict[str, Any]
    investment_score: int
    risk_level: str
    recommendations: list
    document_source: str
    sector_comparison: Dict[str, Any]  # Added missing field
    risk_assessment: Dict[str, Any]    # Added missing field

class StartupData(BaseModel):
    company_name: Optional[str] = None
    sector: Optional[str] = None
    stage: Optional[str] = None
    arr_crore: Optional[float] = None
    team_size: Optional[int] = None
    valuation_pre_money_crore: Optional[float] = None

# Initialize GCP clients
@app.on_event("startup")
async def startup_event():
    """Initialize GCP services on startup."""
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)
        vertexai.init(project=PROJECT_ID, location=REGION)

        # Initialize clients
        app.state.vision_client = vision.ImageAnnotatorClient()
        app.state.storage_client = storage.Client(project=PROJECT_ID)
        app.state.bq_client = bigquery.Client(project=PROJECT_ID)
        app.state.model = GenerativeModel("gemini-1.5-pro")  # Consistent model name

        # Ensure bucket exists with proper region
        try:
            bucket = app.state.storage_client.bucket(BUCKET_NAME)
            if not bucket.exists():
                bucket = app.state.storage_client.create_bucket(BUCKET_NAME, location=REGION)
                logger.info(f"Created bucket: {BUCKET_NAME}")
        except Exception as e:
            logger.warning(f"Bucket setup issue: {e}")

        # Ensure BigQuery dataset and tables exist
        try:
            dataset_ref = app.state.bq_client.dataset(DATASET_ID)
            try:
                app.state.bq_client.get_dataset(dataset_ref)
            except:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = REGION
                app.state.bq_client.create_dataset(dataset)
                logger.info(f"Created dataset: {DATASET_ID}")
                
                # Create tables
                await create_bigquery_tables()
        except Exception as e:
            logger.warning(f"BigQuery setup issue: {e}")

        logger.info("GCP services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize GCP services: {str(e)}")
        raise

async def create_bigquery_tables():
    """Create BigQuery tables with proper schema."""
    tables_schema = {
        "startups": [
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_name", "STRING"),
            bigquery.SchemaField("sector", "STRING"),
            bigquery.SchemaField("stage", "STRING"),
            bigquery.SchemaField("processed_at", "TIMESTAMP"),
            bigquery.SchemaField("document_source", "STRING"),
        ],
        "financial_data": [
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("arr_crore", "FLOAT"),
            bigquery.SchemaField("mrr_lakh", "FLOAT"),
            bigquery.SchemaField("valuation_pre_money_crore", "FLOAT"),
            bigquery.SchemaField("team_size", "INTEGER"),
            bigquery.SchemaField("funding_raised_crore", "FLOAT"),
            bigquery.SchemaField("revenue_model", "STRING"),
        ],
        "evaluations": [
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("investment_score", "INTEGER"),
            bigquery.SchemaField("risk_level", "STRING"),
            bigquery.SchemaField("overall_risk_score", "FLOAT"),
            bigquery.SchemaField("analysis_confidence", "FLOAT"),
            bigquery.SchemaField("processed_at", "TIMESTAMP"),
        ],
        "risk_assessments": [
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("red_flags", "STRING", mode="REPEATED"),
            bigquery.SchemaField("recommendations", "STRING", mode="REPEATED"),
            bigquery.SchemaField("assessment_date", "TIMESTAMP"),
        ]
    }

    for table_name, schema in tables_schema.items():
        try:
            table_ref = app.state.bq_client.dataset(DATASET_ID).table(table_name)
            table = bigquery.Table(table_ref, schema=schema)
            app.state.bq_client.create_table(table, exists_ok=True)
            logger.info(f"Created/verified table: {table_name}")
        except Exception as e:
            logger.warning(f"Table creation issue for {table_name}: {e}")

# Authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify authentication token."""
    token = credentials.credentials

    # For demo purposes - implement proper JWT validation in production
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication token"
        )

    return token

# Core Functions
async def upload_to_gcs(file: UploadFile) -> str:
    """Upload file to Google Cloud Storage."""
    try:
        bucket = app.state.storage_client.bucket(BUCKET_NAME)

        # Generate unique blob name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"uploads/{timestamp}_{file.filename}"
        blob = bucket.blob(blob_name)

        # Upload file content
        content = await file.read()
        blob.upload_from_string(content, content_type=file.content_type)

        gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"
        logger.info(f"File uploaded to: {gcs_uri}")

        return gcs_uri

    except Exception as e:
        logger.error(f"GCS upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

async def extract_text_from_document(gcs_uri: str) -> str:
    """Extract text from document using Cloud Vision API."""
    try:
        image = vision.Image()
        image.source.image_uri = gcs_uri

        response = app.state.vision_client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")

        if not response.full_text_annotation:
            return "No text found in document"

        text = response.full_text_annotation.text
        logger.info(f"Extracted {len(text)} characters of text")

        return text

    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

async def extract_startup_data(text: str) -> Dict[str, Any]:
    """Extract structured startup data using Gemini."""
    try:
        # Limit text for token efficiency
        text_sample = text[:8000] if len(text) > 8000 else text

        prompt = f"""
        TASK: Extract startup metrics from this document and return ONLY valid JSON.

        DOCUMENT TEXT:
        {text_sample}

        REQUIRED JSON FORMAT:
        {{
            "company_name": "string or null",
            "sector": "string or null",
            "stage": "Pre-Seed/Seed/Series A/Series B/etc or null",
            "arr_crore": float or null,
            "mrr_lakh": float or null,
            "valuation_pre_money_crore": float or null,
            "team_size": int or null,
            "funding_raised_crore": float or null,
            "revenue_model": "string or null",
            "founders": ["list of names"] or [],
            "key_metrics": {{"metric": "value"}} or {{}}
        }}

        INSTRUCTIONS:
        - Extract numerical values carefully (convert lakhs/crores)
        - If information not found, use null
        - Return ONLY the JSON object, no explanation
        - Ensure all required fields are present
        """

        response = app.state.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "top_p": 0.8,
                "max_output_tokens": 1024
            }
        )

        # Parse JSON response
        json_text = response.text.strip()
        json_text = re.sub(r'^```json\s*', '', json_text)
        json_text = re.sub(r'\s*```$', '', json_text)

        data = json.loads(json_text)
        logger.info(f"Extracted data for company: {data.get('company_name', 'Unknown')}")

        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        # Return fallback data structure
        return {
            "company_name": "Extracted Company",
            "sector": "Unknown",
            "stage": "Unknown",
            "arr_crore": None,
            "mrr_lakh": None,
            "valuation_pre_money_crore": None,
            "team_size": None,
            "funding_raised_crore": None,
            "revenue_model": "Unknown",
            "founders": [],
            "key_metrics": {}
        }

    except Exception as e:
        logger.error(f"Gemini processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")

async def calculate_investment_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate investment score and risk assessment."""
    try:
        score = 50  # Base score
        risk_factors = []
        recommendations = []

        # Performance scoring
        arr = data.get('arr_crore', 0) or 0
        team_size = data.get('team_size', 0) or 0
        valuation = data.get('valuation_pre_money_crore', 0) or 0

        # ARR-based scoring
        if arr > 10:
            score += 25
        elif arr > 5:
            score += 20
        elif arr > 1:
            score += 10
        elif arr == 0:
            risk_factors.append("🔴 No current ARR")
            recommendations.append("📋 Focus on revenue generation strategy")
            score -= 10

        # Team efficiency analysis
        if team_size > 0 and arr > 0:
            efficiency = arr / team_size
            if efficiency > 0.3:
                score += 15
            elif efficiency > 0.1:
                score += 5
            elif efficiency < 0.05:
                score -= 15
                risk_factors.append("⚠️ Low team efficiency detected")

        # Valuation multiple check
        if arr > 0 and valuation > 0:
            multiple = valuation / arr
            if multiple > 20:
                score -= 10
                risk_factors.append("🔴 High valuation multiple")
            elif multiple < 5:
                score += 5

        # Stage appropriateness
        stage = data.get('stage', '').lower()
        if 'series a' in stage and arr < 1:
            risk_factors.append("🔴 Stage-ARR mismatch for Series A")
            score -= 20
        elif 'series b' in stage and arr < 5:
            risk_factors.append("🔴 Stage-ARR mismatch for Series B")
            score -= 20

        # Risk level calculation
        final_score = max(0, min(100, score))

        if final_score >= 75:
            risk_level = "Low"
        elif final_score >= 50:
            risk_level = "Medium"
        elif final_score >= 30:
            risk_level = "Medium-High"
        else:
            risk_level = "High"

        # Calculate percentile (simplified)
        arr_percentile = min(90, max(10, 50 + (arr - 1) * 10))  # Simplified calculation

        return {
            "investment_score": final_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "overall_risk_score": 100 - final_score,
            "arr_percentile": arr_percentile,
            "performance_tier": "Top Performer" if arr_percentile >= 75 else "Average",
            "team_efficiency": arr / team_size if team_size > 0 else 0,
            "analysis_confidence": 0.8
        }

    except Exception as e:
        logger.error(f"Investment calculation failed: {str(e)}")
        return {
            "investment_score": 50,
            "risk_level": "Medium",
            "risk_factors": ["⚠️ Analysis incomplete"],
            "recommendations": ["📋 Manual review required"],
            "overall_risk_score": 50,
            "arr_percentile": 50,
            "performance_tier": "Unknown",
            "team_efficiency": 0,
            "analysis_confidence": 0.5
        }

async def store_in_bigquery(startup_id: str, data: Dict[str, Any], analysis: Dict[str, Any]):
    """Store evaluation results in BigQuery."""
    try:
        dataset_ref = app.state.bq_client.dataset(DATASET_ID)

        # Prepare records for different tables
        startup_row = {
            "startup_id": startup_id,
            "company_name": data.get("company_name"),
            "sector": data.get("sector"),
            "stage": data.get("stage"),
            "processed_at": datetime.now().isoformat()
        }

        financial_row = {
            "startup_id": startup_id,
            "arr_crore": data.get("arr_crore"),
            "mrr_lakh": data.get("mrr_lakh"),
            "valuation_pre_money_crore": data.get("valuation_pre_money_crore"),
            "team_size": data.get("team_size"),
            "funding_raised_crore": data.get("funding_raised_crore"),
            "revenue_model": data.get("revenue_model")
        }

        evaluation_row = {
            "startup_id": startup_id,
            "investment_score": analysis.get("investment_score"),
            "risk_level": analysis.get("risk_level"),
            "overall_risk_score": analysis.get("overall_risk_score"),
            "analysis_confidence": analysis.get("analysis_confidence"),
            "processed_at": datetime.now().isoformat()
        }

        risk_row = {
            "startup_id": startup_id,
            "red_flags": analysis.get("risk_factors", []),
            "recommendations": analysis.get("recommendations", []),
            "assessment_date": datetime.now().isoformat()
        }

        # Insert into BigQuery tables
        tables_data = [
            ("startups", [startup_row]),
            ("financial_data", [financial_row]),
            ("evaluations", [evaluation_row]),
            ("risk_assessments", [risk_row])
        ]

        for table_name, rows in tables_data:
            try:
                table_ref = dataset_ref.table(table_name)
                table = app.state.bq_client.get_table(table_ref)

                # Clean None values for BigQuery compatibility
                cleaned_rows = []
                for row in rows:
                    cleaned_row = {k: v for k, v in row.items() if v is not None}
                    cleaned_rows.append(cleaned_row)

                errors = app.state.bq_client.insert_rows_json(table, cleaned_rows)

                if errors:
                    logger.warning(f"BigQuery insert errors for {table_name}: {errors}")

            except Exception as table_error:
                logger.warning(f"Failed to insert into {table_name}: {str(table_error)}")

        logger.info(f"Data stored in BigQuery for startup: {startup_id}")

    except Exception as e:
        logger.error(f"BigQuery storage failed: {str(e)}")
        # Don't raise exception - continue with response even if storage fails

# API Endpoints
@app.post("/evaluate", response_model=EvaluationResponse, tags=["Evaluation"])
async def evaluate_startup(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """
    Main startup evaluation endpoint.

    Upload a startup document (PDF, image) and receive comprehensive AI analysis.
    """

    # Validate file
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file.content_type}. Allowed: {allowed_types}"
        )

    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail="File too large. Maximum size: 10MB"
        )

    try:
        # Generate unique startup ID
        startup_id = hashlib.md5(f"{file.filename}_{datetime.now()}".encode()).hexdigest()[:12]

        # Step 1: Upload to Cloud Storage
        gcs_uri = await upload_to_gcs(file)

        # Step 2: Extract text using Cloud Vision
        extracted_text = await extract_text_from_document(gcs_uri)

        # Step 3: Extract structured data using Gemini
        startup_data = await extract_startup_data(extracted_text)

        # Step 4: Calculate investment metrics
        analysis = await calculate_investment_metrics(startup_data)

        # Step 5: Store in BigQuery (background task)
        background_tasks.add_task(store_in_bigquery, startup_id, startup_data, analysis)

        # Prepare response with all required fields
        response = EvaluationResponse(
            startup_id=startup_id,
            timestamp=datetime.now().isoformat(),
            extracted_data=startup_data,
            investment_score=analysis["investment_score"],
            risk_level=analysis["risk_level"],
            recommendations=analysis["recommendations"],
            document_source=gcs_uri,
            sector_comparison={
                "arr_percentile": analysis["arr_percentile"],
                "performance_tier": analysis["performance_tier"],
                "team_efficiency": analysis["team_efficiency"]
            },
            risk_assessment={
                "overall_risk_score": analysis["overall_risk_score"],
                "risk_level": analysis["risk_level"],
                "red_flags": analysis["risk_factors"],
                "recommendations": analysis["recommendations"]
            }
        )

        logger.info(f"Evaluation completed for startup: {startup_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Evaluation failed: {str(e)}"
        )

@app.get("/startup/{startup_id}", tags=["Data Retrieval"])
async def get_startup_details(
    startup_id: str, 
    token: str = Depends(verify_token)
):
    """Retrieve detailed information about a previously evaluated startup."""

    try:
        # Query BigQuery for startup data
        query = f"""
        SELECT 
            s.*,
            f.arr_crore,
            f.team_size,
            f.valuation_pre_money_crore,
            e.investment_score,
            e.risk_level
        FROM `{PROJECT_ID}.{DATASET_ID}.startups` s
        LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.financial_data` f ON s.startup_id = f.startup_id
        LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.evaluations` e ON s.startup_id = e.startup_id
        WHERE s.startup_id = @startup_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id)
            ]
        )

        result = list(app.state.bq_client.query(query, job_config=job_config))

        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Startup {startup_id} not found"
            )

        return {
            "startup_id": startup_id,
            "data": dict(result[0]),
            "retrieved_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Data retrieval failed: {str(e)}"
        )

@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "startup-evaluator-mcp",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "region": REGION,
        "features": [
            "Document Intelligence Engine",
            "Comparative Benchmarking", 
            "AI Risk Assessment"
        ]
    }

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI-Powered Startup Evaluation Platform",
        "description": "Secure MCP server for comprehensive startup analysis using Google Cloud Platform",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "powered_by": "Google Cloud Platform",
        "features": {
            "document_processing": "Cloud Vision + Gemini AI",
            "data_storage": "BigQuery + Cloud Storage",
            "risk_assessment": "Multi-factor AI analysis",
            "security": "Token-based authentication",
            "deployment": "Cloud Run serverless"
        }
    }

# Main application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
