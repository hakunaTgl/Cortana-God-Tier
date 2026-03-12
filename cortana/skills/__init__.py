"""
Cortana Skills System
Modular, hot-swappable skill architecture for extensibility
"""

from .base_skill import BaseSkill, SkillMetadata, SkillStatus, SkillCapability

__all__ = [
    'BaseSkill',
    'SkillMetadata',
    'SkillStatus',
    'SkillCapability'
]
