from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import asyncio
from typing import List, Dict, Optional

from ..scraper.twitter_scraper import TwitterScraper
from ..utils.auth import get_current_user

# Inisialisasi router
router = APIRouter(
    prefix="/twitter",
    tags=["Twitter"],
    responses={404: {"description": "Not found"}},
)

# Singleton scraper instance
_scraper = None
_lock = asyncio.Lock()

async def get_scraper():
    """Get or initialize Twitter scraper singleton"""
    global _scraper
    if _scraper is None:
        async with _lock:
            if _scraper is None:
                _scraper = TwitterScraper()
                await _scraper.login()
    return _scraper

@router.get("/airdrops")
async def get_airdrops(limit: int = 20, current_user: dict = Depends(get_current_user)):
    """
    Get crypto airdrops from Twitter
    """
    scraper = await get_scraper()
    airdrops = await scraper.get_airdrop_opportunities(limit=limit)
    return {
        "airdrops": airdrops,
        "count": len(airdrops)
    }

@router.get("/trending")
async def get_trending(limit: int = 10, current_user: dict = Depends(get_current_user)):
    """
    Get trending crypto projects from Twitter
    """
    scraper = await get_scraper()
    trending = await scraper.get_trending_crypto_projects(limit=limit)
    return {
        "trending": trending,
        "count": len(trending)
    }

@router.get("/search")
async def search_twitter(query: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """
    Search Twitter for specific query
    """
    scraper = await get_scraper()
    results = await scraper.search_crypto_airdrops(query=query, limit=limit)
    return {
        "results": results,
        "count": len(results)
    }

# Fungsi untuk melakukan refresh data secara periodik
async def refresh_cache():
    """Background task to refresh cached Twitter data"""
    scraper = await get_scraper()
    await scraper.get_airdrop_opportunities(limit=50)
    await scraper.get_trending_crypto_projects(limit=20)
    
@router.post("/refresh")
async def trigger_refresh(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Manually trigger refresh of Twitter data cache
    """
    background_tasks.add_task(refresh_cache)
    return {"message": "Cache refresh started in background"} 