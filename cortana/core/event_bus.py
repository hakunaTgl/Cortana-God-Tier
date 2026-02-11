#!/usr/bin/env python3
"""
Event Bus System for Cortana-God-Tier
Provides async publish/subscribe mechanism for loose coupling between skills
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """
    Event data structure for the event bus
    
    Attributes:
        name: Event name/type
        data: Event payload data
        source: Source skill/component that emitted the event
        priority: Event priority level
        timestamp: Event creation timestamp
        metadata: Additional metadata
    """
    name: str
    data: Any
    source: str
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """
    Async Event Bus for decoupled skill communication
    
    Features:
    - Async publish/subscribe pattern
    - Priority-based event handling
    - Event filtering and routing
    - Runtime skill registration
    - Queue management with size limits
    """
    
    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize the event bus
        
        Args:
            max_queue_size: Maximum number of events in the queue
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._event_history: List[Event] = []
        self._max_history_size = 100
        self.max_queue_size = max_queue_size
        logger.info(f"EventBus initialized with max_queue_size={max_queue_size}")
    
    async def start(self):
        """Start the event bus worker"""
        if self._running:
            logger.warning("EventBus already running")
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")
    
    async def stop(self):
        """Stop the event bus worker"""
        if not self._running:
            return
        
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        logger.info("EventBus stopped")
    
    def subscribe(self, event_name: str, handler: Callable) -> None:
        """
        Subscribe to an event
        
        Args:
            event_name: Name of the event to subscribe to
            handler: Async callback function to handle the event
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)
            logger.debug(f"Subscribed {handler.__name__} to event '{event_name}'")
    
    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """
        Unsubscribe from an event
        
        Args:
            event_name: Name of the event to unsubscribe from
            handler: Handler to remove
        """
        if event_name in self._subscribers:
            if handler in self._subscribers[event_name]:
                self._subscribers[event_name].remove(handler)
                logger.debug(f"Unsubscribed {handler.__name__} from event '{event_name}'")
    
    async def publish(
        self,
        event_name: str,
        data: Any,
        source: str,
        priority: EventPriority = EventPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publish an event to the bus
        
        Args:
            event_name: Name of the event
            data: Event payload
            source: Source skill/component
            priority: Event priority level
            metadata: Additional metadata
        """
        event = Event(
            name=event_name,
            data=data,
            source=source,
            priority=priority,
            metadata=metadata or {}
        )
        
        try:
            await self._event_queue.put(event)
            logger.debug(f"Published event '{event_name}' from {source}")
        except asyncio.QueueFull:
            logger.error(f"Event queue full, dropping event '{event_name}'")
    
    async def _process_events(self):
        """Process events from the queue"""
        logger.info("Event processing worker started")
        
        while self._running:
            try:
                # Wait for event with timeout to allow clean shutdown
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                
                # Store in history
                self._add_to_history(event)
                
                # Get subscribers for this event
                handlers = self._subscribers.get(event.name, [])
                
                if not handlers:
                    logger.debug(f"No subscribers for event '{event.name}'")
                    continue
                
                # Call all handlers concurrently
                tasks = []
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            tasks.append(handler(event))
                        else:
                            # Wrap sync function in async
                            tasks.append(asyncio.to_thread(handler, event))
                    except Exception as e:
                        logger.error(f"Error preparing handler {handler.__name__}: {e}")
                
                # Wait for all handlers to complete
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, Exception):
                            logger.error(f"Handler error: {result}")
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
        
        logger.info("Event processing worker stopped")
    
    def _add_to_history(self, event: Event):
        """Add event to history with size limit"""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
    
    def get_history(self, event_name: Optional[str] = None) -> List[Event]:
        """
        Get event history
        
        Args:
            event_name: Filter by event name, or None for all events
            
        Returns:
            List of events
        """
        if event_name:
            return [e for e in self._event_history if e.name == event_name]
        return self._event_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics
        
        Returns:
            Dictionary of stats
        """
        return {
            'running': self._running,
            'queue_size': self._event_queue.qsize(),
            'max_queue_size': self.max_queue_size,
            'subscribers': {
                event: len(handlers) 
                for event, handlers in self._subscribers.items()
            },
            'history_size': len(self._event_history)
        }
