#!/usr/bin/env python3
"""
Tests for ResearchSkill
"""

import pytest
import asyncio

from cortana.core.event_bus import EventBus
from cortana.skills.research_skill import ResearchSkill


class TestResearchSkill:
    """Test ResearchSkill functionality"""
    
    @pytest.mark.asyncio
    async def test_skill_creation(self):
        """Test research skill creation"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'search_enabled': True,
            'max_results': 5,
            'max_cache_size': 10
        }
        research_skill = ResearchSkill(bus, config)
        assert research_skill is not None
        assert research_skill.metadata.name == "research"
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_initialization(self):
        """Test research skill initialization"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'search_enabled': True,
            'max_results': 5,
            'max_cache_size': 10
        }
        research_skill = ResearchSkill(bus, config)
        success = await research_skill.initialize()
        assert success is True
        assert research_skill.is_ready()
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_research_execution(self):
        """Test research execution"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'search_enabled': True,
            'max_results': 5,
            'max_cache_size': 10
        }
        research_skill = ResearchSkill(bus, config)
        await research_skill.initialize()
        
        result = await research_skill._safe_execute("test query")
        assert result['success'] is True
        assert 'result' in result
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_research_caching(self):
        """Test research result caching"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'search_enabled': True,
            'max_results': 5,
            'max_cache_size': 10
        }
        research_skill = ResearchSkill(bus, config)
        await research_skill.initialize()
        
        # First execution
        result1 = await research_skill.execute("test query")
        assert result1['success'] is True
        assert result1.get('cached', False) is False
        
        # Second execution should use cache
        result2 = await research_skill.execute("test query")
        assert result2['success'] is True
        assert result2.get('cached', False) is True
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_cache_stats(self):
        """Test cache statistics"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        config = {
            'search_enabled': True,
            'max_results': 5,
            'max_cache_size': 10
        }
        research_skill = ResearchSkill(bus, config)
        await research_skill.initialize()
        await research_skill._safe_execute("query1")
        
        stats = research_skill.get_cache_stats()
        assert 'cache_size' in stats
        assert stats['cache_size'] > 0
        await bus.stop()
