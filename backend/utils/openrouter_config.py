"""
OpenRouter configuration and API key management
"""
import os
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

# Create data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Path to the API keys file
API_KEYS_FILE = os.path.join(DATA_DIR, "openrouter_keys.json")

# Default configuration for OpenRouter API
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# Model configurations including free models
OPENROUTER_MODELS = {
    # Original models
    "default": "anthropic/claude-3-haiku",
    "fast": "anthropic/claude-3-haiku",
    "smart": "anthropic/claude-3-sonnet",
    "vision": "anthropic/claude-3-opus",
    "balanced": "openai/gpt-3.5-turbo",
    "powerful": "openai/gpt-4-turbo",
    
    # Free models - updated with verified working models
    "free-deepseek-v3": "deepseek/deepseek-chat-v3-0324:free",  
    "free-llama": "meta-llama/llama-3.1-8b-instruct:free",
    "free-mistral": "mistralai/mistral-7b-instruct:free",
    "free-gemini": "google/gemma-3-4b-it:free",
    
    # Aliases for specific use cases (using free models)
    "free-analysis": "mistralai/mistral-7b-instruct:free",      # For crypto analysis
    "free-scraper": "meta-llama/llama-3.1-8b-instruct:free",    # For scraping assistance
    "free-code": "mistralai/mistral-7b-instruct:free",          # For code generation
}

# Default headers for OpenRouter API requests
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    # Site information 
    "HTTP-Referer": "https://crypto-airdrop-analyzer.com",
    "X-Title": "Crypto Airdrop Analyzer",
    # Data policy settings - required for using free models
    "Data-Policy-1": "on",  # Allow prompt to be used for improvement of OpenRouter
    "Data-Policy-2": "on",  # Allow prompt to be shared with model providers
    "Data-Policy-3": "on",  # Allow responses to be used for improvement of OpenRouter
    "Data-Policy-4": "on"   # Allow responses to be shared with model providers
}

# Initialize with provided API key
DEFAULT_API_KEYS = [
    {
        "key": "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",
        "limit_reached": False,
        "last_used": None,
        "usage_count": 0
    }
]

def save_api_keys(keys: List[Dict[str, Any]]) -> None:
    """Save API keys to file"""
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def load_api_keys() -> List[Dict[str, Any]]:
    """Load API keys from file or initialize with default"""
    if not os.path.exists(API_KEYS_FILE):
        save_api_keys(DEFAULT_API_KEYS)
        return DEFAULT_API_KEYS
    
    try:
        with open(API_KEYS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        save_api_keys(DEFAULT_API_KEYS)
        return DEFAULT_API_KEYS

def add_api_key(key: str) -> None:
    """Add a new API key to the rotation"""
    keys = load_api_keys()
    
    # Check if key already exists
    if any(k["key"] == key for k in keys):
        return
    
    keys.append({
        "key": key,
        "limit_reached": False,
        "last_used": None,
        "usage_count": 0
    })
    
    save_api_keys(keys)

def remove_api_key(key: str) -> None:
    """Remove an API key from the rotation"""
    keys = load_api_keys()
    keys = [k for k in keys if k["key"] != key]
    save_api_keys(keys)

def mark_key_limit_reached(key: str) -> None:
    """Mark a key as having reached its limit"""
    keys = load_api_keys()
    for k in keys:
        if k["key"] == key:
            k["limit_reached"] = True
    save_api_keys(keys)

def get_next_available_key() -> Optional[str]:
    """Get the next available API key for rotation"""
    keys = load_api_keys()
    available_keys = [k for k in keys if not k["limit_reached"]]
    
    if not available_keys:
        return None
    
    # Sort by usage count and last used
    available_keys.sort(key=lambda k: (k["usage_count"], k["last_used"] or ""))
    selected_key = available_keys[0]
    
    # Update usage information
    for k in keys:
        if k["key"] == selected_key["key"]:
            k["last_used"] = datetime.now().isoformat()
            k["usage_count"] += 1
    
    save_api_keys(keys)
    return selected_key["key"]

def reset_all_keys() -> None:
    """Reset all keys to not limited state"""
    keys = load_api_keys()
    for k in keys:
        k["limit_reached"] = False
    save_api_keys(keys)

def get_all_keys_status() -> List[Dict[str, Any]]:
    """Get status of all API keys"""
    keys = load_api_keys()
    # Return without actual API keys for security
    return [
        {
            "id": i+1,
            "key_hint": f"{k['key'][:8]}...{k['key'][-4:]}",
            "limit_reached": k["limit_reached"],
            "last_used": k["last_used"],
            "usage_count": k["usage_count"]
        } for i, k in enumerate(keys)
    ] 