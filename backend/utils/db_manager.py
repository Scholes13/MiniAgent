"""
Database manager for Postgrest integration (Supabase)
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from postgrest import AsyncPostgrestClient

from .supabase_config import (
    SUPABASE_URL, 
    SUPABASE_KEY,
    TABLE_PROJECTS,
    TABLE_TWITTER_DATA,
    TABLE_AI_ANALYSIS,
    TABLE_TOKENOMICS,
    TABLE_MARKET_DATA,
    TABLE_USER_WATCHLIST
)

class DatabaseManager:
    """Manager class for database operations with Postgrest (Supabase)"""
    
    def __init__(self, url: str = None, key: str = None):
        """Initialize Postgrest client"""
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self.client = None
        self.initialize_client()
    
    def initialize_client(self) -> bool:
        """Initialize Postgrest client"""
        try:
            if self.url == "YOUR_SUPABASE_URL" or self.key == "YOUR_SUPABASE_KEY":
                print("WARNING: Supabase credentials not set. Using dummy client.")
                self.client = None
                return False
            
            # Format URL for Postgrest
            rest_url = f"{self.url}/rest/v1"
            
            # Create Postgrest client
            self.client = AsyncPostgrestClient(
                rest_url,
                headers={
                    "apikey": self.key,
                    "Authorization": f"Bearer {self.key}"
                }
            )
            print("Postgrest client initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing Postgrest client: {e}")
            self.client = None
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Postgrest"""
        return self.client is not None
    
    async def add_project(self, project_name: str, token_symbol: str = None, 
                   description: str = None, website_url: str = None,
                   twitter_handle: str = None) -> Dict:
        """Add a new project to the database"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            # Check if project already exists
            existing = await self.client.table(TABLE_PROJECTS).select("*").eq("project_name", project_name).execute()
            
            if existing.data and len(existing.data) > 0:
                # Project exists, return it
                return {"status": "exists", "data": existing.data[0]}
            
            # Add new project
            now = datetime.now().isoformat()
            result = await self.client.table(TABLE_PROJECTS).insert({
                "project_name": project_name,
                "token_symbol": token_symbol,
                "description": description,
                "website_url": website_url,
                "twitter_handle": twitter_handle,
                "discovery_date": now,
                "last_updated": now
            }).execute()
            
            if result.data and len(result.data) > 0:
                return {"status": "created", "data": result.data[0]}
            else:
                return {"error": "Failed to create project", "details": result}
                
        except Exception as e:
            print(f"Error adding project: {e}")
            return {"error": str(e)}
    
    async def add_twitter_data(self, project_id: int, tweet_data: Dict) -> Dict:
        """Add Twitter data for a project"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            data = {
                "project_id": project_id,
                "tweet_id": tweet_data.get("id"),
                "tweet_text": tweet_data.get("text"),
                "tweet_url": f"https://twitter.com/i/web/status/{tweet_data.get('id')}",
                "author_name": tweet_data.get("author", {}).get("name"),
                "author_username": tweet_data.get("author", {}).get("username"),
                "followers_count": tweet_data.get("author", {}).get("followers_count", 0),
                "verified": tweet_data.get("author", {}).get("verified", False),
                "engagement_score": tweet_data.get("like_count", 0) + (tweet_data.get("retweet_count", 0) * 2),
                "collected_at": datetime.now().isoformat()
            }
            
            result = await self.client.table(TABLE_TWITTER_DATA).insert(data).execute()
            
            if result.data and len(result.data) > 0:
                return {"status": "success", "data": result.data[0]}
            else:
                return {"error": "Failed to add Twitter data", "details": result}
                
        except Exception as e:
            print(f"Error adding Twitter data: {e}")
            return {"error": str(e)}
    
    async def add_ai_analysis(self, project_id: int, analysis: Dict) -> Dict:
        """Add AI analysis for a project"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            # Convert supporting_entities to JSON string if it's a list
            supporting_entities = analysis.get("supporting_entities", [])
            if isinstance(supporting_entities, list):
                supporting_entities = json.dumps(supporting_entities)
            
            data = {
                "project_id": project_id,
                "legitimacy_score": analysis.get("legitimacy_score"),
                "potential_score": analysis.get("potential_score"),
                "revenue_estimate": analysis.get("revenue_estimate"),
                "risk_level": analysis.get("risk_level"),
                "overall_rating": analysis.get("overall_rating"),
                "supporting_entities": supporting_entities,
                "analysis_text": analysis.get("analysis_text"),
                "ai_model_used": analysis.get("ai_model_used"),
                "analysis_date": datetime.now().isoformat()
            }
            
            result = await self.client.table(TABLE_AI_ANALYSIS).insert(data).execute()
            
            if result.data and len(result.data) > 0:
                return {"status": "success", "data": result.data[0]}
            else:
                return {"error": "Failed to add AI analysis", "details": result}
                
        except Exception as e:
            print(f"Error adding AI analysis: {e}")
            return {"error": str(e)}
    
    async def add_tokenomics(self, project_id: int, tokenomics_data: Dict) -> Dict:
        """Add tokenomics data for a project"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            # Convert vesting_details to JSON string if it's a dict
            vesting_details = tokenomics_data.get("vesting_details", {})
            if isinstance(vesting_details, dict):
                vesting_details = json.dumps(vesting_details)
                
            data = {
                "project_id": project_id,
                "total_supply": tokenomics_data.get("total_supply"),
                "circulating_supply": tokenomics_data.get("circulating_supply"),
                "airdrop_percentage": tokenomics_data.get("airdrop_percentage"),
                "team_allocation_percentage": tokenomics_data.get("team_allocation_percentage"),
                "vesting_details": vesting_details,
                "token_type": tokenomics_data.get("token_type"),
                "blockchain": tokenomics_data.get("blockchain"),
                "updated_at": datetime.now().isoformat()
            }
            
            result = await self.client.table(TABLE_TOKENOMICS).insert(data).execute()
            
            if result.data and len(result.data) > 0:
                return {"status": "success", "data": result.data[0]}
            else:
                return {"error": "Failed to add tokenomics data", "details": result}
                
        except Exception as e:
            print(f"Error adding tokenomics data: {e}")
            return {"error": str(e)}
    
    async def get_project_by_name(self, project_name: str) -> Dict:
        """Get project by name"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            result = await self.client.table(TABLE_PROJECTS).select("*").eq("project_name", project_name).execute()
            
            if result.data and len(result.data) > 0:
                return {"status": "success", "data": result.data[0]}
            else:
                return {"status": "not_found"}
                
        except Exception as e:
            print(f"Error getting project: {e}")
            return {"error": str(e)}
    
    async def get_project_with_details(self, project_id: int) -> Dict:
        """Get project with all related data"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            # Get project details
            project = await self.client.table(TABLE_PROJECTS).select("*").eq("id", project_id).execute()
            
            if not project.data or len(project.data) == 0:
                return {"status": "not_found"}
            
            project_data = project.data[0]
            
            # Get Twitter data
            twitter_data = await self.client.table(TABLE_TWITTER_DATA).select("*").eq("project_id", project_id).execute()
            
            # Get AI analysis
            ai_analysis = await self.client.table(TABLE_AI_ANALYSIS).select("*").eq("project_id", project_id).execute()
            
            # Get tokenomics
            tokenomics = await self.client.table(TABLE_TOKENOMICS).select("*").eq("project_id", project_id).execute()
            
            # Get market data
            market_data = await self.client.table(TABLE_MARKET_DATA).select("*").eq("project_id", project_id).execute()
            
            return {
                "status": "success", 
                "data": {
                    "project": project_data,
                    "twitter_data": twitter_data.data if twitter_data.data else [],
                    "ai_analysis": ai_analysis.data[0] if ai_analysis.data and len(ai_analysis.data) > 0 else None,
                    "tokenomics": tokenomics.data[0] if tokenomics.data and len(tokenomics.data) > 0 else None,
                    "market_data": market_data.data if market_data.data else []
                }
            }
                
        except Exception as e:
            print(f"Error getting project details: {e}")
            return {"error": str(e)}
    
    async def get_latest_projects(self, limit: int = 10) -> Dict:
        """Get latest projects"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            result = await self.client.table(TABLE_PROJECTS).select("*").order("discovery_date", desc=True).limit(limit).execute()
            
            return {"status": "success", "data": result.data}
                
        except Exception as e:
            print(f"Error getting latest projects: {e}")
            return {"error": str(e)}

    async def get_top_rated_projects(self, limit: int = 10) -> Dict:
        """Get top rated projects based on AI analysis"""
        if not self.is_connected():
            print("Not connected to Postgrest")
            return {"error": "Not connected to Postgrest"}
        
        try:
            # Use join via filtering and select
            projects = await self.client.table(TABLE_PROJECTS).select("*").execute()
            analyses = await self.client.table(TABLE_AI_ANALYSIS).select("*").order("overall_rating", desc=True).limit(limit).execute()
            
            if not analyses.data:
                return {"status": "success", "data": []}
            
            # Manually join the data
            result = []
            projects_dict = {p["id"]: p for p in projects.data}
            
            for analysis in analyses.data:
                project_id = analysis["project_id"]
                if project_id in projects_dict:
                    project = projects_dict[project_id]
                    result.append({
                        "id": project["id"],
                        "project_name": project["project_name"],
                        "token_symbol": project["token_symbol"],
                        "overall_rating": analysis["overall_rating"],
                        "analysis_date": analysis["analysis_date"]
                    })
            
            return {"status": "success", "data": result}
                
        except Exception as e:
            print(f"Error getting top rated projects: {e}")
            return {"error": str(e)}

# Initialize global database manager instance
db_manager = DatabaseManager()

# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Test connection
        print(f"Is connected: {db_manager.is_connected()}")
        
        # Example project creation
        if db_manager.is_connected():
            result = await db_manager.add_project(
                project_name="Test Project",
                token_symbol="TEST",
                description="A test project",
                website_url="https://example.com",
                twitter_handle="testproject"
            )
            print(f"Project creation result: {result}")
    
    asyncio.run(test()) 