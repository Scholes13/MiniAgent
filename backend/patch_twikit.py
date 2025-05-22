"""
Monkey patch twikit library untuk mengatasi masalah proxy parameter
"""
import sys
import os
import inspect

def patch_twikit():
    """Apply monkey patch to twikit's AsyncClient initialization"""
    # Original import 
    import httpx
    
    # Get original AsyncClient.__init__
    original_init = httpx.AsyncClient.__init__
    
    # Create patched version
    def patched_init(self, *args, **kwargs):
        # Remove 'proxy' parameter if present
        if 'proxy' in kwargs:
            del kwargs['proxy']
        # Call original init 
        original_init(self, *args, **kwargs)
    
    # Apply patch
    httpx.AsyncClient.__init__ = patched_init
    
    print("[INFO] Successfully applied patch to httpx.AsyncClient")
    return True

if __name__ == "__main__":
    patch_twikit() 