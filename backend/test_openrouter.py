"""
Simple test script for OpenRouter configuration
"""
import os
import sys
import json
import asyncio
import time

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from utils.openrouter_manager import OpenRouterManager
from utils.openrouter_config import OPENROUTER_MODELS

async def test_basic_usage():
    """Test basic usage with default settings"""
    print("Testing OpenRouter Configuration\n")
    
    # Create default manager - should use paid models by default
    default_manager = OpenRouterManager()  # default is prefer_free=False
    
    # Test prompt
    prompt = "What are the best crypto airdrops to look for in 2024?"
    
    messages = [
        {"role": "system", "content": "You are a helpful cryptocurrency expert."},
        {"role": "user", "content": prompt}
    ]
    
    # Test default (paid) model
    print("Using default paid model...")
    paid_start = time.time()
    paid_response = await default_manager.chat_completion(
        messages=messages,
        model="smart",  # Should use Claude by default
        max_tokens=200
    )
    paid_end = time.time()
    
    if "error" in paid_response:
        print(f"Paid model error: {paid_response['error']}")
    else:
        paid_model = paid_response.get("model", "unknown")
        paid_content = paid_response["choices"][0]["message"]["content"]
        
        print(f"Response from: {paid_model}")
        print(f"Time taken: {paid_end - paid_start:.2f} seconds")
        print(f"Response: {paid_content[:300]}...\n")
    
    # Small delay
    await asyncio.sleep(1)
    
    # Create manager with free model preference for testing
    free_manager = OpenRouterManager(prefer_free=True)
    
    # Test free model
    print("\nUsing free model (forced)...")
    free_start = time.time()
    free_response = await free_manager.chat_completion(
        messages=messages,
        model="default",  # Should map to a free model with prefer_free=True
        max_tokens=200
    )
    free_end = time.time()
    
    if "error" in free_response:
        print(f"Free model error: {free_response['error']}")
    else:
        free_model = free_response.get("model", "unknown")
        free_content = free_response["choices"][0]["message"]["content"]
        
        print(f"Response from: {free_model}")
        print(f"Time taken: {free_end - free_start:.2f} seconds")
        print(f"Response: {free_content[:300]}...\n")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_basic_usage()) 