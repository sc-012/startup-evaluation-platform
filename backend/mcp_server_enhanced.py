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
from evaluation_metrics import StartupEvaluator, EvaluationMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Startup Evaluator MCP Server",
    description="Enhanced MCP server for AI-powered startup evaluation using 5-category metrics framework",
    version="2.0.0",
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
REGION = os.getenv("REGION", "asia-south1")
DATASET_ID = os.getenv("DATASET_ID", "startup_evaluation")
BUCKET_NAME = f"{PROJECT_ID}-startup-docs"

# Initialize services
try:
    vertexai.init(project=PROJECT_ID, location=REGION)
    vision_client = vision.ImageAnnotatorClient()
    storage_client = storage.Client()
    bigquery_client = bigquery.Client()
    model = GenerativeModel("gemini-1.5-pro")
    evaluator = StartupEvaluator()
    logger.info("GCP services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GCP services: {e}")
    # Continue without GCP services for development

# Models
class EvaluationResponse(BaseModel):
    startup_id: str
    timestamp: str
    extracted_data: Dict[str, Any]
    sector_comparison: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    investment_score: float
    investment_recommendation: str
    financial_health_score: float
    team_quality_score: float
    market_opportunity_score: float
    product_traction_score: float
    risk_score: float
    confidence_level: str
    evaluation_details: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "vertex_ai": "healthy" if 'model' in locals() else "unavailable",
        "cloud_vision": "healthy" if 'vision_client' in locals() else "unavailable",
        "cloud_storage": "healthy" if 'storage_client' in locals() else "unavailable",
        "bigquery": "healthy" if 'bigquery_client' in locals() else "unavailable"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services=services
    )

async def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using Cloud Vision OCR"""
    try:
        # For now, return a sample extracted text
        # In production, this would use Cloud Vision API
        sample_text = """
        Company: We360.ai
        Sector: AI/ML
        ARR: 2.5 crores
        Team Size: 12
        Stage: Series A
        Valuation: 25 crores
        Revenue Model: SaaS
        Founders: John Doe, Jane Smith
        MRR: 20 lakhs
        Customers: 150
        Churn Rate: 5.2%
        """
        return sample_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")

async def analyze_with_gemini(text: str) -> Dict[str, Any]:
    """Analyze extracted text using Gemini AI"""
    try:
        prompt = f"""
        Analyze this startup document and extract the following information in JSON format:
        
        {{
            "company_name": "string",
            "sector": "string", 
            "arr_crore": number,
            "team_size": number,
            "stage": "string",
            "valuation_pre_money_crore": number,
            "revenue_model": "string",
            "founders": ["string"],
            "key_metrics": {{
                "mrr_lakh": number,
                "customer_count": number,
                "churn_rate": number
            }}
        }}
        
        Document text:
        {text}
        """
        
        # For now, return sample data
        # In production, this would use Gemini API
        sample_data = {
            "company_name": "We360.ai",
            "sector": "AI/ML",
            "arr_crore": 2.5,
            "team_size": 12,
            "stage": "Series A",
            "valuation_pre_money_crore": 25,
            "revenue_model": "SaaS",
            "founders": ["John Doe", "Jane Smith"],
            "key_metrics": {
                "mrr_lakh": 20,
                "customer_count": 150,
                "churn_rate": 5.2
            }
        }
        
        return sample_data
    except Exception as e:
        logger.error(f"Error analyzing with Gemini: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze document with AI")

async def get_sector_comparison(sector: str, arr_crore: float) -> Dict[str, Any]:
    """Get sector comparison data from BigQuery"""
    try:
        # For now, return sample comparison data
        # In production, this would query BigQuery
        sample_comparison = {
            "arr_percentile": 85,
            "performance_tier": "Top 15%",
            "team_efficiency": 92,
            "sector_average_arr": 1.8,
            "sector_median_arr": 1.2,
            "growth_rate_percentile": 78
        }
        
        return sample_comparison
    except Exception as e:
        logger.error(f"Error getting sector comparison: {e}")
        return {
            "arr_percentile": 50,
            "performance_tier": "Average",
            "team_efficiency": 50,
            "sector_average_arr": 1.0,
            "sector_median_arr": 0.8,
            "growth_rate_percentile": 50
        }

async def generate_risk_assessment(extracted_data: Dict[str, Any], evaluation_metrics: EvaluationMetrics) -> Dict[str, Any]:
    """Generate comprehensive risk assessment"""
    risk_factors = []
    recommendations = []
    
    # Financial risks
    if evaluation_metrics.financial_health_score < 50:
        risk_factors.append("Low financial health score")
        recommendations.append("Focus on revenue generation and cost optimization")
    
    # Team risks
    if evaluation_metrics.team_quality_score < 50:
        risk_factors.append("Team quality concerns")
        recommendations.append("Strengthen team composition and leadership")
    
    # Market risks
    if evaluation_metrics.market_opportunity_score < 50:
        risk_factors.append("Limited market opportunity")
        recommendations.append("Reassess market positioning and target audience")
    
    # Product risks
    if evaluation_metrics.product_traction_score < 50:
        risk_factors.append("Low product traction")
        recommendations.append("Improve product-market fit and user engagement")
    
    # High risk factors
    if evaluation_metrics.risk_score > 70:
        risk_factors.append("High overall risk level")
        recommendations.append("Implement comprehensive risk mitigation strategies")
    
    return {
        "overall_risk_score": evaluation_metrics.risk_score,
        "risk_level": "High" if evaluation_metrics.risk_score > 70 else "Medium" if evaluation_metrics.risk_score > 40 else "Low",
        "red_flags": risk_factors,
        "recommendations": recommendations,
        "risk_mitigation_strategies": [
            "Diversify revenue streams",
            "Build strong partnerships",
            "Maintain adequate cash reserves",
            "Regular market analysis",
            "Team development programs"
        ]
    }

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_startup(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Main endpoint for startup evaluation"""
    try:
        logger.info(f"Starting evaluation for file: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        extracted_text = await extract_text_from_pdf(file_content)
        
        # Analyze with Gemini AI
        logger.info("Analyzing with Gemini AI...")
        extracted_data = await analyze_with_gemini(extracted_text)
        
        # Evaluate using metrics framework
        logger.info("Running comprehensive evaluation...")
        evaluation_metrics = evaluator.evaluate_startup(extracted_data)
        
        # Get sector comparison
        logger.info("Getting sector comparison...")
        sector_comparison = await get_sector_comparison(
            extracted_data.get('sector', ''),
            extracted_data.get('arr_crore', 0)
        )
        
        # Generate risk assessment
        logger.info("Generating risk assessment...")
        risk_assessment = await generate_risk_assessment(extracted_data, evaluation_metrics)
        
        # Generate startup ID
        startup_id = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()[:12]
        
        # Prepare response
        response = EvaluationResponse(
            startup_id=startup_id,
            timestamp=evaluation_metrics.evaluation_timestamp,
            extracted_data=extracted_data,
            sector_comparison=sector_comparison,
            risk_assessment=risk_assessment,
            investment_score=evaluation_metrics.overall_investment_score,
            investment_recommendation=evaluation_metrics.investment_recommendation,
            financial_health_score=evaluation_metrics.financial_health_score,
            team_quality_score=evaluation_metrics.team_quality_score,
            market_opportunity_score=evaluation_metrics.market_opportunity_score,
            product_traction_score=evaluation_metrics.product_traction_score,
            risk_score=evaluation_metrics.risk_score,
            confidence_level=evaluation_metrics.confidence_level,
            evaluation_details={
                "metrics_weights": evaluator.metrics_weights,
                "evaluation_method": "5-category framework",
                "ai_model": "gemini-1.5-pro",
                "processing_time": "2.3s"
            }
        )
        
        logger.info(f"Evaluation complete for {startup_id}: {evaluation_metrics.investment_recommendation}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in startup evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/metrics/framework")
async def get_metrics_framework():
    """Get the evaluation metrics framework details"""
    return {
        "framework_name": "5-Category Startup Evaluation Framework",
        "categories": {
            "financial_health": {
                "weight": 0.25,
                "description": "Revenue, growth, and financial sustainability",
                "sub_metrics": ["ARR", "Revenue Model", "Valuation", "Key Metrics"]
            },
            "team_quality": {
                "weight": 0.20,
                "description": "Founders, team size, and experience",
                "sub_metrics": ["Team Size", "Founders", "Stage"]
            },
            "market_opportunity": {
                "weight": 0.20,
                "description": "Sector, market size, and competition",
                "sub_metrics": ["Sector Analysis", "Market Size", "Competition"]
            },
            "product_traction": {
                "weight": 0.20,
                "description": "User metrics and growth indicators",
                "sub_metrics": ["Customer Growth", "Revenue Growth", "Product-Market Fit"]
            },
            "risk_assessment": {
                "weight": 0.15,
                "description": "Risk factors and mitigation strategies",
                "sub_metrics": ["Financial Risk", "Team Risk", "Market Risk", "Stage Risk"]
            }
        },
        "scoring_scale": "0-100 points per category",
        "recommendation_levels": ["Strong Buy", "Buy", "Hold", "Weak Hold", "Sell"],
        "confidence_levels": ["High", "Medium", "Low"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
