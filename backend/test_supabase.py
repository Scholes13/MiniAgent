"""
Test script for Postgrest/Supabase integration
"""
import os
import sys
import asyncio
from datetime import datetime

# Ensure we can import from utils
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from utils.db_manager import db_manager

async def test_supabase():
    """Test Supabase connection and operations"""
    print(f"Testing Supabase connection...")
    is_connected = db_manager.is_connected()
    print(f"Connected: {is_connected}")
    
    if not is_connected:
        print("Not connected to Supabase. Check your credentials.")
        return
    
    # Test creating a project
    print("\nCreating a test project...")
    test_project = {
        "project_name": "Test Project",
        "token_symbol": "TEST",
        "description": "A test project created for testing Supabase integration",
        "website_url": "https://example.com",
        "twitter_handle": "testproject"
    }
    
    project_result = await db_manager.add_project(**test_project)
    print(f"Project creation result: {project_result}")
    
    if "error" in project_result:
        print(f"Error creating project: {project_result['error']}")
        return
    
    project_id = project_result["data"]["id"]
    
    # Test adding Twitter data
    print("\nAdding Twitter data...")
    tweet_data = {
        "id": f"test_tweet_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "text": "This is a test airdrop tweet #airdrop $TEST free tokens!",
        "author": {
            "name": "Test Author",
            "username": "testauthor",
            "followers_count": 1000,
            "verified": False
        },
        "like_count": 50,
        "retweet_count": 20
    }
    
    tweet_result = await db_manager.add_twitter_data(project_id, tweet_data)
    print(f"Tweet data result: {tweet_result}")
    
    # Test adding AI analysis
    print("\nAdding AI analysis...")
    analysis_data = {
        "legitimacy_score": 7,
        "potential_score": 8,
        "revenue_estimate": "$1M - $5M",
        "risk_level": "Medium",
        "overall_rating": 7,
        "supporting_entities": [
            {"name": "Test VC", "type": "VC"},
            {"name": "Test Exchange", "type": "Exchange"}
        ],
        "analysis_text": "This is a test analysis of the project",
        "ai_model_used": "Test AI Model"
    }
    
    analysis_result = await db_manager.add_ai_analysis(project_id, analysis_data)
    print(f"AI analysis result: {analysis_result}")
    
    # Test getting project details
    print("\nRetrieving project details...")
    project_details = await db_manager.get_project_with_details(project_id)
    print(f"Project details: {project_details}")
    
    # Test getting latest projects
    print("\nGetting latest projects...")
    latest_projects = await db_manager.get_latest_projects(limit=5)
    print(f"Latest projects: {latest_projects}")
    
    # Test getting top rated projects
    print("\nGetting top rated projects...")
    top_rated = await db_manager.get_top_rated_projects(limit=5)
    print(f"Top rated projects: {top_rated}")
    
    print("\nTests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_supabase()) 