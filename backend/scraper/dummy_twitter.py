"""
Dummy Twitter scraper for testing when twikit has issues
"""
import os
import json
import random
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union

class DummyTwitterScraper:
    """Dummy Twitter scraper that generates fake data for testing"""
    
    def __init__(self):
        """Initialize the dummy scraper"""
        self.logged_in = False
        print("[DUMMY] TwitterScraper initialized")
    
    async def login(self) -> bool:
        """Simulate Twitter login"""
        print("[DUMMY] Login process simulated")
        self.logged_in = True
        return True
    
    async def search_tweets(self, query: str, limit: int = 50) -> List[Dict]:
        """Generate dummy tweets for the query"""
        print(f"[DUMMY] Searching tweets for '{query}' (limit: {limit})")
        
        tweets = []
        for i in range(min(limit, 10)):  # Generate at most 10 tweets
            # Create tweet with different content based on query
            if "airdrop" in query.lower():
                text = f"Join our amazing {query} airdrop! Limited spots available. Complete tasks to claim free tokens! #airdrop #{query.replace(' ', '')}"
            elif "crypto" in query.lower():
                text = f"Latest {query} news! Price prediction for 2025: $100K. Don't miss this opportunity! #crypto #{query.replace(' ', '')}"
            else:
                text = f"Check out this new project: {query}. Join our community for updates! #crypto #newproject #{query.replace(' ', '')}"
            
            # Create tweet object
            tweet = {
                "id": f"tweet_{i}_{hash(query) % 1000}",
                "text": text,
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                "author": {
                    "id": f"user_{i}_{hash(query) % 1000}",
                    "username": f"crypto_user{i}",
                    "name": f"Crypto User {i}",
                    "followers_count": random.randint(100, 10000),
                    "verified": random.choice([True, False] + [False] * 8)  # 10% chance of being verified
                },
                "like_count": random.randint(5, 500),
                "retweet_count": random.randint(0, 200)
            }
            
            tweets.append(tweet)
        
        return tweets
    
    def score_airdrop_tweet(self, tweet: Dict) -> Dict:
        """Score a tweet for airdrop relevance"""
        # Calculate simple score
        score = random.randint(10, 50)
        
        # Determine legitimacy based on score
        if score >= 40:
            legitimacy = "High"
        elif score >= 20:
            legitimacy = "Medium"
        else:
            legitimacy = "Low"
        
        return {
            "score": score,
            "legitimacy": legitimacy,
            "reasons": ["Mock scoring for testing"]
        }
    
    async def get_airdrop_opportunities(self, queries: List[str] = None, limit: int = 20) -> List[Dict]:
        """Generate dummy airdrop opportunities"""
        print(f"[DUMMY] Getting airdrop opportunities (limit: {limit})")
        
        if not queries:
            queries = ["crypto airdrop", "free tokens", "nft airdrop"]
        
        all_tweets = []
        for query in queries:
            tweets = await self.search_tweets(query, limit=max(3, limit // len(queries)))
            for tweet in tweets:
                tweet["airdrop_score"] = self.score_airdrop_tweet(tweet)
            all_tweets.extend(tweets)
        
        # Sort by score and take top ones
        sorted_tweets = sorted(
            all_tweets,
            key=lambda x: x.get("airdrop_score", {}).get("score", 0),
            reverse=True
        )
        
        return sorted_tweets[:limit]
    
    async def get_trending_crypto_projects(self, limit: int = 10) -> List[Dict]:
        """Generate dummy trending crypto projects"""
        print(f"[DUMMY] Getting trending crypto projects (limit: {limit})")
        
        tickers = ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "MATIC", "LINK", "UNI", "AAVE", "DOGE", "SHIB"]
        random.shuffle(tickers)
        
        trending = []
        for i, ticker in enumerate(tickers[:limit]):
            trending.append({
                "ticker": ticker,
                "mention_count": random.randint(1000, 100000),
                "engagement_score": random.randint(5000, 500000),
                "tweets": [f"dummy_tweet_{ticker}_{j}" for j in range(random.randint(5, 20))]
            })
        
        # Sort by engagement
        trending.sort(key=lambda x: x["engagement_score"], reverse=True)
        
        return trending

# For testing
async def test_dummy_scraper():
    """Test the dummy scraper"""
    scraper = DummyTwitterScraper()
    
    # Login
    print("Testing login...")
    await scraper.login()
    
    # Test airdrop opportunities
    print("\nTesting airdrop opportunities...")
    airdrops = await scraper.get_airdrop_opportunities(limit=5)
    print(f"Found {len(airdrops)} airdrop opportunities")
    for airdrop in airdrops:
        print(f"- {airdrop['text'][:100]}... (Score: {airdrop['airdrop_score']['score']})")
    
    # Test trending projects
    print("\nTesting trending projects...")
    trending = await scraper.get_trending_crypto_projects(limit=5)
    print(f"Found {len(trending)} trending projects")
    for project in trending:
        print(f"- ${project['ticker']}: {project['mention_count']} mentions, {project['engagement_score']} engagement")

if __name__ == "__main__":
    asyncio.run(test_dummy_scraper()) 