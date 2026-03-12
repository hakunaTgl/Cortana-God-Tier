#!/usr/bin/env python3
"""
Memory Skill for Cortana-God-Tier
Handles context management, conversation history, and memory storage
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

from cortana.skills.base_skill import (
    BaseSkill, SkillMetadata, SkillStatus, SkillCapability
)
from cortana.core.event_bus import EventBus, EventPriority

logger = logging.getLogger(__name__)


class MemorySkill(BaseSkill):
    """
    Memory Skill - Context and memory management
    
    Capabilities:
    - Short-term memory (conversation context)
    - Long-term memory (persistent storage)
    - Context retrieval and search
    - Memory optimization
    - Privacy-preserving storage
    """
    
    def _create_metadata(self) -> SkillMetadata:
        """Create skill metadata"""
        return SkillMetadata(
            name="memory",
            version="1.0.0",
            description="Context management and memory storage",
            capabilities=[SkillCapability.MEMORY],
            dependencies=["psutil"],
            privacy_level="local",  # All memory stays local
            experimental=False
        )
    
    async def initialize(self) -> bool:
        """Initialize the memory skill"""
        try:
            self.logger.info("Initializing MemorySkill...")
            
            # Short-term memory (current session)
            self._short_term_memory: List[Dict[str, Any]] = []
            self._max_short_term = self.config.get('max_short_term_memory', 50)
            
            # Long-term memory (persistent)
            self._long_term_memory: Dict[str, Any] = {}
            self._memory_file = self.config.get('memory_file', 'memory_store.json')
            
            # Context window
            self._context_window = self.config.get('context_window', 10)
            
            # Load long-term memory
            await self._load_long_term_memory()
            
            # Subscribe to memory-related events
            self.subscribe_to_event("memory.store", self._handle_store_event)
            self.subscribe_to_event("memory.retrieve", self._handle_retrieve_event)
            self.subscribe_to_event("memory.clear", self._handle_clear_event)
            
            self.status = SkillStatus.READY
            self.logger.info("MemorySkill initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MemorySkill: {e}")
            self.status = SkillStatus.ERROR
            return False
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute memory task
        
        Args:
            task: Memory operation (store, retrieve, search, etc.)
            context: Optional context with operation parameters
            
        Returns:
            Operation results dictionary
        """
        context = context or {}
        operation = context.get('operation', 'store')
        
        try:
            if operation == 'store':
                result = await self._store_memory(task, context)
            elif operation == 'retrieve':
                result = await self._retrieve_memory(context.get('key', task))
            elif operation == 'search':
                result = await self._search_memory(task)
            elif operation == 'get_context':
                result = await self._get_context()
            elif operation == 'optimize':
                result = await self._optimize_memory()
            else:
                result = {
                    'success': False,
                    'data': None,
                    'error': f'Unknown operation: {operation}'
                }
            
            return {
                'success': result.get('success', False),
                'result': result,
            }
            
        except Exception as e:
            self.logger.error(f"Memory operation error: {e}")
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    async def _store_memory(self, data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store data in memory
        
        Args:
            data: Data to store
            context: Storage context (type, tags, etc.)
            
        Returns:
            Storage result
        """
        try:
            memory_entry = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'type': context.get('type', 'general'),
                'tags': context.get('tags', []),
                'metadata': context.get('metadata', {})
            }
            
            # Add to short-term memory
            self._short_term_memory.append(memory_entry)
            
            # Manage short-term memory size
            if len(self._short_term_memory) > self._max_short_term:
                # Move oldest to long-term if important
                oldest = self._short_term_memory.pop(0)
                if oldest.get('important', False):
                    key = f"memory_{datetime.now().timestamp()}"
                    self._long_term_memory[key] = oldest
            
            # Store in long-term if marked as persistent
            if context.get('persistent', False):
                key = context.get('key', f"memory_{datetime.now().timestamp()}")
                self._long_term_memory[key] = memory_entry
                await self._save_long_term_memory()
            
            return {
                'success': True,
                'stored': True,
                'entry_id': len(self._short_term_memory) - 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'stored': False,
                'error': str(e)
            }
    
    async def _retrieve_memory(self, key: str) -> Dict[str, Any]:
        """
        Retrieve memory by key
        
        Args:
            key: Memory key
            
        Returns:
            Retrieved memory
        """
        try:
            # Check long-term memory first
            if key in self._long_term_memory:
                return {
                    'success': True,
                    'data': self._long_term_memory[key],
                    'source': 'long_term'
                }
            
            # Check short-term memory
            for entry in reversed(self._short_term_memory):
                if entry.get('data', '').startswith(key):
                    return {
                        'success': True,
                        'data': entry,
                        'source': 'short_term'
                    }
            
            return {
                'success': False,
                'data': None,
                'error': 'Memory not found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    async def _search_memory(self, query: str) -> Dict[str, Any]:
        """
        Search memory for query
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        try:
            results = []
            
            # Search short-term memory
            for entry in self._short_term_memory:
                if query.lower() in str(entry.get('data', '')).lower():
                    results.append({
                        'entry': entry,
                        'source': 'short_term'
                    })
            
            # Search long-term memory
            for key, entry in self._long_term_memory.items():
                if query.lower() in str(entry.get('data', '')).lower():
                    results.append({
                        'entry': entry,
                        'source': 'long_term',
                        'key': key
                    })
            
            return {
                'success': True,
                'results': results,
                'count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'results': [],
                'error': str(e)
            }
    
    async def _get_context(self) -> Dict[str, Any]:
        """
        Get current context window
        
        Returns:
            Recent memory entries
        """
        recent = self._short_term_memory[-self._context_window:]
        return {
            'success': True,
            'context': recent,
            'window_size': len(recent)
        }
    
    async def _optimize_memory(self) -> Dict[str, Any]:
        """
        Optimize memory storage
        
        Returns:
            Optimization results
        """
        try:
            initial_short_term = len(self._short_term_memory)
            initial_long_term = len(self._long_term_memory)
            
            # Remove old entries from short-term
            cutoff = datetime.now() - timedelta(hours=24)
            self._short_term_memory = [
                entry for entry in self._short_term_memory
                if datetime.fromisoformat(entry['timestamp']) > cutoff
            ]
            
            # Remove old unimportant entries from long-term
            keys_to_remove = []
            for key, entry in self._long_term_memory.items():
                if datetime.fromisoformat(entry['timestamp']) < cutoff:
                    if not entry.get('important', False):
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._long_term_memory[key]
            
            await self._save_long_term_memory()
            
            return {
                'success': True,
                'short_term_removed': initial_short_term - len(self._short_term_memory),
                'long_term_removed': len(keys_to_remove),
                'current_short_term': len(self._short_term_memory),
                'current_long_term': len(self._long_term_memory)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _load_long_term_memory(self):
        """Load long-term memory from file"""
        try:
            with open(self._memory_file, 'r') as f:
                self._long_term_memory = json.load(f)
            self.logger.info(f"Loaded {len(self._long_term_memory)} long-term memories")
        except FileNotFoundError:
            self.logger.info("No existing memory file found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading long-term memory: {e}")
    
    async def _save_long_term_memory(self):
        """Save long-term memory to file"""
        try:
            with open(self._memory_file, 'w') as f:
                json.dump(self._long_term_memory, f, indent=2)
            self.logger.debug("Saved long-term memory")
        except Exception as e:
            self.logger.error(f"Error saving long-term memory: {e}")
    
    async def _handle_store_event(self, event):
        """Handle memory store events"""
        data = event.data.get('data', '')
        context = event.data.get('context', {})
        result = await self._store_memory(data, context)
        
        await self.event_bus.publish(
            event_name="memory.stored",
            data=result,
            source=self.metadata.name
        )
    
    async def _handle_retrieve_event(self, event):
        """Handle memory retrieve events"""
        key = event.data.get('key', '')
        result = await self._retrieve_memory(key)
        
        await self.event_bus.publish(
            event_name="memory.retrieved",
            data=result,
            source=self.metadata.name
        )
    
    async def _handle_clear_event(self, event):
        """Handle memory clear events"""
        self._short_term_memory.clear()
        self.logger.info("Cleared short-term memory")
        
        await self.event_bus.publish(
            event_name="memory.cleared",
            data={'success': True},
            source=self.metadata.name
        )
    
    async def cleanup(self) -> bool:
        """Cleanup skill resources"""
        try:
            self.logger.info("Cleaning up MemorySkill...")
            
            # Save long-term memory
            await self._save_long_term_memory()
            
            # Clear short-term memory
            self._short_term_memory.clear()
            
            self.status = SkillStatus.DISABLED
            self.logger.info("MemorySkill cleanup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return False
    
    def get_capabilities(self) -> List[SkillCapability]:
        """Get skill capabilities"""
        return [SkillCapability.MEMORY]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'short_term_count': len(self._short_term_memory),
            'long_term_count': len(self._long_term_memory),
            'context_window': self._context_window,
            'total_entries': len(self._short_term_memory) + len(self._long_term_memory)
        }
