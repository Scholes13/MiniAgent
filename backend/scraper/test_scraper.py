"""
Test script for TwitterScraper
"""
import os
import sys
import asyncio

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from twitter_scraper import TwitterScraper

async def test():
    """Test the TwitterScraper"""
    print("Initializing TwitterScraper...")
    scraper = TwitterScraper()
    
    print("Logging in to Twitter...")
    login_result = await scraper.login()
    print(f"Login result: {login_result}")
    
    if not login_result and not scraper.guest_client:
        print("Failed to login and no guest client available. Exiting.")
        return
    
    # Test searching tweets
    print("\nTesting tweet search...")
    tweets = await scraper.search_tweets("crypto airdrop", limit=3)
    print(f"Found {len(tweets)} tweets")
    
    if tweets:
        print("First tweet:")
        print(f"- ID: {tweets[0].get('id', 'N/A')}")
        print(f"- Text: {tweets[0].get('text', 'N/A')[:100]}...")
    
    # Test airdrop opportunities
    print("\nTesting airdrop opportunities...")
    airdrops = await scraper.get_airdrop_opportunities(limit=3)
    print(f"Found {len(airdrops)} airdrop opportunities")
    
    if airdrops:
        print("First airdrop:")
        print(f"- Text: {airdrops[0].get('text', 'N/A')[:100]}...")
        print(f"- Score: {airdrops[0].get('airdrop_score', {}).get('score', 'N/A')}")
        print(f"- Legitimacy: {airdrops[0].get('airdrop_score', {}).get('legitimacy', 'N/A')}")
    
    # Test trending projects
    print("\nTesting trending projects...")
    trending = await scraper.get_trending_crypto_projects(limit=3)
    print(f"Found {len(trending)} trending projects")
    
    if trending:
        print("First trending project:")
        print(f"- Ticker: ${trending[0].get('ticker', 'N/A')}")
        print(f"- Mentions: {trending[0].get('mention_count', 'N/A')}")
        print(f"- Engagement: {trending[0].get('engagement_score', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test()) 