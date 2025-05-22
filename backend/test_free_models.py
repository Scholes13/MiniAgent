"""
Test script for OpenRouter models
"""
import os
import sys
import json
import asyncio
import httpx
from typing import Dict, Any

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from utils.openrouter_manager import OpenRouterManager
from utils.openrouter_config import OPENROUTER_MODELS

async def test_claude_model():
    """Test Claude model that we know works"""
    print("Testing Claude OpenRouter Model\n")
    
    # Initialize manager with preference for paid models
    manager = OpenRouterManager(prefer_free=False)
    
    # Test with Claude model
    model_key = "smart"  # This maps to Claude-3-Sonnet
    model_name = OPENROUTER_MODELS.get(model_key)
    
    print(f"Testing model: {model_key} ({model_name})")
    print(f"{'='*50}\n")
    
    # Test prompt
    prompt = "What is the future of cryptocurrency?"
    
    messages = [
        {"role": "system", "content": "You are a helpful cryptocurrency expert."},
        {"role": "user", "content": prompt}
    ]
    
    # Make request
    print("Sending request...")
    start_time = asyncio.get_event_loop().time()
    response = await manager.chat_completion(
        messages=messages,
        model=model_key,
        max_tokens=200
    )
    end_time = asyncio.get_event_loop().time()
    
    # Handle error
    if "error" in response:
        print(f"Error: {response['error']}")
        print(f"Headers used: {json.dumps(manager.headers, indent=2)}")
        return
    
    # Extract response
    try:
        model_used = response.get("model", "unknown")
        tokens = response.get("usage", {})
        content = response["choices"][0]["message"]["content"]
        
        print(f"Response from: {model_used}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Tokens: {json.dumps(tokens, indent=2)}")
        print(f"Response: {content}")
    except (KeyError, IndexError) as e:
        print(f"Unexpected response format: {e}")
        print(f"Raw response: {json.dumps(response, indent=2)}")

async def test_specific_free_model():
    """Test with a specific free model that appears in the list"""
    print("\n\nTesting Specific Free Model\n")
    
    # Initialize manager
    manager = OpenRouterManager(prefer_free=True)
    
    # Get a free model directly from the list we saw
    # We'll try with Mistral 7B since it's a well-known model
    free_model = "mistralai/mistral-7b-instruct:free"
    
    print(f"Testing model: {free_model}")
    print(f"{'='*50}\n")
    
    # Test prompt
    prompt = "What is the future of cryptocurrency?"
    
    messages = [
        {"role": "system", "content": "You are a helpful cryptocurrency expert."},
        {"role": "user", "content": prompt}
    ]
    
    # Update headers with stronger privacy settings
    original_headers = manager.headers.copy()
    privacy_headers = {
        "HTTP-Referer": "https://crypto-airdrop-analyzer.com",
        "X-Title": "Crypto Airdrop Analyzer",
        "Data-Policy-1": "on", 
        "Data-Policy-2": "on", 
        "Data-Policy-3": "on", 
        "Data-Policy-4": "on"
    }
    manager.headers.update(privacy_headers)
    
    # Prepare the payload directly
    payload = {
        "model": free_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    # Make request
    print("Sending request...")
    url = f"{manager.api_base}/chat/completions"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=manager.headers
            )
        
        if response.status_code == 200:
            result = response.json()
            model_used = result.get("model", "unknown")
            content = result["choices"][0]["message"]["content"]
            
            print(f"Response from: {model_used}")
            print(f"Response: {content}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    # Restore original headers
    manager.headers = original_headers
        
async def test_model_info():
    """Get available model information"""
    print("\nGetting model information\n")
    
    # Initialize manager
    manager = OpenRouterManager(prefer_free=False)
    
    # API URL for models endpoint
    url = f"{manager.api_base}/models"
    
    # Make request
    print("Sending request to models endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=manager.headers
        )
    
    if response.status_code == 200:
        models_data = response.json()
        print(f"Available models: {len(models_data.get('data', []))}")
        
        # Look for free models
        free_models = [m for m in models_data.get('data', []) if ":free" in m.get('id', '')]
        print(f"Free models: {len(free_models)}")
        
        for model in free_models:
            print(f"- {model.get('id')}: {model.get('name')}")
            
        # Print details about a few specific models
        print("\nDetails for specific models:")
        models_to_show = ["anthropic/claude-3-sonnet", "deepseek/deepseek-chat-v3-0324:free", "google/gemini-2.0-flash-exp:free"]
        
        for model_id in models_to_show:
            model_data = next((m for m in models_data.get('data', []) if m.get('id') == model_id), None)
            if model_data:
                print(f"\n{model_id}:")
                print(f"  Name: {model_data.get('name')}")
                print(f"  Context: {model_data.get('context_length')}")
                print(f"  Input price: {model_data.get('pricing', {}).get('input', 'N/A')}")
                print(f"  Output price: {model_data.get('pricing', {}).get('output', 'N/A')}")
            else:
                print(f"\n{model_id}: Not found")
    else:
        print(f"Error getting models: {response.status_code} - {response.text}")

async def main():
    """Main test function"""
    try:
        # Test Claude model
        await test_claude_model()
        
        # Get model info
        await test_model_info()
        
        # Test with specific free model
        await test_specific_free_model()
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 