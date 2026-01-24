"""Memory Manager - Efficient RAM Management"""
import psutil
import gc
import logging
from typing import Dict, Any, List
from collections import deque
import sys

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages memory efficiently for Cortana"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.cache = {}
        self.access_history = deque(maxlen=1000)
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        logger.info(f"MemoryManager initialized with {max_memory_mb}MB limit")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        before = self.get_memory_usage()
        
        # Clear unused cache entries
        self._evict_old_entries()
        
        # Force garbage collection
        collected = gc.collect()
        
        after = self.get_memory_usage()
        freed_mb = before['rss_mb'] - after['rss_mb']
        
        logger.info(f"Memory optimized: freed {freed_mb:.2f}MB")
        return {
            'before': before,
            'after': after,
            'freed_mb': freed_mb,
            'objects_collected': collected
        }
    
    def cache_data(self, key: str, data: Any) -> None:
        """Cache data with memory limit check"""
        current_usage = self.get_memory_usage()['rss_mb']
        
        if current_usage > self.max_memory_mb * 0.9:
            self.optimize_memory()
        
        self.cache[key] = data
        self.access_history.append(key)
    
    def get_cached_data(self, key: str) -> Any:
        """Retrieve cached data"""
        if key in self.cache:
            self.stats['hits'] += 1
            self.access_history.append(key)
            return self.cache[key]
        self.stats['misses'] += 1
        return None
    
    def _evict_old_entries(self) -> None:
        """Evict least recently used cache entries"""
        if len(self.cache) < 10:
            return
        
        # Keep only recently accessed items
        recent_keys = set(list(self.access_history)[-100:])
        to_remove = [k for k in self.cache.keys() if k not in recent_keys]
        
        for key in to_remove:
            del self.cache[key]
            self.stats['evictions'] += 1
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.access_history.clear()
        gc.collect()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics"""
        return {
            'memory_usage': self.get_memory_usage(),
            'cache_size': len(self.cache),
            'cache_stats': self.stats,
            'max_memory_mb': self.max_memory_mb
        }
