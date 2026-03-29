"""
Data Cache Module - Smart caching for MCP calls and historical data

Implements intelligent caching to reduce API calls and improve performance:
- Cache historical OHLCV data (24-hour TTL)
- Cache quotes and OHLC data (5-minute TTL)
- Cache sector performance (60-minute TTL)
- Batch MCP calls for efficiency
- Fallback to cached data if MCP unavailable
- Clear expired cache entries

This reduces token usage by avoiding repeated API calls for the same data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class DataCache:
    """Smart caching system for portfolio analysis data."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.default_ttl = {
            "historical": 86400,  # 24 hours
            "quotes": 300,  # 5 minutes
            "ohlc": 300,  # 5 minutes
            "sector": 3600,  # 1 hour
        }
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_file(self, key: str, cache_type: str = "default") -> str:
        """Get cache file path for key."""
        safe_key = key.replace("/", "_").replace(" ", "_")
        return os.path.join(self.cache_dir, f"{cache_type}_{safe_key}.json")
    
    def _is_cache_valid(self, cache_file: str, ttl: int) -> bool:
        """Check if cache file is still valid."""
        if not os.path.exists(cache_file):
            return False
        
        file_time = os.path.getmtime(cache_file)
        current_time = datetime.now().timestamp()
        return (current_time - file_time) < ttl
    
    def get_cache(self, key: str, cache_type: str = "default") -> Optional[Dict]:
        """
        Retrieve cached data if valid, else None.
        
        Args:
            key: Cache key
            cache_type: Type of cache (determines TTL)
        
        Returns:
            Cached data dict or None if expired/missing
        """
        ttl = self.default_ttl.get(cache_type, 3600)
        cache_file = self._get_cache_file(key, cache_type)
        
        if self._is_cache_valid(cache_file, ttl):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def set_cache(self, key: str, data: Dict, cache_type: str = "default") -> bool:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            cache_type: Type of cache
        
        Returns:
            True if successfully cached
        """
        cache_file = self._get_cache_file(key, cache_type)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            return True
        except:
            return False
    
    def get_historical_data_cached(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        interval: str = "day",
        mcp_callback=None
    ) -> Dict:
        """
        Get historical data from cache or MCP.
        
        Args:
            symbol: Stock symbol (e.g., 'INFY')
            from_date: From date (YYYY-MM-DD)
            to_date: To date (YYYY-MM-DD)
            interval: Candle interval (minute/day/etc)
            mcp_callback: Function to call MCP if cache miss
        
        Returns:
            Historical OHLCV data
        """
        cache_key = f"{symbol}_{from_date}_{to_date}_{interval}"
        
        # Check cache first
        cached = self.get_cache(cache_key, "historical")
        if cached:
            return cached
        
        # Cache miss - call MCP if callback provided
        if mcp_callback:
            data = mcp_callback(symbol, from_date, to_date, interval)
            if data:
                self.set_cache(cache_key, data, "historical")
                return data
        
        return {}
    
    def get_quotes_batch(
        self,
        symbols: List[str],
        mcp_callback=None
    ) -> Dict[str, Dict]:
        """
        Get quotes for multiple symbols, using cache when available.
        
        Args:
            symbols: List of symbols
            mcp_callback: MCP get_quotes function
        
        Returns:
            Dict of symbol -> quote data
        """
        cached_quotes = {}
        missing_symbols = []
        
        # Check cache first
        for symbol in symbols:
            cached = self.get_cache(symbol, "quotes")
            if cached:
                cached_quotes[symbol] = cached
            else:
                missing_symbols.append(symbol)
        
        # Batch fetch missing
        if missing_symbols and mcp_callback:
            new_quotes = mcp_callback(missing_symbols)
            for symbol, quote in new_quotes.items():
                self.set_cache(symbol, quote, "quotes")
                cached_quotes[symbol] = quote
        
        return cached_quotes
    
    def clear_expired_cache(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of files deleted
        """
        deleted = 0
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            
            # Determine cache type and TTL
            cache_type = filename.split('_')[0]
            ttl = self.default_ttl.get(cache_type, 3600)
            
            if self._is_cache_valid(file_path, ttl) is False:
                try:
                    os.remove(file_path)
                    deleted += 1
                except:
                    pass
        
        return deleted
    
    def clear_all_cache(self) -> int:
        """Clear all cache files. Use with caution!"""
        deleted = 0
        for filename in os.listdir(self.cache_dir):
            try:
                os.remove(os.path.join(self.cache_dir, filename))
                deleted += 1
            except:
                pass
        return deleted


# Placeholder for feature: cache stats
def get_cache_stats(cache_dir: str = ".cache") -> Dict[str, Any]:
    """Get cache utilization statistics."""
    if not os.path.exists(cache_dir):
        return {"total_files": 0, "total_size_mb": 0}
    
    files = os.listdir(cache_dir)
    total_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in files)
    
    return {
        "total_files": len(files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "files": files,
    }
