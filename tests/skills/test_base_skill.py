#!/usr/bin/env python3
"""
Tests for BaseSkill
"""

import pytest
import asyncio
from typing import Dict, Any, List, Optional

from cortana.core.event_bus import EventBus
from cortana.skills.base_skill import (
    BaseSkill, SkillMetadata, SkillStatus, SkillCapability
)


class TestSkill(BaseSkill):
    """Test skill implementation for testing"""
    
    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="test_skill",
            version="1.0.0",
            description="Test skill",
            capabilities=[SkillCapability.RESEARCH]
        )
    
    async def initialize(self) -> bool:
        self.status = SkillStatus.READY
        return True
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            'success': True,
            'result': f"Executed: {task}",
        }
    
    async def cleanup(self) -> bool:
        self.status = SkillStatus.DISABLED
        return True
    
    def get_capabilities(self) -> List[SkillCapability]:
        return [SkillCapability.RESEARCH]


class TestBaseSkill:
    """Test BaseSkill functionality"""
    
    @pytest.mark.asyncio
    async def test_skill_creation(self):
        """Test skill can be created"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        assert test_skill is not None
        assert test_skill.status == SkillStatus.UNINITIALIZED
        assert test_skill.metadata.name == "test_skill"
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_initialization(self):
        """Test skill initialization"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        success = await test_skill.initialize()
        assert success is True
        assert test_skill.status == SkillStatus.READY
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_execution(self):
        """Test skill execution"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        await test_skill.initialize()
        
        result = await test_skill._safe_execute("test task")
        assert result['success'] is True
        assert 'Executed' in result['result']
        assert 'metadata' in result
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_cleanup(self):
        """Test skill cleanup"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        await test_skill.initialize()
        success = await test_skill.cleanup()
        assert success is True
        assert test_skill.status == SkillStatus.DISABLED
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_stats(self):
        """Test skill statistics"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        await test_skill.initialize()
        await test_skill._safe_execute("test")
        
        stats = test_skill.get_stats()
        assert stats['name'] == "test_skill"
        assert stats['execution_count'] == 1
        assert stats['error_count'] == 0
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_health_check(self):
        """Test skill health check"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        await test_skill.initialize()
        is_healthy = await test_skill.health_check()
        assert is_healthy is True
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_skill_capabilities(self):
        """Test skill capabilities"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        test_skill = TestSkill(bus)
        capabilities = test_skill.get_capabilities()
        assert SkillCapability.RESEARCH in capabilities
        await bus.stop()
