"""Input validation utilities for Cortana"""
import re
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

def validate_input(text: str, max_length: int = 10000) -> bool:
    """Validate user input"""
    if not text or not isinstance(text, str):
        logger.warning("Invalid input: empty or not a string")
        return False
    
    if len(text) > max_length:
        logger.warning(f"Input too long: {len(text)} > {max_length}")
        return False
    
    # Check for potential injection attacks
    dangerous_patterns = [
        r'<script', r'javascript:', r'onerror=',
        r'onclick=', r'eval\(', r'exec\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potentially dangerous input detected: {pattern}")
            return False
    
    return True

def sanitize_input(text: str) -> str:
    """Sanitize user input by removing dangerous characters"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove special characters that could be used for injection
    text = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text

def validate_config(config: dict) -> bool:
    """Validate configuration dictionary"""
    required_keys = ['cortana', 'memory', 'models']
    
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required config key: {key}")
            return False
    
    return True

def validate_model_name(model_name: str) -> bool:
    """Validate model name format"""
    # Allow alphanumeric, dashes, underscores, and forward slashes
    pattern = r'^[a-zA-Z0-9/_-]+$'
    
    if not re.match(pattern, model_name):
        logger.warning(f"Invalid model name format: {model_name}")
        return False
    
    return True
