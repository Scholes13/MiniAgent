"""
Data processor for handling Twitter data and saving to Supabase
"""
import sys
import os
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Add current and parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from scraper.twitter_scraper import TwitterScraper
from utils.db_manager import db_manager
from utils.twitter_config import TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL

class DataProcessor:
    """Process and save Twitter data to database"""
    
    def __init__(self):
        """Initialize data processor"""
        print("[DEBUG] ======== DATA PROCESSOR INITIALIZED ========")
        self.twitter_scraper = None
        self.initialize_twitter()
    
    def initialize_twitter(self):
        """Initialize Twitter scraper"""
        print("[DEBUG] Initializing Twitter scraper...")
        self.twitter_scraper = TwitterScraper()
        print("[DEBUG] Twitter scraper initialized")
    
    def extract_project_name(self, tweet_text: str, username: str = None) -> str:
        """Extract project name from tweet text"""
        print(f"[DEBUG] Extracting project name from tweet: {tweet_text[:50]}...")
        
        # First check for specific formats like "Project: NAME" or "Token: NAME"
        project_match = re.search(r'(?:project|token|airdrop)[:\s]+([A-Za-z0-9]+)', tweet_text, re.IGNORECASE)
        if project_match:
            result = project_match.group(1)
            print(f"[DEBUG] Found project name via regex: {result}")
            return result
            
        # Try extracting from cashtags
        cashtags = re.findall(r'\$([A-Za-z0-9]+)', tweet_text)
        if cashtags:
            result = cashtags[0]
            print(f"[DEBUG] Found project name via cashtag: {result}")
            return result
        
        # Extract name from hashtags
        hashtags = re.findall(r'#([A-Za-z0-9]+)', tweet_text)
        filtered_hashtags = [h for h in hashtags if len(h) > 3 and h.lower() not in ['airdrop', 'crypto', 'nft', 'token']]
        if filtered_hashtags:
            result = filtered_hashtags[0]
            print(f"[DEBUG] Found project name via hashtag: {result}")
            return result
        
        # Fallback to generic name with timestamp
        if username:
            result = f"{username}-airdrop-{datetime.now().strftime('%m%d')}"
            print(f"[DEBUG] Using username fallback: {result}")
            return result
        else:
            result = f"unknown-airdrop-{datetime.now().strftime('%m%d%H%M')}"
            print(f"[DEBUG] Using generic fallback: {result}")
            return result
    
    def extract_token_symbol(self, tweet_text: str) -> Optional[str]:
        """Extract token symbol from tweet text"""
        print(f"[DEBUG] Extracting token symbol from tweet: {tweet_text[:50]}...")
        
        # Look for cashtags which are usually token symbols
        cashtags = re.findall(r'\$([A-Za-z0-9]+)', tweet_text)
        if cashtags:
            result = cashtags[0].upper()
            print(f"[DEBUG] Found token symbol: {result}")
            return result
        
        print("[DEBUG] No token symbol found")
        return None
    
    def extract_website(self, tweet_text: str) -> Optional[str]:
        """Extract website URL from tweet text"""
        print(f"[DEBUG] Extracting website from tweet: {tweet_text[:50]}...")
        
        # Look for URLs
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        urls = re.findall(url_pattern, tweet_text)
        for url in urls:
            # Skip Twitter and common social media URLs
            if not any(domain in url.lower() for domain in ['twitter.com', 't.co', 'instagram.com', 'facebook.com']):
                print(f"[DEBUG] Found website URL: {url}")
                return url
        
        print("[DEBUG] No website URL found")
        return None
    
    async def process_airdrop_tweets(self, limit: int = 20) -> List[Dict]:
        """Process airdrop tweets and save to database"""
        print("[DEBUG] ======== PROCESSING AIRDROP TWEETS ========")
        print(f"[DEBUG] Processing with limit: {limit}")
        
        if not self.twitter_scraper:
            print("[DEBUG] Twitter scraper not initialized")
            return []
        
        # Login to Twitter if needed
        if not self.twitter_scraper.logged_in:
            print("[DEBUG] Twitter not logged in, attempting login...")
            login_success = await self.twitter_scraper.login()
            if not login_success:
                print("[DEBUG] Failed to login to Twitter")
                return []
            print("[DEBUG] Login successful")
        else:
            print("[DEBUG] Already logged in to Twitter")
        
        # Get airdrop opportunities
        print("[DEBUG] Searching for airdrop opportunities...")
        airdrops = await self.twitter_scraper.get_airdrop_opportunities(limit=limit)
        
        if not airdrops:
            print("[DEBUG] No airdrop opportunities found")
            return []
        
        print(f"[DEBUG] Found {len(airdrops)} airdrop opportunities")
        
        # Check DB connection
        is_connected = db_manager.is_connected()
        print(f"[DEBUG] Database connection status: {'Connected' if is_connected else 'Not connected'}")
        
        results = []
        for i, airdrop in enumerate(airdrops):
            try:
                print(f"[DEBUG] Processing airdrop {i+1}/{len(airdrops)}: {airdrop['id']}")
                
                # Extract project name and token symbol
                project_name = self.extract_project_name(
                    airdrop['text'], 
                    airdrop.get('author', {}).get('username')
                )
                token_symbol = self.extract_token_symbol(airdrop['text'])
                website_url = self.extract_website(airdrop['text'])
                twitter_handle = airdrop.get('author', {}).get('username')
                
                print(f"[DEBUG] Extracted data: project={project_name}, token={token_symbol}, website={website_url}, twitter={twitter_handle}")
                
                # Save project to database
                print(f"[DEBUG] Saving project to database: {project_name}")
                project_result = await db_manager.add_project(
                    project_name=project_name,
                    token_symbol=token_symbol,
                    website_url=website_url,
                    twitter_handle=twitter_handle
                )
                
                print(f"[DEBUG] Database add_project result: {project_result}")
                
                if 'error' in project_result:
                    print(f"[DEBUG] Error saving project {project_name}: {project_result['error']}")
                    continue
                
                project_id = project_result['data']['id']
                print(f"[DEBUG] Project saved with ID: {project_id}")
                
                # Save tweet data
                print(f"[DEBUG] Saving tweet data for project ID: {project_id}")
                tweet_result = await db_manager.add_twitter_data(project_id, airdrop)
                
                print(f"[DEBUG] Tweet data save result: {tweet_result}")
                
                if 'error' in tweet_result:
                    print(f"[DEBUG] Error saving tweet for {project_name}: {tweet_result['error']}")
                
                # Create basic AI analysis based on airdrop_score
                if 'airdrop_score' in airdrop:
                    print(f"[DEBUG] Creating AI analysis for project ID: {project_id}")
                    score = airdrop['airdrop_score']['score']
                    legitimacy = airdrop['airdrop_score']['legitimacy']
                    reasons = airdrop['airdrop_score']['reasons']
                    
                    # Convert score to 1-10 scale
                    legitimacy_score = min(10, max(1, int(score / 10)))
                    
                    analysis = {
                        "legitimacy_score": legitimacy_score,
                        "potential_score": None,  # Will be filled by AI analysis later
                        "revenue_estimate": None, # Will be filled by AI analysis later
                        "risk_level": "High" if legitimacy == "Low" else "Medium" if legitimacy == "Medium" else "Low",
                        "overall_rating": legitimacy_score,  # Initial rating based on legitimacy
                        "analysis_text": f"Initial analysis based on Twitter data: {', '.join(reasons)}",
                        "ai_model_used": "Twitter Scraper Initial Analysis"
                    }
                    
                    print(f"[DEBUG] AI analysis data: {analysis}")
                    ai_result = await db_manager.add_ai_analysis(project_id, analysis)
                    
                    print(f"[DEBUG] AI analysis save result: {ai_result}")
                    
                    if 'error' in ai_result:
                        print(f"[DEBUG] Error saving AI analysis for {project_name}: {ai_result['error']}")
                
                # Add to results
                results.append({
                    "project_id": project_id,
                    "project_name": project_name,
                    "token_symbol": token_symbol,
                    "tweet_id": airdrop['id'],
                    "legitimacy": legitimacy if 'airdrop_score' in airdrop else "Unknown"
                })
                
                print(f"[DEBUG] Successfully processed airdrop for project: {project_name}")
                
            except Exception as e:
                print(f"[DEBUG] Error processing airdrop: {str(e)}")
                continue
        
        print(f"[DEBUG] Total airdrop processing results: {len(results)} successful")
        print("[DEBUG] ======== AIRDROP PROCESSING COMPLETE ========")
        return results
    
    async def process_trending_projects(self, limit: int = 10) -> List[Dict]:
        """Process trending crypto projects and save to database"""
        print("[DEBUG] ======== PROCESSING TRENDING PROJECTS ========")
        print(f"[DEBUG] Processing with limit: {limit}")
        
        if not self.twitter_scraper:
            print("[DEBUG] Twitter scraper not initialized")
            return []
        
        # Login to Twitter if needed
        if not self.twitter_scraper.logged_in:
            print("[DEBUG] Twitter not logged in, attempting login...")
            login_success = await self.twitter_scraper.login()
            if not login_success:
                print("[DEBUG] Failed to login to Twitter")
                return []
            print("[DEBUG] Login successful")
        else:
            print("[DEBUG] Already logged in to Twitter")
        
        # Get trending projects
        print("[DEBUG] Searching for trending crypto projects...")
        trending = await self.twitter_scraper.get_trending_crypto_projects(limit=limit)
        
        if not trending:
            print("[DEBUG] No trending projects found")
            return []
        
        print(f"[DEBUG] Found {len(trending)} trending projects")
        
        # Check DB connection
        is_connected = db_manager.is_connected()
        print(f"[DEBUG] Database connection status: {'Connected' if is_connected else 'Not connected'}")
        
        results = []
        for i, project in enumerate(trending):
            try:
                print(f"[DEBUG] Processing trending project {i+1}/{len(trending)}: ${project['ticker']}")
                
                # Save project to database
                project_name = f"{project['ticker']} Token"
                print(f"[DEBUG] Saving project to database: {project_name}")
                
                project_result = await db_manager.add_project(
                    project_name=project_name,
                    token_symbol=project['ticker'].upper()
                )
                
                print(f"[DEBUG] Database add_project result: {project_result}")
                
                if 'error' in project_result:
                    print(f"[DEBUG] Error saving trending project {project['ticker']}: {project_result['error']}")
                    continue
                
                project_id = project_result['data']['id']
                print(f"[DEBUG] Project saved with ID: {project_id}")
                
                # Add to results
                results.append({
                    "project_id": project_id,
                    "project_name": project_name,
                    "token_symbol": project['ticker'].upper(),
                    "mention_count": project['mention_count'],
                    "engagement_score": project['engagement_score']
                })
                
                print(f"[DEBUG] Successfully processed trending project: {project_name}")
                
            except Exception as e:
                print(f"[DEBUG] Error processing trending project: {str(e)}")
                continue
        
        print(f"[DEBUG] Total trending processing results: {len(results)} successful")
        print("[DEBUG] ======== TRENDING PROCESSING COMPLETE ========")
        return results
    
    async def run(self, airdrop_limit: int = 20, trending_limit: int = 10):
        """Run data processor"""
        print("[DEBUG] ======== STARTING DATA PROCESSOR ========")
        print(f"[DEBUG] Airdrop limit: {airdrop_limit}, Trending limit: {trending_limit}")
        
        # Process airdrop tweets
        print("[DEBUG] Starting airdrop tweets processing...")
        airdrops = await self.process_airdrop_tweets(limit=airdrop_limit)
        print(f"[DEBUG] Processed {len(airdrops)} airdrop opportunities")
        
        # Process trending projects
        print("[DEBUG] Starting trending projects processing...")
        trending = await self.process_trending_projects(limit=trending_limit)
        print(f"[DEBUG] Processed {len(trending)} trending projects")
        
        print("[DEBUG] ======== DATA PROCESSOR COMPLETE ========")
        return {
            "airdrops": airdrops,
            "trending": trending
        }

# For testing
async def main():
    """Test function"""
    processor = DataProcessor()
    results = await processor.run()
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main()) 