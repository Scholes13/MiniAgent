"""
Configuration for the Twitter scraper and Airdrop Pipeline
"""
import os
from typing import Dict, Any

# Twitter configuration
TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME", "your_twitter_username")
TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL", "your_twitter_email")
TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD", "your_twitter_password")
COOKIES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache", "twitter_cookies.json")

# Supabase configuration
SUPABASE_URL = "https://yolgbenpsuacibxgipsb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvbGdiZW5wc3VhY2lieGdpcHNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc4OTA1MjEsImV4cCI6MjA2MzQ2NjUyMX0.wAp0WK0RldUdJWNI5MdzxTuIMIdXv5VTWDLfbwFEQNU"
AIRDROP_TABLE = "crypto_airdrops"

# Twitter hashtags and search queries
AIRDROP_SEARCH_QUERIES = [
    "crypto airdrop",
    "token airdrop",
    "free crypto",
    "airdrop solana",
    "airdrop ethereum",
    "#airdrop"
]

CRYPTO_HASHTAGS = [
    "#bitcoin", "#ethereum", "#solana", "#crypto",
    "$btc", "$eth", "$sol", "$avax", "$matic"
]

# Scraper configuration
DEFAULT_SCRAPE_INTERVAL_MINUTES = 30
DEFAULT_TWEETS_PER_HASHTAG = 10

# Define sleep times between API calls to avoid rate limits
API_CALL_DELAY_SECONDS = 1.5

# Pipeline configuration
PIPELINE_RUN_INTERVAL_MINUTES = 60

def get_credentials() -> Dict[str, Any]:
    """Get all credentials as a dictionary"""
    return {
        "twitter": {
            "username": TWITTER_USERNAME,
            "email": TWITTER_EMAIL,
            "password": TWITTER_PASSWORD
        },
        "supabase": {
            "url": SUPABASE_URL,
            "key": SUPABASE_KEY
        }
    }

def validate_credentials() -> bool:
    """Validate that all required credentials are set"""
    required_vars = [
        TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD,
        SUPABASE_URL, SUPABASE_KEY
    ]
    
    for var in required_vars:
        if var.startswith("your_") or not var:
            return False
    
    return True 