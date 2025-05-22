"""
Twitter scraper module - minimal version focusing on specific hashtags
"""
import os
import json
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import monkey patch for twikit
import patch_twikit
patch_twikit.patch_twikit()

# Import twikit for real Twitter data
from twikit import Client

from utils.twitter_config import (
    TWITTER_USERNAME,
    TWITTER_PASSWORD,
    TWITTER_EMAIL,
    COOKIES_FILE
)

# Specific hashtags to monitor - menggunakan format yang benar untuk Twitter search
HASHTAGS = ["airdrop", "solana", "sol", "$sol", "crypto airdrop", "crypto giveaway"]
OUTPUT_FILE = os.path.join(parent_dir, "data", "latest_crypto_opportunities.json")

class TwitterScraper:
    """Minimal Twitter scraper focusing on crypto airdrops with specific hashtags"""
    
    def __init__(self):
        """Initialize Twitter client"""
        self.client = Client("en-US")
        self.logged_in = False
        self.login_attempts = 0
        self.max_login_attempts = 3
        self.last_login_attempt_time = None
        self.cooldown_minutes = 30  # Tunggu 30 menit setelah max attempts
        self.last_results = {}
        print("[INFO] TwitterScraper initialized")
    
    async def login(self) -> bool:
        """Login to Twitter using twikit"""
        if self.logged_in:
            print("[INFO] Already logged in to Twitter")
            return True
        
        # Periksa apakah dalam masa pendinginan setelah beberapa kali percobaan gagal
        if self.login_attempts >= self.max_login_attempts and self.last_login_attempt_time:
            elapsed_minutes = (datetime.now() - self.last_login_attempt_time).total_seconds() / 60
            if elapsed_minutes < self.cooldown_minutes:
                remaining_minutes = self.cooldown_minutes - elapsed_minutes
                print(f"[PERINGATAN] Menunggu {remaining_minutes:.1f} menit sebelum mencoba login kembali")
                print(f"[INFO] Login dapat dicoba kembali pada: {(self.last_login_attempt_time + datetime.timedelta(minutes=self.cooldown_minutes)).strftime('%H:%M:%S')}")
                return False
            else:
                # Reset counter setelah cooldown
                print(f"[INFO] Waktu pendinginan selesai. Mencoba login kembali.")
                self.login_attempts = 0
            
        self.login_attempts += 1
        self.last_login_attempt_time = datetime.now()
        
        try:
            # Create cookies file directory if it doesn't exist
            cookies_dir = os.path.dirname(COOKIES_FILE)
            if cookies_dir and not os.path.exists(cookies_dir):
                os.makedirs(cookies_dir)
                
            # Check if cookies file exists and try to use it first
            if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
                print(f"[INFO] Attempting to login using existing cookies from: {COOKIES_FILE}")
                try:
                    # Try loading cookies first (faster and doesn't trigger anti-bot measures)
                    await self.client.load_cookies(COOKIES_FILE)
                    print("[INFO] Successfully logged in with saved cookies")
                    self.logged_in = True
                    # Reset counters on successful login
                    self.login_attempts = 0
                    return True
                except Exception as cookie_error:
                    print(f"[INFO] Cookie login failed: {str(cookie_error)}")
                    print("[INFO] Will try username/password login instead")
            else:
                print(f"[INFO] No valid cookies file found at: {COOKIES_FILE}")
                print("[INFO] Will use username/password login")
                
            # Login with credentials and save cookies
            if TWITTER_USERNAME and TWITTER_PASSWORD:
                print(f"[INFO] Logging in with username: {TWITTER_USERNAME[:3]}{'*' * (len(TWITTER_USERNAME)-3)}")
                
                # Log email usage (blank or provided)
                if TWITTER_EMAIL:
                    email_display = f"{TWITTER_EMAIL.split('@')[0][:3]}{'*' * 3}@{TWITTER_EMAIL.split('@')[1]}" if '@' in TWITTER_EMAIL else f"{TWITTER_EMAIL[:3]}{'*' * (len(TWITTER_EMAIL)-3)}"
                    print(f"[INFO] Using email: {email_display}")
                else:
                    print("[INFO] No email provided, using only username")
                
                # Attempt username/password login
                print("[INFO] Sending login credentials...")
                await self.client.login(
                    auth_info_1=TWITTER_USERNAME,
                    auth_info_2=TWITTER_EMAIL,
                    password=TWITTER_PASSWORD,
                    cookies_file=COOKIES_FILE
                )
                
                print(f"[INFO] Login successful. Cookies saved to: {COOKIES_FILE}")
                self.logged_in = True
                # Reset counters on successful login
                self.login_attempts = 0
                return True
            else:
                print("[ERROR] Twitter credentials not provided in config")
                return False
                
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Login failed: {error_msg}")
            
            # Provide more specific error information
            if "rate limit" in error_msg.lower():
                print("[INFO] Twitter rate limit reached. Please wait a few minutes before trying again.")
            elif "password" in error_msg.lower():
                print("[INFO] Password verification failed. Please check your password.")
            elif "challenge" in error_msg.lower() or "verification" in error_msg.lower():
                print("[INFO] Twitter is requesting additional verification. You may need to manually login once.")
            
            # Tampilkan informasi tentang percobaan yang tersisa
            attempts_left = self.max_login_attempts - self.login_attempts
            if attempts_left > 0:
                print(f"[INFO] {attempts_left} percobaan login tersisa sebelum cooldown {self.cooldown_minutes} menit")
            else:
                next_attempt_time = self.last_login_attempt_time + datetime.timedelta(minutes=self.cooldown_minutes)
                print(f"[PERINGATAN] Batas percobaan login tercapai. Silakan tunggu {self.cooldown_minutes} menit.")
                print(f"[INFO] Login dapat dicoba kembali pada: {next_attempt_time.strftime('%H:%M:%S')}")
            
            return False
    
    def generate_tweet_url(self, tweet_id, username):
        """Generate a direct URL to the tweet"""
        if not tweet_id or not username or username == "unknown":
            return None
        return f"https://twitter.com/{username}/status/{tweet_id}"
    
    async def search_latest_by_hashtag(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """Search for latest tweets with specific hashtag"""
        if not self.logged_in:
            print("[INFO] Not logged in yet. Attempting login...")
            if not await self.login():
                print("[ERROR] Login failed. Cannot search.")
                return []
        
        try:
            # Prepare search query properly (add # if not present for hashtags)
            search_query = hashtag
            if not hashtag.startswith('#') and not hashtag.startswith('$') and ' ' not in hashtag and hashtag not in ['airdrop']:
                search_query = f"#{hashtag}"
                
            print(f"[INFO] Searching for '{search_query}' with 'Latest' sort")
            
            # Search for tweets using twikit with 'Latest' sort
            search_start_time = time.time()
            print(f"[INFO] Sending API request to Twitter for {search_query}...")
            tweets_data = await self.client.search_tweet(search_query, 'Latest', limit)
            search_duration = time.time() - search_start_time
            
            # Log tweet count
            tweet_count = len(tweets_data) if tweets_data else 0
            print(f"[INFO] Received {tweet_count} tweets in {search_duration:.2f} seconds")
            
            # Convert to simplified dictionary format
            processed_tweets = []
            for idx, tweet in enumerate(tweets_data):
                try:
                    # Extract user information - use screen_name if username not available
                    username = None
                    if hasattr(tweet, 'user'):
                        if hasattr(tweet.user, 'username'):
                            username = tweet.user.username
                        elif hasattr(tweet.user, 'screen_name'):
                            username = tweet.user.screen_name
                        elif hasattr(tweet.user, 'name'):
                            username = tweet.user.name
                    
                    # If we still don't have a username, create one from the tweet
                    if not username:
                        # Generate a fake username based on the hashtag
                        username = f"crypto_user_{hashtag.replace('#', '').replace('$', '')}_{idx}"
                    
                    # Format tweet ID as string
                    tweet_id = str(tweet.id) if hasattr(tweet, 'id') else f"unknown_{int(time.time())}_{idx}"
                    
                    # Generate tweet URL
                    tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                    
                    # Create simple tweet object with only essential info
                    processed_tweet = {
                        "id": tweet_id,
                        "text": tweet.text if hasattr(tweet, 'text') else "",
                        "created_at": tweet.created_at.isoformat() if hasattr(tweet, 'created_at') and not isinstance(tweet.created_at, str) else tweet.created_at if hasattr(tweet, 'created_at') else datetime.now().isoformat(),
                        "author": {
                            "username": username,
                            "verified": tweet.user.verified if hasattr(tweet, 'user') and hasattr(tweet.user, 'verified') else False,
                            "followers": tweet.user.followers_count if hasattr(tweet, 'user') and hasattr(tweet.user, 'followers_count') else 0
                        },
                        "engagement": {
                            "likes": tweet.favorite_count if hasattr(tweet, 'favorite_count') else 0,
                            "retweets": tweet.retweet_count if hasattr(tweet, 'retweet_count') else 0
                        },
                        "hashtag": hashtag,
                        "score": self.calculate_relevance_score(tweet),
                        "search_query": search_query,
                        "tweet_url": tweet_url
                    }
                    
                    # Add URLs if present
                    if hasattr(tweet, 'urls') and tweet.urls:
                        processed_tweet["external_urls"] = tweet.urls
                    
                    processed_tweets.append(processed_tweet)
                    
                except Exception as e:
                    print(f"[ERROR] Error processing tweet {idx+1}: {str(e)}")
                    continue
            
            print(f"[INFO] Successfully processed {len(processed_tweets)} tweets for {hashtag}")
            return processed_tweets
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Search failed for {hashtag}: {error_msg}")
            
            # More detailed error handling, tetapi tidak menggunakan data mock
            if "404" in error_msg:
                print(f"[ERROR] Twitter API returned 404 error - API endpoint may have changed")
                return []
            elif "429" in error_msg:
                print(f"[ERROR] Rate limit exceeded (429 error). Skipping search for this hashtag.")
                return []
            elif "401" in error_msg:
                print(f"[INFO] Authentication error (401). Session may have expired. Attempting to re-login...")
                self.logged_in = False
                if await self.login():
                    # Try again with fresh login
                    return await self.search_latest_by_hashtag(hashtag, limit)
                else:
                    print(f"[ERROR] Re-login failed. Skipping search for this hashtag.")
                    return []
            else:
                print(f"[ERROR] Unknown error searching for {hashtag}. Skipping this hashtag.")
                return []
    
    def generate_mock_tweets(self, hashtag, limit):
        """Generate mock tweet data for testing when API fails"""
        print(f"[INFO] Generating {min(limit, 3)} mock tweets for {hashtag}")
        mock_tweets = []
        for i in range(min(limit, 3)):
            tweet_id = f"mock_{int(time.time())}_{i}"
            username = f"crypto_user_{i}"
            mock_tweets.append({
                "id": tweet_id,
                "text": f"This is a mock tweet about {hashtag} for testing purposes #{hashtag} #crypto #airdrop",
                "created_at": datetime.now().isoformat(),
                "author": {
                    "username": username,
                    "verified": i == 0,  # First user is verified
                    "followers": 5000 * (i + 1)
                },
                "engagement": {
                    "likes": 50 * (i + 1),
                    "retweets": 20 * (i + 1)
                },
                "hashtag": hashtag,
                "score": 25 - (i * 5),  # Decreasing scores
                "search_query": hashtag,
                "tweet_url": self.generate_tweet_url(tweet_id, username),
                "is_mock": True  # Flag to indicate this is mock data
            })
        print(f"[INFO] Created {len(mock_tweets)} mock tweets for testing (API fallback)")
        return mock_tweets
    
    def calculate_relevance_score(self, tweet) -> int:
        """Calculate a simple relevance score for crypto airdrop tweets"""
        score = 0
        
        # Author credibility
        if hasattr(tweet, 'user'):
            if hasattr(tweet.user, 'verified') and tweet.user.verified:
                score += 30
            
            if hasattr(tweet.user, 'followers_count'):
                if tweet.user.followers_count > 10000:
                    score += 20
                elif tweet.user.followers_count > 1000:
                    score += 10
        
        # Engagement score
        likes = tweet.favorite_count if hasattr(tweet, 'favorite_count') else 0
        retweets = tweet.retweet_count if hasattr(tweet, 'retweet_count') else 0
        engagement = likes + (retweets * 2)
        
        if engagement > 100:
            score += 20
        elif engagement > 50:
            score += 10
        
        # Content relevance
        if hasattr(tweet, 'text'):
            text = tweet.text.lower()
            if "airdrop" in text:
                score += 15
            if "free" in text and ("token" in text or "nft" in text):
                score += 10
            if "solana" in text or "$sol" in text or "#sol" in text:
                score += 15
            if "claim" in text:
                score += 5
            
            # Suspicious patterns (reduce score)
            if "send" in text and "eth" in text:
                score -= 30
            if "connect wallet" in text:
                score -= 10
        
        return max(0, score)  # Don't return negative scores
    
    async def monitor_all_hashtags(self, tweets_per_hashtag: int = 10) -> Dict[str, List[Dict]]:
        """Monitor all specified hashtags and return results"""
        if not self.logged_in and not await self.login():
            print("[ERROR] Not logged in. Cannot monitor hashtags.")
            return {"top_opportunities": []}
        
        results = {}
        total_tweets = 0
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries and total_tweets == 0:
            if retry_count > 0:
                print(f"[INFO] Percobaan ke-{retry_count+1} untuk mencari tweets (max: {max_retries})")
            
            results = {}
            total_tweets = 0
            
            for hashtag in HASHTAGS:
                print(f"[INFO] Searching for {hashtag}")
                tweets = await self.search_latest_by_hashtag(hashtag, tweets_per_hashtag)
                results[hashtag] = tweets
                total_tweets += len(tweets)
                
                # Add a small delay between searches to avoid rate limits
                await asyncio.sleep(1.5)
            
            if total_tweets == 0:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 5 * retry_count  # Increase wait time with each retry
                    print(f"[PERINGATAN] Tidak ada tweet yang ditemukan. Menunggu {wait_time} detik sebelum mencoba lagi...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[ERROR] Semua {max_retries} percobaan gagal. Tidak ada tweet yang ditemukan.")
            else:
                print(f"[INFO] Berhasil menemukan total {total_tweets} tweets dari {len(HASHTAGS)} hashtag")
        
        # Get combined results sorted by score
        all_tweets = []
        for hashtag_tweets in results.values():
            all_tweets.extend(hashtag_tweets)
        
        if not all_tweets:
            print("[PERINGATAN] Tidak ada tweet yang berhasil dikumpulkan")
            return {"top_opportunities": []}
        
        # Sort by score and timestamp (newest first for equal scores)
        sorted_tweets = sorted(all_tweets, key=lambda x: (x.get('score', 0), x.get('created_at', '')), reverse=True)
        
        # Remove duplicates (same tweet ID)
        unique_tweets = []
        seen_ids = set()
        
        for tweet in sorted_tweets:
            tweet_id = tweet.get('id')
            if tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                unique_tweets.append(tweet)
        
        # Add top results to the output
        top_opportunities = unique_tweets[:tweets_per_hashtag]
        results["top_opportunities"] = top_opportunities
        
        print(f"[INFO] Menghasilkan {len(top_opportunities)} peluang teratas setelah pemfilteran dan pengurutan")
        
        # Save the current results
        self.last_results = results
        
        return results
    
    def save_results_to_file(self, results: Dict[str, List[Dict]], filename: str = None) -> bool:
        """Save results to a JSON file"""
        if not filename:
            filename = OUTPUT_FILE
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Add timestamp
            data_to_save = {
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
            print(f"[INFO] Results saved to {filename}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save results: {str(e)}")
            return False
    
    async def run_periodic_monitoring(self, interval_minutes: int = 30, max_runs: int = None):
        """Run the monitoring process periodically"""
        run_count = 0
        
        while True:
            try:
                print(f"\n[INFO] Starting monitoring run #{run_count + 1}")
                start_time = time.time()
                
                # Run monitoring
                results = await self.monitor_all_hashtags(10)
                
                # Save results
                if results and results.get("top_opportunities"):
                    self.save_results_to_file(results)
                    
                    # Print top opportunities
                    print("\n[INFO] Top opportunities in this run:")
                    for i, tweet in enumerate(results.get("top_opportunities", [])[:5], 1):
                        print(f"{i}. [{tweet.get('score')}] @{tweet.get('author', {}).get('username', 'unknown')}: {tweet.get('text', '')[:100]}...")
                        if tweet.get('tweet_url'):
                            print(f"   URL: {tweet.get('tweet_url')}")
                
                # Increment run count
                run_count += 1
                
                # Check if we've reached the maximum number of runs
                if max_runs and run_count >= max_runs:
                    print(f"[INFO] Reached maximum number of runs ({max_runs}). Exiting.")
                    break
                
                # Calculate time to sleep
                elapsed = time.time() - start_time
                sleep_time = max(0, interval_minutes * 60 - elapsed)
                
                if sleep_time > 0:
                    print(f"[INFO] Waiting {sleep_time:.1f} seconds until next run...")
                    await asyncio.sleep(sleep_time)
                    
            except Exception as e:
                print(f"[ERROR] Error in monitoring run: {str(e)}")
                # Sleep a bit before retrying
                await asyncio.sleep(60)

# For testing
async def test_scraper():
    """Test the minimal scraper"""
    scraper = TwitterScraper()
    
    # Monitor hashtags once
    print("\nRunning single monitoring pass...")
    results = await scraper.monitor_all_hashtags(5)
    
    # Save results
    scraper.save_results_to_file(results)
    
    # Print top opportunities
    print("\nTop opportunities:")
    for i, tweet in enumerate(results.get("top_opportunities", []), 1):
        print(f"{i}. [{tweet.get('score')}] @{tweet.get('author', {}).get('username', 'unknown')}: {tweet.get('text', '')[:100]}...")
        if tweet.get('tweet_url'):
            print(f"   URL: {tweet.get('tweet_url')}")

async def run_continuous_monitoring():
    """Run continuous monitoring with a 30-minute interval"""
    scraper = TwitterScraper()
    await scraper.run_periodic_monitoring(interval_minutes=30, max_runs=None)

if __name__ == "__main__":
    try:
        # Choose the mode: test or continuous
        mode = "test"  # Change to "continuous" for ongoing monitoring
        
        if mode == "test":
            print("[INFO] Running in test mode (single pass)")
            asyncio.run(test_scraper())
        else:
            print("[INFO] Running in continuous mode")
            asyncio.run(run_continuous_monitoring())
            
    except KeyboardInterrupt:
        print("[INFO] Script was interrupted by user")
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")
    finally:
        print("[INFO] Script completed") 