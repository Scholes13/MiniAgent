"""
Patch untuk twikit library
"""
import sys
import os
import inspect
import importlib.util
from types import ModuleType

def patch_twikit_client():
    """
    Patch twikit Client class untuk mengatasi masalah proxy.
    Ini adalah solusi sementara sampai masalah diperbaiki di twikit.
    """
    try:
        # Import twikit
        import twikit
        from twikit.client import client
        
        # Lokasi file Client
        client_file = inspect.getfile(client)
        print(f"Twikit client file: {client_file}")
        
        # Get the original AsyncClient
        from httpx import AsyncClient as OriginalAsyncClient
        
        # Create a patched version of AsyncClient that ignores 'proxy' keyword
        class PatchedAsyncClient(OriginalAsyncClient):
            def __init__(self, *args, **kwargs):
                # Remove 'proxy' from kwargs if present
                if 'proxy' in kwargs:
                    del kwargs['proxy']
                super().__init__(*args, **kwargs)
        
        # Apply the patch to httpx
        import httpx
        httpx.AsyncClient = PatchedAsyncClient
        
        print("httpx.AsyncClient patched successfully")
        return True
        
    except Exception as e:
        print(f"Failed to patch twikit: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test the patch
    if patch_twikit_client():
        try:
            from twikit import Client
            client = Client()
            print("Successfully created patched Client")
        except Exception as e:
            print(f"Error creating Client: {e}")
    else:
        print("Patch failed, cannot test Client") 