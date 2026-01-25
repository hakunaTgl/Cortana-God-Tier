#!/usr/bin/env python3
"""
Performance Anomaly Detection Script
Detect performance anomalies in the system
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

def detect_cpu_anomalies():
    """Detect CPU usage anomalies"""
    cpu_percent = psutil.cpu_percent(interval=1)
    logger.info(f"Current CPU usage: {cpu_percent:.1f}%")
    
    if cpu_percent > 80:
        logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
    else:
        logger.info("CPU usage is normal")

def detect_memory_anomalies():
    """Detect memory usage anomalies"""
    memory = psutil.virtual_memory()
    logger.info(f"Memory usage: {memory.percent:.1f}% ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)")
    
    if memory.percent > 80:
        logger.warning(f"High memory usage detected: {memory.percent:.1f}%")
    else:
        logger.info("Memory usage is normal")

def detect_disk_anomalies():
    """Detect disk usage anomalies"""
    disk = psutil.disk_usage('/')
    logger.info(f"Disk usage: {disk.percent:.1f}% ({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)")
    
    if disk.percent > 90:
        logger.warning(f"High disk usage detected: {disk.percent:.1f}%")
    else:
        logger.info("Disk usage is normal")

def main():
    """Main function to detect performance anomalies"""
    try:
        logger.info("Starting performance anomaly detection...")
        
        # Check system resources
        detect_cpu_anomalies()
        detect_memory_anomalies()
        detect_disk_anomalies()
        
        logger.info("Performance anomaly detection completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during anomaly detection: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
