"""
OpenRouter API endpoints for admin management
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any, Union
import asyncio

import sys
import os
# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from utils.openrouter_config import (
    add_api_key,
    remove_api_key, 
    get_all_keys_status,
    reset_all_keys,
    mark_key_limit_reached,
    OPENROUTER_MODELS
)
from utils.openrouter_manager import OpenRouterManager

# Setup security
security = HTTPBearer()
admin_api_key = "admin_secret_key"  # In production, use a secure environment variable

# Initialize router
router = APIRouter(prefix="/openrouter", tags=["openrouter"])
openrouter_manager = OpenRouterManager(prefer_free=False)  # Default to using paid models

# Authentication dependency
async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token for protected routes"""
    if credentials.credentials != admin_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Endpoint to list all API keys (only hints, not full keys)
@router.get("/keys", summary="List all OpenRouter API keys")
async def list_api_keys(token: str = Depends(verify_admin_token)):
    """
    Get status of all API keys in the rotation
    """
    return {"keys": get_all_keys_status()}

# Endpoint to add a new API key
@router.post("/keys", summary="Add a new OpenRouter API key")
async def add_new_api_key(
    api_key: str = Body(..., embed=True),
    token: str = Depends(verify_admin_token)
):
    """
    Add a new API key to the rotation
    """
    add_api_key(api_key)
    return {"status": "success", "message": "API key added successfully"}

# Endpoint to remove an API key
@router.delete("/keys/{key_id}", summary="Remove an OpenRouter API key")
async def delete_api_key(
    key_id: str = Path(..., description="Full API key or key_hint to remove"),
    token: str = Depends(verify_admin_token)
):
    """
    Remove an API key from the rotation
    """
    remove_api_key(key_id)
    return {"status": "success", "message": "API key removed successfully if it existed"}

# Endpoint to mark a key as limited
@router.post("/keys/{key_id}/limit", summary="Mark an OpenRouter API key as limited")
async def mark_key_as_limited(
    key_id: str = Path(..., description="Full API key to mark as limited"),
    token: str = Depends(verify_admin_token)
):
    """
    Mark an API key as having reached its limit
    """
    mark_key_limit_reached(key_id)
    return {"status": "success", "message": "API key marked as limited"}

# Endpoint to reset all keys
@router.post("/keys/reset", summary="Reset all OpenRouter API keys")
async def reset_keys(token: str = Depends(verify_admin_token)):
    """
    Reset all API keys to available state
    """
    result = openrouter_manager.reset_api_keys()
    return result

# Endpoint to get available models
@router.get("/models", summary="Get available OpenRouter models")
async def get_models():
    """
    Get all available models including free options
    """
    # Group models by category
    model_groups = {
        "free": {k: v for k, v in OPENROUTER_MODELS.items() if k.startswith("free-")},
        "paid": {k: v for k, v in OPENROUTER_MODELS.items() if not k.startswith("free-")}
    }
    
    return {"models": model_groups}

# Endpoint to set model preference
@router.post("/preference", summary="Set model preference")
async def set_model_preference(
    prefer_free: bool = Body(..., embed=True),
    token: str = Depends(verify_admin_token)
):
    """
    Set whether to prefer free models or paid models
    """
    result = openrouter_manager.set_prefer_free(prefer_free)
    return result

# Endpoint to test OpenRouter integration with a simple analysis
@router.post("/test", summary="Test OpenRouter integration")
async def test_openrouter(
    text: str = Body(..., embed=True),
    model: str = Body("default", embed=True),
    token: str = Depends(verify_admin_token)
):
    """
    Test the OpenRouter integration with a simple text analysis
    """
    try:
        result = await openrouter_manager.analyze_text(
            text, 
            prompt="Provide a brief analysis of this crypto-related text.",
            model=model
        )
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenRouter test failed: {str(e)}"
        )

# Endpoint for project analysis
@router.post("/analyze", summary="Analyze a crypto project")
async def analyze_project(
    project_data: Dict[str, Any] = Body(...),
    model: Optional[str] = None
):
    """
    Generate AI analysis for a crypto project
    
    This endpoint does not require admin authentication as it's used by regular users
    """
    try:
        # If a specific model is requested and not using default manager setting
        if model:
            original_prefer_free = openrouter_manager.prefer_free
            openrouter_manager.prefer_free = model.startswith("free-")
            result = await openrouter_manager.generate_project_analysis(project_data)
            openrouter_manager.prefer_free = original_prefer_free
        else:
            result = await openrouter_manager.generate_project_analysis(project_data)
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

# Endpoint for code analysis/generation
@router.post("/code", summary="Analyze or generate code")
async def analyze_code(
    code: str = Body(..., embed=True),
    prompt: Optional[str] = Body(None, embed=True)
):
    """
    Analyze or generate code related to crypto projects
    """
    try:
        result = await openrouter_manager.analyze_code(code, prompt)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code analysis failed: {str(e)}"
        )

# Endpoint for scraping assistance
@router.post("/scrape-assist", summary="Get scraping assistance")
async def scrape_assistance(
    query: str = Body(..., embed=True)
):
    """
    Get assistance with scraping strategies for crypto data
    """
    try:
        result = await openrouter_manager.scrape_assistant(query)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping assistance failed: {str(e)}"
        ) 