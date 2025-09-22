"""
Final Enhanced MCP Server
Integrates all services: Agent Orchestration, Authentication, Cloud Storage, BigQuery Analytics
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Security, BackgroundTasks, Header
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
from agent_orchestrator import AgentOrchestrator
from auth_system import security_middleware, UserRole
from cloud_storage_service import get_storage_service
from bigquery_analytics import get_analytics_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Startup Evaluator MCP Server - Final",
    description="Complete AI-powered startup evaluation platform with agent orchestration, authentication, and analytics",
    version="3.0.0",
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
    agent_orchestrator = AgentOrchestrator()
    storage_service = get_storage_service()
    analytics_service = get_analytics_service()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
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
    agent_workflow_results: Dict[str, Any]
    file_storage_info: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
    agent_status: Dict[str, str]

class AnalyticsResponse(BaseModel):
    sector_analysis: list
    total_evaluations: int
    average_scores: Dict[str, float]
    recommendation_distribution: Dict[str, int]

# Dependency for authentication
async def get_current_user(authorization: str = Header(None)):
    """Get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    user_info = security_middleware.authenticate_request(authorization)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_info

# Dependency for authorization
def require_permission(permission: str):
    """Require specific permission for endpoint"""
    def permission_checker(user_info: dict = Depends(get_current_user)):
        user_role = UserRole(user_info.get("role", "guest"))
        if not security_middleware.authz_service.has_permission(user_role, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user_info
    return permission_checker

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    services = {
        "vertex_ai": "healthy" if 'model' in locals() else "unavailable",
        "cloud_vision": "healthy" if 'vision_client' in locals() else "unavailable",
        "cloud_storage": "healthy" if 'storage_client' in locals() else "unavailable",
        "bigquery": "healthy" if 'bigquery_client' in locals() else "unavailable",
        "agent_orchestrator": "healthy" if 'agent_orchestrator' in locals() else "unavailable",
        "storage_service": "healthy" if 'storage_service' in locals() else "unavailable",
        "analytics_service": "healthy" if 'analytics_service' in locals() else "unavailable"
    }
    
    agent_status = agent_orchestrator.get_workflow_status() if 'agent_orchestrator' in locals() else {}
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services=services,
        agent_status=agent_status
    )

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_startup(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    user_info: dict = Depends(require_permission("write"))
):
    """Enhanced startup evaluation with agent orchestration and storage"""
    try:
        logger.info(f"Starting enhanced evaluation for file: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Upload file to Cloud Storage
        logger.info("Uploading file to Cloud Storage...")
        user_id = user_info.get("user_id", "anonymous")
        storage_result = storage_service.upload_file(
            file_content, 
            file.filename, 
            user_id,
            metadata={"evaluation_type": "startup_analysis"}
        )
        
        if not storage_result.get("success"):
            raise HTTPException(status_code=500, detail=f"File upload failed: {storage_result.get('error')}")
        
        # Execute agent orchestration workflow
        logger.info("Executing agent orchestration workflow...")
        workflow_results = await agent_orchestrator.execute_workflow(file_content, file.filename)
        
        if workflow_results.get("workflow_status") != "completed":
            raise HTTPException(status_code=500, detail=f"Agent workflow failed: {workflow_results.get('error')}")
        
        # Extract data from workflow results
        agent_results = workflow_results.get("agent_results", {})
        extracted_data = agent_results.get("document_intelligence", {})
        market_analysis = agent_results.get("market_analysis", {})
        financial_analysis = agent_results.get("financial_analysis", {})
        risk_assessment = agent_results.get("risk_assessment", {})
        investment_recommendation = agent_results.get("investment_recommendation", {})
        
        # Get peer comparison from BigQuery
        logger.info("Getting peer comparison from BigQuery...")
        sector_comparison = analytics_service.get_peer_comparison(extracted_data)
        
        # Store data in BigQuery
        logger.info("Storing data in BigQuery...")
        startup_id = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()[:12]
        
        # Insert startup data
        startup_data = {
            "startup_id": startup_id,
            "company_name": extracted_data.get("company_name", ""),
            "sector": extracted_data.get("sector", ""),
            "stage": extracted_data.get("stage", ""),
            "arr_crore": extracted_data.get("arr_crore", 0),
            "team_size": extracted_data.get("team_size", 0),
            "valuation_crore": extracted_data.get("valuation_pre_money_crore", 0),
            "revenue_model": extracted_data.get("revenue_model", ""),
            "founders": extracted_data.get("founders", [])
        }
        analytics_service.insert_startup_data(startup_data)
        
        # Insert evaluation data
        evaluation_data = {
            "evaluation_id": f"eval_{startup_id}",
            "startup_id": startup_id,
            "financial_health_score": financial_analysis.get("financial_health_score", 0),
            "team_quality_score": extracted_data.get("team_quality_score", 0),
            "market_opportunity_score": market_analysis.get("market_opportunity_score", 0),
            "product_traction_score": extracted_data.get("product_traction_score", 0),
            "risk_score": risk_assessment.get("overall_risk_score", 0),
            "overall_score": investment_recommendation.get("overall_score", 0),
            "investment_recommendation": investment_recommendation.get("recommendation", ""),
            "confidence_level": investment_recommendation.get("confidence", ""),
            "evaluation_data": workflow_results
        }
        analytics_service.insert_evaluation_data(evaluation_data)
        
        # Prepare response
        response = EvaluationResponse(
            startup_id=startup_id,
            timestamp=datetime.now().isoformat(),
            extracted_data=extracted_data,
            sector_comparison=sector_comparison,
            risk_assessment=risk_assessment,
            investment_score=investment_recommendation.get("overall_score", 0),
            investment_recommendation=investment_recommendation.get("recommendation", ""),
            financial_health_score=financial_analysis.get("financial_health_score", 0),
            team_quality_score=extracted_data.get("team_quality_score", 0),
            market_opportunity_score=market_analysis.get("market_opportunity_score", 0),
            product_traction_score=extracted_data.get("product_traction_score", 0),
            risk_score=risk_assessment.get("overall_risk_score", 0),
            confidence_level=investment_recommendation.get("confidence", ""),
            evaluation_details={
                "metrics_weights": evaluator.metrics_weights,
                "evaluation_method": "5-category framework with agent orchestration",
                "ai_model": "gemini-1.5-pro",
                "processing_time": workflow_results.get("execution_time", 0),
                "agent_count": workflow_results.get("summary", {}).get("total_agents", 0)
            },
            agent_workflow_results=workflow_results,
            file_storage_info=storage_result
        )
        
        logger.info(f"Enhanced evaluation complete for {startup_id}: {investment_recommendation.get('recommendation', 'N/A')}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced startup evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/analytics/dashboard", response_model=AnalyticsResponse)
async def get_analytics_dashboard(user_info: dict = Depends(require_permission("read"))):
    """Get analytics dashboard data"""
    try:
        dashboard_data = analytics_service.get_analytics_dashboard_data()
        
        return AnalyticsResponse(
            sector_analysis=dashboard_data.get("sector_analysis", []),
            total_evaluations=dashboard_data.get("total_evaluations", 0),
            average_scores=dashboard_data.get("average_scores", {}),
            recommendation_distribution=dashboard_data.get("recommendation_distribution", {})
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@app.get("/analytics/sector/{sector}")
async def get_sector_analytics(sector: str, user_info: dict = Depends(require_permission("read"))):
    """Get detailed analytics for specific sector"""
    try:
        benchmarks = analytics_service.get_sector_benchmarks(sector)
        peer_comparison = analytics_service.get_peer_comparison({"sector": sector})
        
        return {
            "sector": sector,
            "benchmarks": benchmarks,
            "peer_comparison": peer_comparison,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sector analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Sector analytics error: {str(e)}")

@app.get("/files")
async def list_user_files(user_info: dict = Depends(require_permission("read"))):
    """List files uploaded by user"""
    try:
        user_id = user_info.get("user_id", "anonymous")
        files = storage_service.list_user_files(user_id)
        
        return {
            "files": files,
            "total_files": len(files),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing user files: {e}")
        raise HTTPException(status_code=500, detail=f"File listing error: {str(e)}")

@app.delete("/files/{file_path:path}")
async def delete_file(file_path: str, user_info: dict = Depends(require_permission("write"))):
    """Delete user file"""
    try:
        success = storage_service.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
        
        return {
            "success": True,
            "message": f"File {file_path} deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"File deletion error: {str(e)}")

@app.get("/metrics/framework")
async def get_metrics_framework(user_info: dict = Depends(require_permission("read"))):
    """Get the evaluation metrics framework details"""
    return {
        "framework_name": "5-Category Startup Evaluation Framework with Agent Orchestration",
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
        "agent_workflow": {
            "document_intelligence": "Extracts and analyzes data from startup documents",
            "market_analysis": "Analyzes market opportunity and sector benchmarks",
            "financial_analysis": "Analyzes financial health and projections",
            "risk_assessment": "Assesses risks and provides mitigation strategies",
            "investment_recommendation": "Generates final investment recommendation"
        },
        "scoring_scale": "0-100 points per category",
        "recommendation_levels": ["Strong Buy", "Buy", "Hold", "Weak Hold", "Sell"],
        "confidence_levels": ["High", "Medium", "Low"]
    }

@app.post("/auth/login")
async def login(username: str, password: str):
    """User login endpoint"""
    try:
        from auth_system import auth_service
        
        user = auth_service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = auth_service.generate_token(user)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_info": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "permissions": user.permissions
            },
            "expires_in": 24 * 3600  # 24 hours
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/auth/me")
async def get_current_user_info(user_info: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user_info": user_info,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
