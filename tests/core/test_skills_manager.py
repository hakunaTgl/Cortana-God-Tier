#!/usr/bin/env python3
"""
Tests for SkillsManager
"""

import pytest
import asyncio

from cortana.core.event_bus import EventBus
from cortana.core.skills_manager import SkillsManager
from cortana.skills.base_skill import SkillCapability


class TestSkillsManager:
    """Test SkillsManager functionality"""
    
    @pytest.mark.asyncio
    async def test_manager_creation(self):
        """Test skills manager creation"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        assert skills_manager is not None
        assert len(skills_manager.enabled_skills) == 3
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test skills manager initialization"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        success = await skills_manager.initialize()
        assert success is True
        assert len(skills_manager.skills) == 3
        await skills_manager.cleanup()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_execute_skill(self):
        """Test executing a specific skill"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        await skills_manager.initialize()
        
        result = await skills_manager.execute_skill('research', 'test query')
        assert 'success' in result
        await skills_manager.cleanup()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_execute_by_capability(self):
        """Test executing by capability"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        await skills_manager.initialize()
        
        results = await skills_manager.execute_by_capability(
            SkillCapability.RESEARCH,
            'test task'
        )
        assert len(results) > 0
        await skills_manager.cleanup()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_list_skills(self):
        """Test listing skills"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        await skills_manager.initialize()
        
        skills = skills_manager.list_skills()
        assert len(skills) == 3
        assert all('name' in skill for skill in skills)
        await skills_manager.cleanup()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        await skills_manager.initialize()
        
        health = await skills_manager.health_check()
        assert len(health) == 3
        assert all(info['healthy'] for info in health.values())
        await skills_manager.cleanup()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_get_skills_by_capability(self):
        """Test getting skills by capability"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        await skills_manager.initialize()
        
        skills = skills_manager.get_skills_by_capability(SkillCapability.SYSTEM)
        assert 'system' in skills
        await skills_manager.cleanup()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_manager_cleanup(self):
        """Test manager cleanup"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'enabled': ['research', 'memory', 'system'],
            'experimental': []
        }
        skills_manager = SkillsManager(bus, config)
        await skills_manager.initialize()
        success = await skills_manager.cleanup()
        assert success is True
        assert len(skills_manager.skills) == 0
        await bus.stop()
