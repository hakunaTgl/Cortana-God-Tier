#!/usr/bin/env python3
"""
Tests for EventBus
"""

import pytest
import asyncio
from cortana.core.event_bus import EventBus, Event, EventPriority


class TestEventBus:
    """Test EventBus functionality"""
    
    @pytest.mark.asyncio
    async def test_event_bus_creation(self):
        """Test event bus can be created"""
        bus = EventBus(max_queue_size=100)
        assert bus is not None
        assert bus.max_queue_size == 100
    
    @pytest.mark.asyncio
    async def test_event_bus_start_stop(self):
        """Test event bus can start and stop"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        assert bus._running is True
        await bus.stop()
        assert bus._running is False
    
    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe(self):
        """Test subscribing and unsubscribing to events"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        
        async def handler(event):
            pass
        
        bus.subscribe("test.event", handler)
        assert "test.event" in bus._subscribers
        assert handler in bus._subscribers["test.event"]
        
        bus.unsubscribe("test.event", handler)
        assert handler not in bus._subscribers["test.event"]
        
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_publish_event(self):
        """Test publishing events"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        bus.subscribe("test.event", handler)
        
        await bus.publish(
            event_name="test.event",
            data={"message": "test"},
            source="test",
            priority=EventPriority.NORMAL
        )
        
        # Wait for event processing
        await asyncio.sleep(0.2)
        
        assert len(received_events) == 1
        assert received_events[0].name == "test.event"
        assert received_events[0].data["message"] == "test"
        
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Test multiple subscribers for same event"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        
        received_count = [0]
        
        async def handler1(event):
            received_count[0] += 1
        
        async def handler2(event):
            received_count[0] += 1
        
        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)
        
        await bus.publish(
            event_name="test.event",
            data={},
            source="test"
        )
        
        await asyncio.sleep(0.2)
        
        assert received_count[0] == 2
        
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_event_history(self):
        """Test event history tracking"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        
        await bus.publish(
            event_name="test.event",
            data={"test": 1},
            source="test"
        )
        
        await asyncio.sleep(0.1)
        
        history = bus.get_history()
        assert len(history) >= 1
        
        event_history = bus.get_history("test.event")
        assert len(event_history) >= 1
        assert event_history[0].name == "test.event"
        
        await bus.stop()
    
    @pytest.mark.asyncio
    async def test_event_stats(self):
        """Test event bus statistics"""
        bus = EventBus(max_queue_size=100)
        await bus.start()
        
        async def handler(event):
            pass
        
        bus.subscribe("test.event", handler)
        
        stats = bus.get_stats()
        assert 'running' in stats
        assert 'queue_size' in stats
        assert 'subscribers' in stats
        assert stats['running'] is True
        
        await bus.stop()
