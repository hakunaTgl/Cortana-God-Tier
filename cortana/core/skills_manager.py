#!/usr/bin/env python3
"""
Skills Manager for Cortana-God-Tier
Manages skill lifecycle, registration, and orchestration
"""

import asyncio
from typing import Dict, List, Optional, Type, Any
import logging
import yaml

from cortana.core.event_bus import EventBus, EventPriority
from cortana.skills.base_skill import BaseSkill, SkillStatus, SkillCapability
from cortana.skills.research_skill import ResearchSkill
from cortana.skills.code_skill import CodeSkill
from cortana.skills.memory_skill import MemorySkill
from cortana.skills.system_skill import SystemSkill

logger = logging.getLogger(__name__)


class SkillsManager:
    """
    Skills Manager - Orchestrates all Cortana skills
    
    Features:
    - Skill registration and initialization
    - Hot-reloading of skills
    - Skill lifecycle management
    - Capability-based routing
    - Health monitoring
    """
    
    # Registry of available skill classes
    SKILL_REGISTRY: Dict[str, Type[BaseSkill]] = {
        'research': ResearchSkill,
        'code': CodeSkill,
        'memory': MemorySkill,
        'system': SystemSkill,
    }
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the skills manager
        
        Args:
            event_bus: EventBus instance
            config: Configuration dictionary
        """
        self.event_bus = event_bus
        self.config = config or {}
        self.skills: Dict[str, BaseSkill] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enabled_skills = self.config.get('enabled', list(self.SKILL_REGISTRY.keys()))
        self.experimental_skills = self.config.get('experimental', [])
        
        self.logger.info("SkillsManager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize all enabled skills
        
        Returns:
            True if all skills initialized successfully
        """
        try:
            self.logger.info("Initializing skills...")
            
            # Initialize enabled skills
            initialization_results = []
            for skill_name in self.enabled_skills:
                if skill_name not in self.SKILL_REGISTRY:
                    self.logger.warning(f"Unknown skill: {skill_name}")
                    continue
                
                result = await self._initialize_skill(skill_name)
                initialization_results.append(result)
            
            success_count = sum(initialization_results)
            total_count = len(initialization_results)
            
            self.logger.info(f"Initialized {success_count}/{total_count} skills")
            
            # Publish initialization complete event
            await self.event_bus.publish(
                event_name="skills.initialized",
                data={
                    'success_count': success_count,
                    'total_count': total_count,
                    'skills': list(self.skills.keys())
                },
                source="SkillsManager",
                priority=EventPriority.HIGH
            )
            
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Error initializing skills: {e}")
            return False
    
    async def _initialize_skill(self, skill_name: str) -> bool:
        """
        Initialize a single skill
        
        Args:
            skill_name: Name of the skill to initialize
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Initializing skill: {skill_name}")
            
            # Get skill class
            skill_class = self.SKILL_REGISTRY[skill_name]
            
            # Get skill-specific config
            skill_config = self.config.get(skill_name, {})
            
            # Create skill instance
            skill = skill_class(self.event_bus, skill_config)
            
            # Initialize skill
            success = await skill.initialize()
            
            if success:
                self.skills[skill_name] = skill
                self.logger.info(f"Skill '{skill_name}' initialized successfully")
                return True
            else:
                self.logger.error(f"Failed to initialize skill: {skill_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing skill '{skill_name}': {e}")
            return False
    
    async def execute_skill(
        self,
        skill_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific skill
        
        Args:
            skill_name: Name of the skill
            task: Task to execute
            context: Optional context
            
        Returns:
            Execution result
        """
        if skill_name not in self.skills:
            return {
                'success': False,
                'result': None,
                'error': f"Skill '{skill_name}' not found or not initialized"
            }
        
        skill = self.skills[skill_name]
        
        if not skill.is_ready():
            return {
                'success': False,
                'result': None,
                'error': f"Skill '{skill_name}' not ready (status: {skill.status.value})"
            }
        
        return await skill._safe_execute(task, context)
    
    async def execute_by_capability(
        self,
        capability: SkillCapability,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute task using skills with specific capability
        
        Args:
            capability: Required capability
            task: Task to execute
            context: Optional context
            
        Returns:
            List of results from all capable skills
        """
        results = []
        
        for skill_name, skill in self.skills.items():
            if capability in skill.get_capabilities() and skill.is_ready():
                self.logger.info(f"Executing task with skill '{skill_name}'")
                result = await skill._safe_execute(task, context)
                results.append({
                    'skill': skill_name,
                    'result': result
                })
        
        if not results:
            self.logger.warning(f"No skills found with capability: {capability.value}")
        
        return results
    
    async def reload_skill(self, skill_name: str) -> bool:
        """
        Reload a skill (hot-reload)
        
        Args:
            skill_name: Name of the skill to reload
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Reloading skill: {skill_name}")
            
            # Cleanup existing skill
            if skill_name in self.skills:
                await self.skills[skill_name].cleanup()
                del self.skills[skill_name]
            
            # Reinitialize
            return await self._initialize_skill(skill_name)
            
        except Exception as e:
            self.logger.error(f"Error reloading skill '{skill_name}': {e}")
            return False
    
    async def add_skill(self, skill_name: str, skill_class: Type[BaseSkill]) -> bool:
        """
        Register and initialize a new skill at runtime
        
        Args:
            skill_name: Name for the skill
            skill_class: Skill class
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Adding new skill: {skill_name}")
            
            # Add to registry
            self.SKILL_REGISTRY[skill_name] = skill_class
            
            # Initialize
            return await self._initialize_skill(skill_name)
            
        except Exception as e:
            self.logger.error(f"Error adding skill '{skill_name}': {e}")
            return False
    
    async def remove_skill(self, skill_name: str) -> bool:
        """
        Remove and cleanup a skill
        
        Args:
            skill_name: Name of the skill to remove
            
        Returns:
            True if successful
        """
        try:
            if skill_name not in self.skills:
                self.logger.warning(f"Skill '{skill_name}' not found")
                return False
            
            self.logger.info(f"Removing skill: {skill_name}")
            
            # Cleanup
            await self.skills[skill_name].cleanup()
            
            # Remove
            del self.skills[skill_name]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing skill '{skill_name}': {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all skills
        
        Returns:
            Health status dictionary
        """
        health_status = {}
        
        for skill_name, skill in self.skills.items():
            is_healthy = await skill.health_check()
            health_status[skill_name] = {
                'healthy': is_healthy,
                'status': skill.status.value,
                'stats': skill.get_stats()
            }
        
        return health_status
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        Get a skill instance
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill instance or None
        """
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        List all registered skills
        
        Returns:
            List of skill information
        """
        return [
            {
                'name': skill.metadata.name,
                'version': skill.metadata.version,
                'description': skill.metadata.description,
                'status': skill.status.value,
                'capabilities': [cap.value for cap in skill.get_capabilities()],
                'experimental': skill.metadata.experimental
            }
            for skill in self.skills.values()
        ]
    
    def get_skills_by_capability(self, capability: SkillCapability) -> List[str]:
        """
        Get skill names that provide a specific capability
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of skill names
        """
        return [
            skill_name
            for skill_name, skill in self.skills.items()
            if capability in skill.get_capabilities()
        ]
    
    async def cleanup(self) -> bool:
        """
        Cleanup all skills
        
        Returns:
            True if successful
        """
        try:
            self.logger.info("Cleaning up all skills...")
            
            cleanup_results = []
            for skill_name, skill in self.skills.items():
                self.logger.info(f"Cleaning up skill: {skill_name}")
                result = await skill.cleanup()
                cleanup_results.append(result)
            
            self.skills.clear()
            
            success = all(cleanup_results)
            self.logger.info(f"Skills cleanup complete (success={success})")
            return success
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_skills': len(self.skills),
            'enabled_skills': self.enabled_skills,
            'experimental_skills': self.experimental_skills,
            'skills': {
                skill_name: skill.get_stats()
                for skill_name, skill in self.skills.items()
            }
        }
