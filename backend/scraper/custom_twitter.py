"""
Custom Twitter client yang sederhana untuk fallback jika twikit bermasalah
"""
import os
import json
import random
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import httpx
from dataclasses import dataclass

@dataclass
class MockTweet:
    """Mocked Tweet object for fallback scenario"""
    id: str
    text: str
    created_at: datetime
    user: Any
    favorite_count: int = 0
    retweet_count: int = 0
    
@dataclass
class MockUser:
    """Mocked User object for fallback scenario"""
    id: str
    username: str
    name: str
    followers_count: int = 0
    verified: bool = False
    screen_name: str = ""

@dataclass
class MockTrend:
    """Mocked Trend object for fallback scenario"""
    name: str
    tweet_volume: int = 0

class SimpleFallbackClient:
    """
    Client Twitter sederhana yang dapat digunakan sebagai fallback
    jika twikit bermasalah
    """
    
    def __init__(self, language="en-US"):
        """Initialize client"""
        self.language = language
        self.is_logged_in = False
        
    async def login(self, auth_info_1=None, auth_info_2=None, password=None, cookies_file=None):
        """Simulate login - always succeeds in fallback mode"""
        print("[FALLBACK] SimpleFallbackClient login called")
        self.is_logged_in = True
        return True
        
    async def search_tweet(self, query, filter_type='Latest', count=20):
        """Generate mock tweets for the query"""
        print(f"[FALLBACK] SimpleFallbackClient search_tweet: {query}")
        
        results = []
        for i in range(min(count, 10)):  # At most 10 mock tweets
            # Determine tweet content based on query
            if "airdrop" in query.lower():
                text = f"Join our amazing {query} airdrop! Complete tasks and win tokens. Limited spots available. Join now: example.com/airdrop{i} #airdrop #{query.replace(' ', '')}"
            elif any(ticker in query.lower() for ticker in ["btc", "eth", "sol"]):
                text = f"{query} is looking bullish today! Price target: ${random.randint(100, 10000)}. #crypto #{query.replace(' ', '')}"
            else:
                text = f"Check out this new project: {query}. Great potential for growth! #crypto #newproject #{query.replace(' ', '')}"
                
            # Create mock user
            user = MockUser(
                id=f"user_{i}",
                username=f"crypto_user{i}",
                name=f"Crypto User {i}",
                followers_count=random.randint(100, 5000),
                verified=random.choice([True, False] + [False] * 8),  # 10% chance of being verified
                screen_name=f"crypto_user{i}"
            )
            
            # Create mock tweet
            tweet = MockTweet(
                id=f"tweet_{i}_{query.replace(' ', '_')}",
                text=text,
                created_at=datetime.now() - timedelta(hours=random.randint(0, 48)),
                user=user,
                favorite_count=random.randint(5, 200),
                retweet_count=random.randint(0, 50)
            )
            
            results.append(tweet)
            
        return results
        
    async def get_trends(self, trend_type="trending"):
        """Get mock trending topics"""
        print(f"[FALLBACK] SimpleFallbackClient get_trends: {trend_type}")
        
        # Create mock trends
        crypto_trends = [
            "bitcoin", "ethereum", "solana", 
            "BTC", "ETH", "SOL", "DOGE", "SHIB",
            "#crypto", "#NFT", "#web3", "#DeFi"
        ]
        
        results = []
        for trend in random.sample(crypto_trends, min(10, len(crypto_trends))):
            results.append(MockTrend(
                name=trend,
                tweet_volume=random.randint(1000, 100000)
            ))
            
        return results 