"""
Cache manager for storing analysis results to reduce API usage
"""
import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Cache configuration
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
CACHE_EXPIRY = 60 * 60 * 24 * 7  # 7 days in seconds

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)


class AnalysisCache:
    """
    Cache manager for storing and retrieving analysis results
    
    This class provides functionality to cache analysis results to avoid
    repeated API calls and save API credits when analyzing the same project
    multiple times within the expiry period.
    """
    
    @staticmethod
    def _generate_cache_key(project_data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key based on project data
        
        Args:
            project_data: Dictionary containing project information
            
        Returns:
            A unique hash string to use as cache key
        """
        # Extract key identifying information
        key_parts = [
            project_data.get('project_name', ''),
            project_data.get('token_symbol', ''),
            # Include additional identifiers if available
            project_data.get('website_url', ''),
            project_data.get('twitter_handle', '')
        ]
        
        # Create a stable string representation and hash it
        identifier = '_'.join([str(part).lower().strip() for part in key_parts if part])
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _get_cache_path(cache_key: str) -> str:
        """
        Get the full file path for a cache key
        
        Args:
            cache_key: The unique cache key
            
        Returns:
            Full path to the cache file
        """
        return os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    @classmethod
    def get_cached_analysis(cls, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis results for a project if available and not expired
        
        Args:
            project_data: Project information dictionary
            
        Returns:
            Cached analysis results or None if not available
        """
        cache_key = cls._generate_cache_key(project_data)
        cache_path = cls._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            # Check if cache has expired
            cached_time = cached_data.get('cached_at', 0)
            if time.time() - cached_time > CACHE_EXPIRY:
                print(f"Cache expired for {project_data.get('project_name')}")
                return None
                
            print(f"Using cached analysis for {project_data.get('project_name')}")
            return cached_data.get('analysis')
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading cache: {e}")
            return None
    
    @classmethod
    def cache_analysis(cls, project_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> bool:
        """
        Store analysis results in cache
        
        Args:
            project_data: Project information dictionary
            analysis_result: Analysis results to cache
            
        Returns:
            True if caching was successful, False otherwise
        """
        cache_key = cls._generate_cache_key(project_data)
        cache_path = cls._get_cache_path(cache_key)
        
        try:
            # Prepare cache entry with metadata
            cache_entry = {
                'cached_at': time.time(),
                'expires_at': time.time() + CACHE_EXPIRY,
                'project_name': project_data.get('project_name', 'Unknown'),
                'token_symbol': project_data.get('token_symbol', 'Unknown'),
                'analysis': analysis_result
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2)
                
            print(f"Cached analysis for {project_data.get('project_name')}")
            return True
                
        except IOError as e:
            print(f"Error writing to cache: {e}")
            return False
    
    @classmethod
    def clear_expired_cache(cls) -> int:
        """
        Clear expired cache entries
        
        Returns:
            Number of cache entries cleared
        """
        cleared_count = 0
        current_time = time.time()
        
        for filename in os.listdir(CACHE_DIR):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(CACHE_DIR, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Check if cache has expired
                cached_time = cache_data.get('cached_at', 0)
                if current_time - cached_time > CACHE_EXPIRY:
                    os.remove(file_path)
                    cleared_count += 1
                    
            except (json.JSONDecodeError, IOError):
                # Remove invalid cache files
                try:
                    os.remove(file_path)
                    cleared_count += 1
                except:
                    pass
                    
        return cleared_count
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get statistics about the cache
        
        Returns:
            Dictionary with cache statistics
        """
        total_files = 0
        total_size = 0
        expired_count = 0
        current_time = time.time()
        projects = []
        
        for filename in os.listdir(CACHE_DIR):
            if not filename.endswith('.json'):
                continue
                
            total_files += 1
            file_path = os.path.join(CACHE_DIR, filename)
            total_size += os.path.getsize(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Check if cache has expired
                cached_time = cache_data.get('cached_at', 0)
                expires_at = cache_data.get('expires_at', 0)
                is_expired = current_time - cached_time > CACHE_EXPIRY
                
                if is_expired:
                    expired_count += 1
                
                # Record project info
                projects.append({
                    'project_name': cache_data.get('project_name', 'Unknown'),
                    'token_symbol': cache_data.get('token_symbol', 'Unknown'),
                    'cached_at': datetime.fromtimestamp(cached_time).isoformat(),
                    'expires_at': datetime.fromtimestamp(expires_at).isoformat(),
                    'is_expired': is_expired
                })
                    
            except (json.JSONDecodeError, IOError):
                expired_count += 1
                
        return {
            'total_cached': total_files,
            'active_cache_entries': total_files - expired_count,
            'expired_entries': expired_count,
            'total_size_bytes': total_size,
            'projects': projects
        } 