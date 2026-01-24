#!/usr/bin/env python3
"""
Memory Manager for Cortana-God-Tier
Optimizes RAM usage and manages system memory efficiently
"""

import gc
import os
import sys
import psutil
import yaml
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize Memory Manager with configuration"""
        self.config = self.load_config(config_path)
        self.memory_config = self.config.get('memory', {})
        self.max_memory_mb = self.memory_config.get('max_memory_mb', 512)
        self.cache_size_mb = self.memory_config.get('cache_size_mb', 128)
        self.auto_cleanup = self.memory_config.get('auto_cleanup', True)
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            return {}
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        return {
            'rss_mb': mem_info.rss / (1024 * 1024),
            'vms_mb': mem_info.vms / (1024 * 1024),
            'percent': process.memory_percent()
        }
    
    def optimize_memory(self) -> bool:
        """Optimize memory usage by cleaning up unused objects"""
        if not self.auto_cleanup:
            return False
            
        before = self.get_memory_usage()
        
        # Force garbage collection
        gc.collect()
        
        after = self.get_memory_usage()
        freed_mb = before['rss_mb'] - after['rss_mb']
        
        logger.info(f"Memory optimization freed {freed_mb:.2f} MB")
        return True
    
    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold"""
        usage = self.get_memory_usage()
        return usage['rss_mb'] > self.max_memory_mb
    
    def force_cleanup(self):
        """Force aggressive memory cleanup"""
        gc.collect(2)  # Full collection
        logger.info("Forced memory cleanup completed")

if __name__ == "__main__":
    manager = MemoryManager()
    usage = manager.get_memory_usage()
    print(f"Current memory usage: {usage['rss_mb']:.2f} MB ({usage['percent']:.2f}%)")
    manager.optimize_memory()
