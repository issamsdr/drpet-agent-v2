"""
DRPET Agent v2 Main Application

FastAPI application entry point for the DRPET Agent v2.
Provides REST API endpoints for resilience assessment and analysis.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import DRPET components
from .core.config import get_config
from .core.performance_optimizer import get_performance_stats
from .core.production_hardening import get_hardening_stats
from .monitoring.health_checks import health_registry, start_health_monitoring, stop_health_monitoring
from .monitoring.alerting import alert_manager
from .analysis.whitepaper_analyzer import WhitepaperAnalysisModule
from .analysis.service_analysis_manager import service_analysis_manager
from .mcp_tools.mcp_handler import BaseMCPHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting DRPET Agent v2...")
    
    # Start health monitoring
    start_health_monitoring()
    
    # Start alert monitoring
    alert_manager.start_monitoring()
    
    logger.info("DRPET Agent v2 started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DRPET Agent v2...")
    
    # Stop monitoring systems
    stop_health_monitoring()
    alert_manager.stop_monitoring()
    
    logger.info("DRPET Agent v2 shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="DRPET Agent v2",
    description="AWS Disaster Recovery Planning and Execution Tool - Agent v2",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize components
config = get_config()
whitepaper_analyzer = WhitepaperAnalysisModule()
mcp_handler = BaseMCPHandler()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "DRPET Agent v2",
        "version": "2.0.0",
        "status": "operational",
        "description": "AWS Disaster Recovery Planning and Execution Tool - Agent v2"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = health_registry.get_health_status()
        
        if health_status.get('overall_healthy', False):
            return {
                "status": "healthy",
                "timestamp": health_status.get('timestamp'),
                "checks": health_status.get('individual_status', {})
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": health_status.get('timestamp'),
                    "checks": health_status.get('individual_status', {})
                }
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": str(e)
            }
        )


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring"""
    try:
        return {
            "performance": get_performance_stats(),
            "hardening": get_hardening_stats(),
            "health": health_registry.get_health_status(),
            "alerts": alert_manager.get_alert_stats()
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/whitepaper")
async def analyze_whitepaper(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Analyze architecture against AWS resilience whitepapers
    
    Request body:
    {
        "architecture_data": {...},
        "rpo_target": "1 hour",
        "rto_target": "4 hours"
    }
    """
    try:
        architecture_data = request.get('architecture_data', {})
        rpo_target = request.get('rpo_target', '1 hour')
        rto_target = request.get('rto_target', '4 hours')
        
        if not architecture_data:
            raise HTTPException(status_code=400, detail="architecture_data is required")
        
        # Perform whitepaper analysis
        result = whitepaper_analyzer.analyze_all_whitepapers(
            architecture_data, rpo_target, rto_target
        )
        
        return {
            "status": "success",
            "analysis_result": result
        }
        
    except Exception as e:
        logger.error(f"Whitepaper analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/services")
async def analyze_services(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Analyze services for resilience patterns
    
    Request body:
    {
        "services": {...},
        "rpo_target": "1 hour",
        "rto_target": "4 hours"
    }
    """
    try:
        services = request.get('services', {})
        rpo_target = request.get('rpo_target', '1 hour')
        rto_target = request.get('rto_target', '4 hours')
        
        if not services:
            raise HTTPException(status_code=400, detail="services data is required")
        
        # Perform service analysis
        result = service_analysis_manager.analyze_all_services(
            services, rpo_target, rto_target
        )
        
        return {
            "status": "success",
            "analysis_result": result
        }
        
    except Exception as e:
        logger.error(f"Service analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/comprehensive")
async def comprehensive_analysis(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Perform comprehensive DRPET analysis including both whitepaper and service analysis
    
    Request body:
    {
        "architecture_data": {...},
        "services": {...},
        "rpo_target": "1 hour",
        "rto_target": "4 hours"
    }
    """
    try:
        architecture_data = request.get('architecture_data', {})
        services = request.get('services', {})
        rpo_target = request.get('rpo_target', '1 hour')
        rto_target = request.get('rto_target', '4 hours')
        
        if not architecture_data and not services:
            raise HTTPException(
                status_code=400, 
                detail="Either architecture_data or services data is required"
            )
        
        results = {}
        
        # Perform whitepaper analysis if architecture data provided
        if architecture_data:
            whitepaper_result = whitepaper_analyzer.analyze_all_whitepapers(
                architecture_data, rpo_target, rto_target
            )
            results['whitepaper_analysis'] = whitepaper_result
        
        # Perform service analysis if services data provided
        if services:
            service_result = service_analysis_manager.analyze_all_services(
                services, rpo_target, rto_target
            )
            results['service_analysis'] = service_result
        
        # Calculate overall score if both analyses were performed
        if 'whitepaper_analysis' in results and 'service_analysis' in results:
            whitepaper_score = results['whitepaper_analysis'].get('overall_score', 0)
            service_score = results['service_analysis'].get('overall_score', 0)
            overall_score = (whitepaper_score + service_score) / 2
            results['overall_score'] = overall_score
        
        return {
            "status": "success",
            "analysis_results": results
        }
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Factory function to create the FastAPI app"""
    return app


if __name__ == "__main__":
    # Run the application
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv('ENVIRONMENT') == 'development',
        log_level=os.getenv('LOG_LEVEL', 'info').lower()
    )