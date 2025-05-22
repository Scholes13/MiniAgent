"""
Airdrop Pipeline - Proses data Twitter, analisis dengan AI, dan simpan ke Supabase
"""
import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import twitter scraper
from scraper.twitter_scraper import TwitterScraper

# Import OpenRouter manager for AI processing
from utils.openrouter_manager import OpenRouterManager

# Import Supabase for database storage
from supabase import create_client, Client

# Config
from utils.config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    AIRDROP_TABLE,
    API_CALL_DELAY_SECONDS,
    PIPELINE_RUN_INTERVAL_MINUTES
)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AirdropPipeline:
    """Pipeline for processing Twitter data, analyzing with AI, and storing in Supabase"""
    
    def __init__(self):
        """Initialize the pipeline components"""
        self.twitter_scraper = TwitterScraper()
        self.ai_processor = OpenRouterManager()  # Default to using paid models
        self.processed_count = 0
        self.start_time = datetime.now()
        print(f"[INISIALISASI] Pipeline Airdrop dimulai pada {self.start_time.isoformat()}")
    
    async def scrape_twitter_data(self, tweets_per_hashtag: int = 10) -> Dict[str, List[Dict]]:
        """Step 1: Scrape data from Twitter"""
        print(f"[LANGKAH 1/3] Mulai mengumpulkan data Twitter dari beberapa hashtag populer...")
        twitter_data = await self.twitter_scraper.monitor_all_hashtags(tweets_per_hashtag)
        
        if not twitter_data or not twitter_data.get("top_opportunities"):
            print("[PERINGATAN] Tidak ada data Twitter yang berhasil dikumpulkan")
            return {}
        
        top_opportunities = twitter_data.get("top_opportunities", [])
        print(f"[LANGKAH 1/3 SELESAI] Berhasil mengumpulkan {len(top_opportunities)} peluang potensial dari Twitter")
        return twitter_data
    
    async def analyze_with_ai(self, twitter_data: Dict[str, List[Dict]]) -> List[Dict]:
        """Step 2: Process the collected data with AI"""
        if not twitter_data or not twitter_data.get("top_opportunities"):
            print("[PERINGATAN] Tidak ada data untuk dianalisis AI")
            return []
        
        print(f"[LANGKAH 2/3] Mulai analisis data Twitter dengan model AI...")
        top_opportunities = twitter_data.get("top_opportunities", [])
        analyzed_opportunities = []
        
        for idx, tweet in enumerate(top_opportunities):
            try:
                tweet_id = tweet.get("id", "unknown")
                author = tweet.get("author", {}).get("username", "unknown")
                
                print(f"[ANALISIS TWEET {idx+1}/{len(top_opportunities)}] Menganalisis tweet dari @{author} (ID: {tweet_id})")
                
                # Prepare tweet data for AI analysis
                tweet_text = tweet.get("text", "")
                tweet_url = tweet.get("tweet_url", "")
                followers = tweet.get("author", {}).get("followers", 0)
                
                # Skip if tweet is too short or lacks substance
                if len(tweet_text) < 10:
                    print(f"[TWEET DILEWATI] Tweet {idx+1}/{len(top_opportunities)} terlalu pendek untuk dianalisis")
                    continue
                
                # Create prompt for AI analysis
                prompt = self._create_ai_prompt(tweet)
                
                # Process with OpenRouter
                print(f"[ANALISIS DIMULAI] Mengirimkan tweet ke model AI untuk analisis mendalam...")
                ai_result = await self._process_with_openrouter(prompt)
                
                if not ai_result:
                    print(f"[ANALISIS GAGAL] Gagal mendapatkan analisis AI untuk tweet {idx+1}/{len(top_opportunities)}")
                    continue
                
                # Combine original tweet data with AI analysis
                analyzed_tweet = {
                    **tweet,
                    "ai_analysis": ai_result,
                    "processed_at": datetime.now().isoformat()
                }
                
                analyzed_opportunities.append(analyzed_tweet)
                
                project = ai_result.get("related_crypto", "Unknown")
                legitimacy = ai_result.get("is_legitimate", "Unknown")
                risk = ai_result.get("risk_level", "Unknown")
                
                print(f"[ANALISIS SELESAI] Tweet {idx+1}/{len(top_opportunities)} berhasil dianalisis:")
                print(f"  - Proyek: {project}")
                print(f"  - Legitimasi: {legitimacy}")
                print(f"  - Tingkat Risiko: {risk}")
                
                # Add a small delay between API calls to respect rate limits
                await asyncio.sleep(API_CALL_DELAY_SECONDS)
                
            except Exception as e:
                print(f"[ERROR] Gagal menganalisis tweet {idx+1}/{len(top_opportunities)}: {str(e)}")
                continue
        
        print(f"[LANGKAH 2/3 SELESAI] Analisis AI selesai. Berhasil menganalisis {len(analyzed_opportunities)}/{len(top_opportunities)} tweets")
        return analyzed_opportunities
    
    def _create_ai_prompt(self, tweet: Dict) -> str:
        """Create a prompt for AI analysis based on tweet data"""
        tweet_text = tweet.get("text", "")
        tweet_url = tweet.get("tweet_url", "")
        author = tweet.get("author", {})
        username = author.get("username", "unknown")
        verified = "verified" if author.get("verified") else "unverified"
        followers = author.get("followers", 0)
        
        return f"""
Analyze this cryptocurrency tweet for airdrop or token opportunity:

Tweet: "{tweet_text}"
Author: @{username} ({verified} account with {followers} followers)
URL: {tweet_url}

Please provide the following assessment:
1. Is this a legitimate airdrop or token opportunity? (Yes/No/Maybe)
2. What cryptocurrency or blockchain is this related to?
3. What action is required? (e.g., follow account, submit wallet, join community)
4. Risk level (Low/Medium/High) and explanation
5. Estimated value or potential (if determinable)
6. Step-by-step guide for claiming (if applicable)

Format the response as a JSON object with the following structure:
{{
  "is_legitimate": "Yes/No/Maybe",
  "related_crypto": "Blockchain/Token name",
  "required_action": "Description of required actions",
  "risk_level": "Low/Medium/High",
  "risk_explanation": "Brief explanation of risks",
  "estimated_value": "Description or range if applicable",
  "claim_steps": ["Step 1", "Step 2", ...],
  "additional_notes": "Any other relevant information"
}}
"""
    
    async def _process_with_openrouter(self, prompt: str) -> Optional[Dict]:
        """Process the prompt with OpenRouter"""
        try:
            # Create message payload for OpenRouter
            messages = [
                {"role": "system", "content": "You are a cryptocurrency expert specializing in identifying legitimate airdrops and token opportunities. Be thorough but concise in your analysis."},
                {"role": "user", "content": prompt}
            ]
            
            # Use the OpenRouterManager to send the request with the "smart" model
            response = await self.ai_processor.chat_completion(
                messages=messages,
                model="smart",  # Uses the smarter model defined in openrouter_config.py
                temperature=0.2,
                max_tokens=1000
            )
            
            if "error" in response:
                print(f"[ERROR] OpenRouter error: {response.get('error')}")
                return None
            
            # Extract the content from response
            ai_response = response["choices"][0]["message"]["content"].strip()
            
            # Extract and parse JSON response
            try:
                # Find JSON content if it's within other text
                json_start = ai_response.find("{")
                json_end = ai_response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = ai_response[json_start:json_end]
                    return json.loads(json_content)
                else:
                    return {"error": "No valid JSON found in response", "raw_response": ai_response}
            except json.JSONDecodeError:
                return {"error": "Failed to parse AI response as JSON", "raw_response": ai_response}
                
        except Exception as e:
            print(f"[ERROR] AI processing error: {str(e)}")
            return None
    
    async def store_in_supabase(self, analyzed_data: List[Dict]) -> bool:
        """Step 3: Store the analyzed data in Supabase using new relational schema"""
        if not analyzed_data:
            print("[PERINGATAN] Tidak ada data yang dianalisis untuk disimpan ke database")
            return False
        
        print(f"[LANGKAH 3/3] Menyimpan {len(analyzed_data)} peluang yang sudah dianalisis ke database...")
        success_count = 0
        
        # Test Supabase connection
        try:
            test_response = supabase.table("projects").select("id").limit(1).execute()
            print(f"[KONEKSI DATABASE] Berhasil terhubung ke database Supabase.")
        except Exception as e:
            print(f"[ERROR DATABASE] Gagal terhubung ke Supabase: {str(e)}")
        
        for idx, item in enumerate(analyzed_data):
            try:
                tweet_text = item.get("text", "No text")
                tweet_id = item.get("id", f"tweet_{idx}")
                tweet_url = item.get("tweet_url", "")
                author = item.get("author", {})
                author_name = author.get("name", "Unknown")
                author_username = author.get("username", "Unknown")
                followers = author.get("followers", 0)
                verified = author.get("verified", False)
                ai_analysis = item.get("ai_analysis", {})
                
                # Get related crypto from AI analysis
                related_crypto = ai_analysis.get("related_crypto", "Unknown")
                is_legitimate = ai_analysis.get("is_legitimate", "Unknown")
                risk_level = ai_analysis.get("risk_level", "High")
                
                print(f"[PENYIMPANAN {idx+1}/{len(analyzed_data)}] Menyimpan data untuk tweet dari @{author_username} tentang {related_crypto}")
                
                # 1. First check if project exists based on related_crypto from AI analysis
                project_query = supabase.table("projects") \
                    .select("id") \
                    .eq("project_name", related_crypto) \
                    .execute()
                
                project_id = None
                
                # 2. If project doesn't exist, create it
                if not project_query.data:
                    print(f"[DATABASE] Membuat proyek baru untuk {related_crypto}")
                    
                    # Convert token symbol if identified
                    token_symbol = related_crypto.upper() if len(related_crypto) <= 5 else None
                    
                    # Create project record
                    project_data = {
                        "project_name": related_crypto,
                        "token_symbol": token_symbol,
                        "description": f"Project discovered via Twitter analysis: {tweet_text[:100]}...",
                        "twitter_handle": author_username
                    }
                    
                    project_response = supabase.table("projects").insert(project_data).execute()
                    
                    if project_response.data:
                        project_id = project_response.data[0]["id"]
                        print(f"[DATABASE] Proyek baru berhasil dibuat dengan ID: {project_id}")
                    else:
                        print(f"[ERROR DATABASE] Gagal membuat proyek untuk {related_crypto}")
                        continue
                else:
                    project_id = project_query.data[0]["id"]
                    print(f"[DATABASE] Menggunakan proyek yang sudah ada dengan ID: {project_id}")
                
                # 3. Insert Twitter data
                twitter_data = {
                    "project_id": project_id,
                    "tweet_id": tweet_id,
                    "tweet_text": tweet_text,
                    "tweet_url": tweet_url,
                    "author_name": author_name,
                    "author_username": author_username,
                    "followers_count": followers,
                    "verified": verified,
                    "engagement_score": item.get("score", 0)
                }
                
                # Check if tweet already exists to avoid duplicates
                existing_tweet = supabase.table("twitter_data") \
                    .select("id") \
                    .eq("tweet_id", tweet_id) \
                    .execute()
                
                if not existing_tweet.data:
                    twitter_response = supabase.table("twitter_data").insert(twitter_data).execute()
                    
                    if not twitter_response.data:
                        print(f"[ERROR DATABASE] Gagal menyimpan data Twitter untuk tweet {idx+1}/{len(analyzed_data)}")
                    else:
                        print(f"[DATABASE] Data Twitter berhasil disimpan untuk tweet {idx+1}/{len(analyzed_data)}")
                else:
                    print(f"[DATABASE] Tweet {tweet_id} sudah ada dalam database, melewati penyimpanan duplikat")
                
                # 4. Insert AI analysis
                # Convert legitimacy from Yes/No/Maybe to score
                legitimacy_score = 8 if is_legitimate == "Yes" else (5 if is_legitimate == "Maybe" else 2)
                # Convert risk from Low/Medium/High to potential score
                potential_score = 8 if risk_level == "Low" else (5 if risk_level == "Medium" else 3)
                
                analysis_data = {
                    "project_id": project_id,
                    "legitimacy_score": legitimacy_score,
                    "potential_score": potential_score,
                    "revenue_estimate": ai_analysis.get("estimated_value", "Unknown"),
                    "risk_level": risk_level,
                    "overall_rating": (legitimacy_score + potential_score) // 2,
                    "analysis_text": json.dumps(ai_analysis),
                    "ai_model_used": "OpenRouter"
                }
                
                analysis_response = supabase.table("ai_analysis").insert(analysis_data).execute()
                
                if analysis_response.data:
                    print(f"[DATABASE] Analisis AI berhasil disimpan untuk proyek {project_id}")
                    success_count += 1
                    print(f"[PENYIMPANAN BERHASIL] Data tweet {idx+1}/{len(analyzed_data)} berhasil disimpan dan dianalisis secara lengkap")
                else:
                    print(f"[ERROR DATABASE] Gagal menyimpan analisis AI untuk proyek {project_id}")
                
                # 5. Insert tokenomics data if available
                if "token_utility" in ai_analysis or "airdrop_percentage" in ai_analysis:
                    try:
                        # Extract airdrop percentage if mentioned
                        airdrop_percent = None
                        if "airdrop_percentage" in ai_analysis:
                            airdrop_text = ai_analysis["airdrop_percentage"]
                            # Try to extract percentage
                            import re
                            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', airdrop_text)
                            if percentage_match:
                                airdrop_percent = float(percentage_match.group(1))
                        
                        tokenomics_data = {
                            "project_id": project_id,
                            "airdrop_percentage": airdrop_percent,
                            "token_type": "Unknown",  # Default values
                            "blockchain": related_crypto.split()[0] if " " in related_crypto else related_crypto
                        }
                        
                        supabase.table("tokenomics").insert(tokenomics_data).execute()
                        print(f"[DATABASE] Data tokenomics berhasil disimpan untuk proyek {project_id}")
                    except Exception as token_error:
                        print(f"[ERROR DATABASE] Gagal menyimpan data tokenomics: {str(token_error)}")
                
            except Exception as e:
                print(f"[ERROR DATABASE] Gagal menyimpan data untuk item {idx+1}/{len(analyzed_data)}: {str(e)}")
                continue
        
        print(f"[LANGKAH 3/3 SELESAI] Penyimpanan database selesai. Berhasil menyimpan {success_count}/{len(analyzed_data)} item")
        return success_count > 0
    
    async def run_pipeline(self, tweets_per_hashtag: int = 10) -> bool:
        """Run the complete pipeline: Twitter -> AI -> Supabase"""
        print(f"[PIPELINE DIMULAI] ===== MEMULAI ANALISIS PELUANG AIRDROP =====")
        self.start_time = datetime.now()
        
        try:
            # Step 1: Scrape Twitter data
            print(f"\n[TAHAP 1/3] PENGUMPULAN DATA TWITTER")
            retry_count = 0
            max_retries = 3
            twitter_data = {}
            
            # Coba beberapa kali jika diperlukan
            while retry_count < max_retries and (not twitter_data or not twitter_data.get("top_opportunities")):
                if retry_count > 0:
                    wait_time = 60 * retry_count
                    print(f"[RETRY] Percobaan ke-{retry_count+1} mengumpulkan data Twitter. Menunggu {wait_time} detik...")
                    await asyncio.sleep(wait_time)
                    print(f"[RETRY] Memulai percobaan ke-{retry_count+1}...")
                
                twitter_data = await self.scrape_twitter_data(tweets_per_hashtag)
                
                if not twitter_data or not twitter_data.get("top_opportunities"):
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"[PIPELINE BERHENTI] Gagal mengumpulkan data Twitter setelah {max_retries} percobaan. Pipeline dihentikan.")
                        return False
            
            # Step 2: Analyze with AI
            print(f"\n[TAHAP 2/3] ANALISIS DATA DENGAN AI")
            analyzed_data = await self.analyze_with_ai(twitter_data)
            if not analyzed_data:
                print("[PIPELINE BERHENTI] Gagal menganalisis data dengan AI. Pipeline dihentikan.")
                return False
            
            # Step 3: Store in Supabase
            print(f"\n[TAHAP 3/3] PENYIMPANAN DATA KE DATABASE")
            storage_result = await self.store_in_supabase(analyzed_data)
            if not storage_result:
                print("[PIPELINE BERHENTI] Gagal menyimpan data ke database. Pipeline dihentikan.")
                return False
            
            # Pipeline complete
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.processed_count += len(analyzed_data)
            
            print(f"\n[PIPELINE SELESAI] ===== ANALISIS BERHASIL DISELESAIKAN =====")
            print(f"[RINGKASAN] Pipeline selesai dalam {duration:.2f} detik")
            print(f"[RINGKASAN] {len(analyzed_data)} item diproses dalam sesi ini, total {self.processed_count} item")
            return True
            
        except Exception as e:
            print(f"[ERROR PIPELINE] Terjadi kesalahan: {str(e)}")
            return False
    
    async def run_periodic_pipeline(self, interval_minutes: int = PIPELINE_RUN_INTERVAL_MINUTES, max_runs: int = None):
        """Run the pipeline periodically"""
        run_count = 0
        
        while True:
            try:
                print(f"\n\n[SIKLUS #{run_count + 1}] ===== MEMULAI SIKLUS ANALISIS BARU =====")
                start_time = time.time()
                
                # Run the pipeline
                success = await self.run_pipeline(10)
                status_msg = "BERHASIL" if success else "GAGAL"
                print(f"[SIKLUS #{run_count + 1}] Siklus analisis {status_msg}")
                
                # Increment run count
                run_count += 1
                
                # Check if we've reached the maximum number of runs
                if max_runs and run_count >= max_runs:
                    print(f"[SIKLUS SELESAI] Mencapai jumlah maksimum siklus ({max_runs}). Program berhenti.")
                    break
                
                # Calculate time to sleep
                elapsed = time.time() - start_time
                sleep_time = max(0, interval_minutes * 60 - elapsed)
                
                if sleep_time > 0:
                    next_time = datetime.now() + datetime.timedelta(seconds=sleep_time)
                    print(f"[ISTIRAHAT] Menunggu {sleep_time/60:.1f} menit sampai siklus berikutnya...")
                    print(f"[ISTIRAHAT] Siklus berikutnya akan dimulai pada: {next_time.strftime('%H:%M:%S')}")
                    await asyncio.sleep(sleep_time)
                    
            except Exception as e:
                print(f"[ERROR SIKLUS] Terjadi kesalahan dalam siklus pipeline: {str(e)}")
                # Sleep a bit before retrying
                print(f"[PEMULIHAN] Menunggu 60 detik sebelum mencoba lagi...")
                await asyncio.sleep(60)

# For testing
async def test_pipeline():
    """Test the airdrop pipeline with a single run"""
    print("[MODE PENGUJIAN] Menjalankan pipeline dalam mode pengujian (satu kali jalan)")
    pipeline = AirdropPipeline()
    result = await pipeline.run_pipeline(5)
    status = "BERHASIL" if result else "GAGAL"
    print(f"[HASIL PENGUJIAN] Pipeline {status}")

async def run_continuous_pipeline():
    """Run continuous pipeline with a 60-minute interval"""
    print("[MODE BERKELANJUTAN] Menjalankan pipeline dalam mode berkelanjutan dengan interval waktu tertentu")
    pipeline = AirdropPipeline()
    print(f"[KONFIGURASI] Interval antar siklus: {PIPELINE_RUN_INTERVAL_MINUTES} menit")
    await pipeline.run_periodic_pipeline(interval_minutes=PIPELINE_RUN_INTERVAL_MINUTES, max_runs=None)

if __name__ == "__main__":
    try:
        # Choose the mode: test or continuous
        mode = "test"  # Change to "continuous" for ongoing monitoring
        
        if mode == "test":
            print("\n===== CRYPTO AIRDROP ANALYZER - MODE PENGUJIAN =====")
            asyncio.run(test_pipeline())
        else:
            print("\n===== CRYPTO AIRDROP ANALYZER - MODE BERKELANJUTAN =====")
            asyncio.run(run_continuous_pipeline())
            
    except KeyboardInterrupt:
        print("\n[BERHENTI] Program dihentikan oleh pengguna")
    except Exception as e:
        print(f"\n[ERROR FATAL] Terjadi kesalahan fatal: {str(e)}")
    finally:
        print("\n===== PROGRAM SELESAI =====") 