#!/usr/bin/env python3
"""
Base Skill Abstract Class for Cortana-God-Tier
Defines the standard interface for all skills
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio

from cortana.core.event_bus import EventBus, Event, EventPriority

logger = logging.getLogger(__name__)


class SkillStatus(Enum):
    """Skill lifecycle status"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


class SkillCapability(Enum):
    """Standard skill capabilities"""
    RESEARCH = "research"          # Web search, information gathering
    CODE = "code"                  # Code execution, file operations
    MEMORY = "memory"              # Context and memory management
    SYSTEM = "system"              # OS-level operations
    COMMUNICATION = "communication" # External communication
    ANALYSIS = "analysis"          # Data analysis and processing


@dataclass
class SkillMetadata:
    """
    Metadata for skill versioning and requirements
    
    Attributes:
        name: Skill name
        version: Skill version (semver)
        description: Skill description
        author: Skill author
        capabilities: List of capabilities provided
        dependencies: Required Python packages
        requires_skills: Other skills this skill depends on
        experimental: Whether this is an experimental skill
        privacy_level: Privacy level (local, cloud, mixed)
    """
    name: str
    version: str
    description: str
    author: str = "Cortana-God-Tier"
    capabilities: List[SkillCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    requires_skills: List[str] = field(default_factory=list)
    experimental: bool = False
    privacy_level: str = "local"
    created_at: datetime = field(default_factory=datetime.now)


class BaseSkill(ABC):
    """
    Abstract base class for all Cortana skills
    
    All skills must implement:
    - initialize(): Setup the skill
    - execute(): Main skill execution logic
    - cleanup(): Cleanup resources
    - get_capabilities(): Return skill capabilities
    """
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base skill
        
        Args:
            event_bus: EventBus instance for communication
            config: Optional configuration dictionary
        """
        self.event_bus = event_bus
        self.config = config or {}
        self.status = SkillStatus.UNINITIALIZED
        self.metadata = self._create_metadata()
        self.logger = logging.getLogger(f"{__name__}.{self.metadata.name}")
        self._subscribed_events: Set[str] = set()
        self._execution_count = 0
        self._error_count = 0
        self._last_execution: Optional[datetime] = None
        
        self.logger.info(f"Skill '{self.metadata.name}' v{self.metadata.version} created")
    
    @abstractmethod
    def _create_metadata(self) -> SkillMetadata:
        """
        Create skill metadata
        
        Returns:
            SkillMetadata instance
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the skill
        
        This method should:
        - Set up required resources
        - Register event handlers
        - Validate dependencies
        - Set status to READY on success
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the skill's main functionality
        
        Args:
            task: Task description or command
            context: Optional context data
            
        Returns:
            Dictionary with execution results:
            {
                'success': bool,
                'result': Any,
                'error': Optional[str],
                'metadata': Dict[str, Any]
            }
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """
        Cleanup skill resources
        
        This method should:
        - Release resources
        - Unsubscribe from events
        - Save state if needed
        
        Returns:
            True if cleanup successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[SkillCapability]:
        """
        Get list of capabilities this skill provides
        
        Returns:
            List of SkillCapability enums
        """
        pass
    
    async def _safe_execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Safely execute the skill with error handling and metrics
        
        Args:
            task: Task to execute
            context: Execution context
            
        Returns:
            Execution result dictionary
        """
        try:
            self.status = SkillStatus.BUSY
            self._execution_count += 1
            self._last_execution = datetime.now()
            
            start_time = datetime.now()
            result = await self.execute(task, context)
            duration = (datetime.now() - start_time).total_seconds()
            
            # Add execution metadata
            if 'metadata' not in result:
                result['metadata'] = {}
            result['metadata']['duration'] = duration
            result['metadata']['skill'] = self.metadata.name
            result['metadata']['timestamp'] = datetime.now().isoformat()
            
            self.status = SkillStatus.READY
            
            # Publish completion event
            await self.event_bus.publish(
                event_name=f"skill.{self.metadata.name}.completed",
                data=result,
                source=self.metadata.name,
                priority=EventPriority.NORMAL
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            self.status = SkillStatus.ERROR
            self.logger.error(f"Error executing skill: {e}", exc_info=True)
            
            error_result = {
                'success': False,
                'result': None,
                'error': str(e),
                'metadata': {
                    'skill': self.metadata.name,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Publish error event
            await self.event_bus.publish(
                event_name=f"skill.{self.metadata.name}.error",
                data=error_result,
                source=self.metadata.name,
                priority=EventPriority.HIGH
            )
            
            return error_result
    
    def subscribe_to_event(self, event_name: str, handler):
        """
        Subscribe to an event on the event bus
        
        Args:
            event_name: Event to subscribe to
            handler: Handler function
        """
        self.event_bus.subscribe(event_name, handler)
        self._subscribed_events.add(event_name)
        self.logger.debug(f"Subscribed to event: {event_name}")
    
    def unsubscribe_from_event(self, event_name: str, handler):
        """
        Unsubscribe from an event
        
        Args:
            event_name: Event to unsubscribe from
            handler: Handler function
        """
        self.event_bus.unsubscribe(event_name, handler)
        self._subscribed_events.discard(event_name)
        self.logger.debug(f"Unsubscribed from event: {event_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get skill statistics
        
        Returns:
            Dictionary of statistics
        """
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'status': self.status.value,
            'execution_count': self._execution_count,
            'error_count': self._error_count,
            'last_execution': self._last_execution.isoformat() if self._last_execution else None,
            'subscribed_events': list(self._subscribed_events),
            'capabilities': [cap.value for cap in self.get_capabilities()]
        }
    
    def is_ready(self) -> bool:
        """Check if skill is ready to execute"""
        return self.status == SkillStatus.READY
    
    async def health_check(self) -> bool:
        """
        Perform health check on the skill
        
        Returns:
            True if healthy, False otherwise
        """
        return self.status in [SkillStatus.READY, SkillStatus.BUSY]
