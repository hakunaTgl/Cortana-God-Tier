"""Configuration loader for Cortana"""
import yaml
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return get_default_config()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
    
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        'cortana': {
            'name': 'Cortana',
            'version': '1.0.0',
            'log_level': 'INFO'
        },
        'memory': {
            'max_memory_mb': 512,
            'cache_enabled': True
        },
        'models': {
            'default_model': 'gpt2',
            'quantization': 'int8'
        },
        'api': {
            'host': '0.0.0.0',
            'port': 8000,
            'debug': False
        }
    }

def save_config(config: Dict[str, Any], config_path: str = "config.yaml") -> bool:
    """Save configuration to YAML file"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False
