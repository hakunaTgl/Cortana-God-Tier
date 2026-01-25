#!/usr/bin/env python3
"""
Memory Usage Analysis Script
Analyze memory usage of the system and applications
"""

import sys
import logging
import psutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_system_memory():
    """Analyze system memory usage"""
    memory = psutil.virtual_memory()
    
    logger.info("=== System Memory Analysis ===")
    logger.info(f"Total Memory: {memory.total / (1024**3):.2f} GB")
    logger.info(f"Available Memory: {memory.available / (1024**3):.2f} GB")
    logger.info(f"Used Memory: {memory.used / (1024**3):.2f} GB")
    logger.info(f"Memory Usage: {memory.percent:.1f}%")
    logger.info(f"Free Memory: {memory.free / (1024**3):.2f} GB")

def analyze_swap_memory():
    """Analyze swap memory usage"""
    swap = psutil.swap_memory()
    
    logger.info("=== Swap Memory Analysis ===")
    logger.info(f"Total Swap: {swap.total / (1024**3):.2f} GB")
    logger.info(f"Used Swap: {swap.used / (1024**3):.2f} GB")
    logger.info(f"Free Swap: {swap.free / (1024**3):.2f} GB")
    logger.info(f"Swap Usage: {swap.percent:.1f}%")

def get_top_memory_processes(limit: int = 5):
    """Get top memory-consuming processes"""
    logger.info(f"=== Top {limit} Memory-Consuming Processes ===")
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by memory usage
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    
    for i, proc in enumerate(processes[:limit], 1):
        logger.info(f"{i}. {proc['name']} (PID: {proc['pid']}): {proc['memory_percent']:.2f}%")

def main():
    """Main function to analyze memory usage"""
    try:
        logger.info("Starting memory usage analysis...")
        
        # Analyze memory
        analyze_system_memory()
        analyze_swap_memory()
        get_top_memory_processes()
        
        logger.info("Memory usage analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during memory analysis: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
