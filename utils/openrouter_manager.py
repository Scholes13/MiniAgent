"""
OpenRouter API Manager with API key rotation
"""
import os
import json
import httpx
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .openrouter_config import (
    OPENROUTER_API_BASE,
    OPENROUTER_MODELS,
    DEFAULT_HEADERS,
    get_next_available_key,
    mark_key_limit_reached,
    reset_all_keys
)
from .cache_manager import AnalysisCache

class OpenRouterManager:
    """Manager for OpenRouter API with key rotation capability"""
    
    def __init__(self, prefer_free=False):
        """
        Initialize the OpenRouter manager
        
        Args:
            prefer_free: Whether to prefer using free models by default
        """
        self.api_base = OPENROUTER_API_BASE
        self.headers = DEFAULT_HEADERS.copy()
        
        # Tambahkan data policy headers berdasarkan dokumentasi
        # Ini diperlukan untuk menggunakan model gratis
        self.headers.update({
            "HTTP-Referer": "https://crypto-airdrop-analyzer.com",
            "X-Title": "Crypto Airdrop Analyzer",
            # Aktifkan semua policy untuk memastikan model gratis berfungsi
            "Data-Policy-1": "on", # Allow prompt to be used for improvement of OpenRouter
            "Data-Policy-2": "on", # Allow prompt to be shared with model providers
            "Data-Policy-3": "on", # Allow responses to be used for improvement of OpenRouter
            "Data-Policy-4": "on"  # Allow responses to be shared with model providers
        })
        
        self.current_key = None
        self.prefer_free = prefer_free
        self._refresh_api_key()
    
    def _refresh_api_key(self) -> bool:
        """Refresh the API key from the rotation pool"""
        self.current_key = get_next_available_key()
        if self.current_key:
            self.headers["Authorization"] = f"Bearer {self.current_key}"
            return True
        return False
    
    def _get_model_name(self, model: str) -> str:
        """
        Get the actual model name based on preferences
        
        Args:
            model: The model key or direct model name
            
        Returns:
            The actual model name to use
        """
        # Prefer paid models by default unless explicitly set to use free models
        if self.prefer_free:
            if model == "default":
                return OPENROUTER_MODELS.get("free-mistral")
            elif model == "smart":
                return OPENROUTER_MODELS.get("free-analysis") 
            elif model == "fast":
                return OPENROUTER_MODELS.get("free-mistral")
        
        # Otherwise use the standard mapping or the direct name
        return OPENROUTER_MODELS.get(model, model)
    
    async def _make_request(self, endpoint: str, payload: Dict[str, Any], 
                           method: str = "POST", attempt: int = 0) -> Optional[Dict[str, Any]]:
        """Make a request to OpenRouter API with retry and key rotation"""
        if attempt >= 3:  # Maximum 3 attempts
            return None
        
        if not self.current_key and not self._refresh_api_key():
            # No available keys
            return {"error": "No available API keys. All keys have reached their limit."}
        
        url = f"{self.api_base}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=payload, headers=self.headers)
                else:
                    response = await client.get(url, params=payload, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()
                
                # Handle API key limit errors for paid models first
                if response.status_code in [401, 403, 429]:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get("message", "")
                    
                    # Limit could be reached, quota exceeded, etc.
                    if any(msg in error_msg.lower() for msg in ["limit", "exceeded", "quota"]):
                        # If not using free model yet, try to fall back to free model
                        if not self.prefer_free and "model" in payload and ":free" not in payload.get("model", ""):
                            # Try to find a free alternative
                            model_base = payload["model"].split("/")[-1].split("-")[0]  # Extract base name
                            for key, value in OPENROUTER_MODELS.items():
                                if key.startswith("free-") and model_base.lower() in key.lower():
                                    payload["model"] = value
                                    print(f"Falling back to free model: {value}")
                                    return await self._make_request(endpoint, payload, method, attempt + 1)
                            
                            # If no matching free model, try default free model
                            payload["model"] = OPENROUTER_MODELS.get("free-mistral")
                            print(f"Falling back to default free model: {payload['model']}")
                            return await self._make_request(endpoint, payload, method, attempt + 1)
                            
                        # If already using free model or no free alternative, try rotating keys
                        if self.current_key:
                            mark_key_limit_reached(self.current_key)
                        
                        # Try to get a new key
                        if self._refresh_api_key():
                            # Retry with new key
                            return await self._make_request(endpoint, payload, method, attempt + 1)
                
                # Handle data policy errors for free models
                if response.status_code == 404 and "policy" in response.text.lower():
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get("message", "")
                    
                    # Try with a non-free model if this is a data policy error
                    if "policy" in error_msg.lower() and ":free" in payload.get("model", ""):
                        # Fall back to a paid model
                        if "model" in payload:
                            # Remove the :free suffix and try a paid alternative
                            model_base = payload["model"].split(":")[0]
                            for key, value in OPENROUTER_MODELS.items():
                                if not key.startswith("free-") and model_base in value:
                                    payload["model"] = value
                                    print(f"Falling back to paid model: {value}")
                                    return await self._make_request(endpoint, payload, method, attempt + 1)
                
                return {"error": f"API request failed: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    async def chat_completion(self, 
                             messages: List[Dict[str, str]], 
                             model: str = "default",
                             temperature: float = 0.7,
                             max_tokens: int = 1000,
                             stream: bool = False) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter
        
        Args:
            messages: List of message objects with role and content
            model: Model key from OPENROUTER_MODELS or full model name
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response dictionary from API
        """
        # Get actual model string based on preferences
        model_name = self._get_model_name(model)
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        return await self._make_request("chat/completions", payload)
    
    async def analyze_text(self, text: str, prompt: str = None, model: str = "smart") -> Dict[str, Any]:
        """
        Analyze text using a chat completion
        
        Args:
            text: Text to analyze
            prompt: Specific prompt instructions (optional)
            model: Model to use for analysis
            
        Returns:
            Analysis results
        """
        system_message = "You are an expert cryptocurrency analyst specializing in analyzing airdrops, tokenomics, and crypto projects."
        
        if prompt:
            system_message += f" {prompt}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": text}
        ]
        
        return await self.chat_completion(messages, model=model, temperature=0.3)
    
    async def generate_project_analysis(self, project_data: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive analysis for a crypto project
        
        Args:
            project_data: Project information including Twitter data, tokenomics, etc.
            use_cache: Whether to check cache before making API request
            
        Returns:
            Analysis dictionary with various scores and insights
        """
        # Check cache first if enabled
        if use_cache:
            cached_analysis = AnalysisCache.get_cached_analysis(project_data)
            if cached_analysis:
                return {
                    "success": True,
                    "analysis": cached_analysis,
                    "source": "cache"
                }
        
        # Format project data into a structured prompt
        prompt = f"""
        Project Name: {project_data.get('project_name', 'Unknown')}
        Token Symbol: {project_data.get('token_symbol', 'Unknown')}
        Description: {project_data.get('description', 'No description available')}
        
        Website: {project_data.get('website_url', 'Not provided')}
        Twitter: {project_data.get('twitter_handle', 'Not provided')}
        
        ## Project Background
        Team: {project_data.get('team_info', 'Limited information available')}
        Founded: {project_data.get('founded_date', 'Unknown')}
        Blockchain: {project_data.get('blockchain', 'Unknown')}
        Previous Projects: {project_data.get('previous_projects', 'No information')}
        
        ## Backing & Investors
        Investors: {project_data.get('investors', 'No information available')}
        Partnerships: {project_data.get('partnerships', 'No information available')}
        Funding Rounds: {project_data.get('funding_rounds', 'No information available')}
        Total Funding: {project_data.get('total_funding', 'Unknown')}
        
        ## Tokenomics
        Total Supply: {project_data.get('total_supply', 'Unknown')}
        Circulating Supply: {project_data.get('circulating_supply', 'Unknown')}
        Token Distribution: {project_data.get('token_distribution', 'No information available')}
        Vesting Schedule: {project_data.get('vesting_schedule', 'No information available')}
        Token Utility: {project_data.get('token_utility', 'Unknown')}
        Airdrop Percentage: {project_data.get('airdrop_percentage', 'Unknown')}
        
        ## Roadmap
        Current Phase: {project_data.get('current_phase', 'Unknown')}
        Upcoming Milestones: {project_data.get('upcoming_milestones', 'No information available')}
        Recent Achievements: {project_data.get('recent_achievements', 'No information available')}
        
        ## Social Statistics
        Twitter Followers: {project_data.get('twitter_followers', 'Unknown')}
        Engagement Rate: {project_data.get('engagement_rate', 'Unknown')}
        Tweet Frequency: {project_data.get('tweet_frequency', 'Unknown')}
        Community Size: {project_data.get('community_size', 'Unknown')}
        
        Conduct a thorough analysis of this crypto project focusing on:
        
        1. BACKGROUND CHECK: Investigate the legitimacy of the team, evaluate previous projects, and identify any red flags in their history.
        
        2. INVESTOR ANALYSIS: Evaluate the quality and credibility of backing investors and partners. Assess if there are any notable VCs or established crypto entities supporting the project.
        
        3. TOKENOMICS ASSESSMENT: Analyze token distribution (is it fair or concentrated?), supply mechanics, inflation rate, and token utility model. Evaluate if the token design makes economic sense.
        
        4. ROADMAP EVALUATION: Assess project roadmap feasibility, evaluate progress to date against promises, and determine likelihood of meeting future milestones.
        
        5. AIRDROP POTENTIAL: Based on all data, estimate likelihood of an airdrop, potential value, and qualification requirements. Consider token allocations for community.
        
        6. RISK FACTORS: Identify specific risks including regulatory concerns, competition, centralization issues, and technical challenges.
        
        7. INVESTMENT OUTLOOK: Provide short and long-term growth potential assessment based on fundamentals, not hype.
        
        Structure your analysis as a JSON object with the following fields:
        - legitimacy_score (1-10)
        - team_assessment (text)
        - investor_quality (text)
        - tokenomics_rating (1-10 with explanation)
        - roadmap_feasibility (1-10 with explanation)
        - airdrop_likelihood (percentage)
        - estimated_airdrop_value (range in USD)
        - primary_risks (array of risk factors)
        - growth_potential (text)
        - recommendation (text)
        - detailed_analysis (comprehensive text)
        """
        
        messages = [
            {"role": "system", "content": "You are an expert cryptocurrency analyst specializing in tokenomics, blockchain technology, and investment analysis. You have deep experience evaluating early-stage crypto projects and airdrops. Respond only with a valid JSON object based on the data provided."},
            {"role": "user", "content": prompt}
        ]
        
        # Use free model for analysis by default if prefer_free is enabled
        model = "free-analysis" if self.prefer_free else "smart"
        response = await self.chat_completion(messages, model=model, temperature=0.2, max_tokens=2000)
        
        # Try to extract JSON from the response
        try:
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                # Try to parse the JSON response
                try:
                    analysis = json.loads(content)
                    
                    # Cache successful analysis results
                    if use_cache:
                        AnalysisCache.cache_analysis(project_data, analysis)
                    
                    return {
                        "success": True,
                        "analysis": analysis,
                        "source": "api",
                        "raw_response": response
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse AI response as JSON",
                        "raw_response": response
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing response: {str(e)}",
                "raw_response": response
            }
        
        return {
            "success": False,
            "error": "Invalid response format",
            "raw_response": response
        }
    
    async def analyze_code(self, code: str, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze or generate code using a specialized code model
        
        Args:
            code: Code or code specification to analyze/generate
            prompt: Specific instructions (optional)
            
        Returns:
            Analysis or generated code results
        """
        system_message = "You are an expert programmer specialized in blockchain and cryptocurrency technologies."
        
        if prompt:
            system_message += f" {prompt}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": code}
        ]
        
        # Use free code model by default if prefer_free is enabled
        model = "free-code" if self.prefer_free else "powerful"
        return await self.chat_completion(messages, model=model, temperature=0.1, max_tokens=2000)
    
    async def scrape_assistant(self, query: str) -> Dict[str, Any]:
        """
        Get assistance with scraping strategies or data extraction
        
        Args:
            query: Description of scraping needs or data to extract
            
        Returns:
            Assistance with scraping strategies
        """
        system_message = (
            "You are an expert in web scraping, data extraction, and cryptocurrency information retrieval. "
            "Help the user with strategic advice for scraping crypto-related information efficiently."
        )
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ]
        
        # Use free scraper model by default if prefer_free is enabled
        model = "free-scraper" if self.prefer_free else "fast"
        return await self.chat_completion(messages, model=model, temperature=0.5, max_tokens=1500)
    
    def reset_api_keys(self):
        """Reset all API keys to available state (e.g., daily reset)"""
        reset_all_keys()
        self._refresh_api_key()
        return {"success": True, "message": "All API keys have been reset"}
    
    def set_prefer_free(self, prefer_free: bool):
        """Set whether to prefer free models"""
        self.prefer_free = prefer_free
        return {"success": True, "prefer_free": prefer_free}
    
    def clear_cache(self):
        """Clear expired cache entries"""
        cleared = AnalysisCache.clear_expired_cache()
        return {"success": True, "cleared_entries": cleared}
    
    def get_cache_stats(self):
        """Get statistics about the cache"""
        return AnalysisCache.get_cache_stats() 