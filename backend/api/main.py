"""
Main FastAPI application for Crypto Airdrop Analyzer
"""
import os
import sys
import asyncio
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scraper.data_processor import DataProcessor
from utils.db_manager import db_manager

# Import OpenRouter endpoints
from .openrouter_endpoints import router as openrouter_router

# Create FastAPI app
app = FastAPI(
    title="Crypto Airdrop Analyzer API",
    description="API for analyzing cryptocurrency airdrops from Twitter",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Specify frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Include OpenRouter endpoints
app.include_router(openrouter_router)

# Models
class ProjectBase(BaseModel):
    project_name: str
    token_symbol: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    twitter_handle: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    project_name: str
    token_symbol: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    discovery_date: str
    last_updated: str

class ScrapeRequest(BaseModel):
    query: Optional[str] = None
    limit: Optional[int] = 10

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Crypto Airdrop Analyzer API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_connected = db_manager.is_connected()
    return {
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected"
    }

@app.post("/projects/", response_model=dict)
async def create_project(project: ProjectBase):
    """Create a new project"""
    result = await db_manager.add_project(
        project_name=project.project_name,
        token_symbol=project.token_symbol,
        description=project.description,
        website_url=project.website_url,
        twitter_handle=project.twitter_handle
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@app.get("/projects/latest", response_model=dict)
async def get_latest_projects(limit: int = 10):
    """Get latest projects"""
    result = await db_manager.get_latest_projects(limit=limit)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@app.get("/projects/top", response_model=dict)
async def get_top_projects(limit: int = 10):
    """Get top rated projects"""
    result = await db_manager.get_top_rated_projects(limit=limit)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@app.get("/projects/{project_id}", response_model=dict)
async def get_project(project_id: int):
    """Get project details"""
    result = await db_manager.get_project_with_details(project_id)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    if result.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    return result

@app.post("/scrape/twitter", response_model=dict)
async def scrape_twitter(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Trigger Twitter scraping"""
    print(f"[DEBUG] ======== SCRAPE TWITTER ENDPOINT CALLED ========")
    print(f"[DEBUG] Request: query={request.query}, limit={request.limit}")
    
    try:
        # Create DataProcessor
        print(f"[DEBUG] Creating DataProcessor...")
        processor = DataProcessor()
        
        # Add task to background
        print(f"[DEBUG] Adding background task to run scraper with limit {request.limit}")
        background_tasks.add_task(
            processor.run,
            airdrop_limit=request.limit
        )
        
        print(f"[DEBUG] Background task added successfully")
        print(f"[DEBUG] ======== SCRAPE TWITTER ENDPOINT COMPLETED ========")
        
        return {
            "status": "scraping_started",
            "message": f"Twitter scraping started with limit {request.limit}"
        }
    except Exception as e:
        print(f"[ERROR] Twitter scraping error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Twitter scraping error: {str(e)}"
        )

# For testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 