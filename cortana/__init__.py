"""
Cortana God-Tier AI Assistant
Modular, privacy-first personal AI with skills-based architecture
"""

__version__ = "1.0.0-modular"
__author__ = 'hakunaTgl'

# New modular architecture imports (lightweight)
from cortana.core.event_bus import EventBus, Event, EventPriority
from cortana.core.skills_manager import SkillsManager
from cortana.skills.base_skill import BaseSkill, SkillMetadata, SkillStatus, SkillCapability

# Original core imports are available but not auto-imported to avoid heavy dependencies
# To use them, import directly:
# from cortana.core.brain import CortanaBrain
# from cortana.core.memory_manager import MemoryManager

__all__ = [
    # New modular exports
    'EventBus',
    'Event',
    'EventPriority',
    'SkillsManager',
    'BaseSkill',
    'SkillMetadata',
    'SkillStatus',
    'SkillCapability',
]
