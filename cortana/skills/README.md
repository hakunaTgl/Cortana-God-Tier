# Cortana Skills System

## Overview

The Cortana Skills System is a modular, event-driven architecture that enables hot-swappable capabilities through independent skill modules. Each skill is a self-contained unit with its own lifecycle, configuration, and capabilities.

## Architecture

### Core Components

1. **EventBus** (`cortana/core/event_bus.py`)
   - Async publish/subscribe mechanism
   - Priority-based event handling
   - Event history tracking
   - Queue management

2. **BaseSkill** (`cortana/skills/base_skill.py`)
   - Abstract base class for all skills
   - Standard interface: `initialize()`, `execute()`, `cleanup()`
   - Automatic error handling and metrics tracking
   - Event subscription management

3. **SkillsManager** (`cortana/core/skills_manager.py`)
   - Orchestrates skill lifecycle
   - Capability-based routing
   - Hot-reload support
   - Health monitoring

### Available Skills

#### Research Skill
- **Capabilities**: Research, Analysis
- **Features**:
  - Web search and information gathering
  - Result caching
  - Source verification
  - Summarization

#### Code Skill
- **Capabilities**: Code, System
- **Features**:
  - Safe command execution
  - File operations
  - GitHub integration
  - VSCode integration

#### Memory Skill
- **Capabilities**: Memory
- **Features**:
  - Short-term memory (session)
  - Long-term memory (persistent)
  - Context window management
  - Privacy-preserving storage

#### System Skill
- **Capabilities**: System
- **Features**:
  - Resource monitoring
  - Process management
  - Performance optimization
  - Health alerts

## Creating a New Skill

### 1. Create Skill Class

```python
from cortana.skills.base_skill import BaseSkill, SkillMetadata, SkillCapability

class MySkill(BaseSkill):
    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="my_skill",
            version="1.0.0",
            description="My custom skill",
            capabilities=[SkillCapability.RESEARCH],
            dependencies=["requests"],
            privacy_level="local"
        )
    
    async def initialize(self) -> bool:
        # Setup resources
        self.status = SkillStatus.READY
        return True
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Main skill logic
        return {
            'success': True,
            'result': "Task completed"
        }
    
    async def cleanup(self) -> bool:
        # Cleanup resources
        return True
    
    def get_capabilities(self) -> List[SkillCapability]:
        return [SkillCapability.RESEARCH]
```

### 2. Register Skill

Add to `SkillsManager.SKILL_REGISTRY`:

```python
SKILL_REGISTRY = {
    'my_skill': MySkill,
    # ... other skills
}
```

### 3. Configure Skill

Add to `config.yaml`:

```yaml
skills:
  enabled:
    - my_skill
  
  my_skill:
    option1: value1
    option2: value2
```

### 4. Add Tests

Create `tests/skills/test_my_skill.py`:

```python
import pytest
from cortana.skills.my_skill import MySkill

class TestMySkill:
    @pytest.mark.asyncio
    async def test_skill_execution(self):
        # Test your skill
        pass
```

## Event-Driven Communication

### Publishing Events

```python
await self.event_bus.publish(
    event_name="my_skill.completed",
    data={'result': 'success'},
    source=self.metadata.name,
    priority=EventPriority.NORMAL
)
```

### Subscribing to Events

```python
async def initialize(self) -> bool:
    self.subscribe_to_event("other_skill.event", self._handle_event)
    return True

async def _handle_event(self, event):
    # Handle the event
    pass
```

## Hot Reloading

Skills can be reloaded at runtime:

```python
# Reload a skill
await skills_manager.reload_skill('my_skill')

# Add a new skill at runtime
await skills_manager.add_skill('new_skill', NewSkillClass)

# Remove a skill
await skills_manager.remove_skill('old_skill')
```

## Capability-Based Routing

Execute tasks by capability instead of specific skill:

```python
# Execute with all skills that have RESEARCH capability
results = await skills_manager.execute_by_capability(
    SkillCapability.RESEARCH,
    "Find information about X"
)
```

## Configuration

### Event Bus Configuration

```yaml
event_bus:
  async_enabled: true
  max_queue_size: 1000
```

### Skills Configuration

```yaml
skills:
  enabled:
    - research
    - code
    - memory
    - system
  
  experimental:
    - beta_skill
  
  # Skill-specific config
  research:
    max_results: 10
    cache_enabled: true
```

## Best Practices

1. **Async First**: All skill operations should be async
2. **Error Handling**: Use try-except in execute() methods
3. **Resource Cleanup**: Always cleanup in cleanup() method
4. **Event Publishing**: Publish events for important state changes
5. **Privacy**: Mark privacy_level accurately in metadata
6. **Testing**: Write comprehensive tests for each skill
7. **Documentation**: Document capabilities and configuration options

## Skill Lifecycle

```
UNINITIALIZED -> INITIALIZING -> READY -> BUSY -> READY
                                   ↓
                              ERROR/DISABLED
```

- **UNINITIALIZED**: Just created
- **INITIALIZING**: Running initialize()
- **READY**: Available for execution
- **BUSY**: Currently executing
- **ERROR**: Error occurred
- **DISABLED**: Cleanup completed

## Monitoring and Stats

### Skill Stats

```python
stats = skill.get_stats()
# Returns:
# {
#     'name': 'research',
#     'version': '1.0.0',
#     'status': 'ready',
#     'execution_count': 42,
#     'error_count': 2,
#     'last_execution': '2024-01-01T12:00:00',
#     'capabilities': ['research', 'analysis']
# }
```

### Health Check

```python
health = await skills_manager.health_check()
# Returns status for all skills
```

## Examples

### Execute a Skill

```python
result = await skills_manager.execute_skill(
    'research',
    'Find latest AI news',
    {'max_results': 5}
)
```

### List All Skills

```python
skills = skills_manager.list_skills()
for skill in skills:
    print(f"{skill['name']} v{skill['version']}: {skill['description']}")
```

### Get Skills by Capability

```python
system_skills = skills_manager.get_skills_by_capability(SkillCapability.SYSTEM)
```

## Troubleshooting

### Skill Won't Initialize

1. Check skill dependencies are installed
2. Verify configuration is valid
3. Check logs for error messages
4. Ensure event bus is started

### Events Not Received

1. Verify subscription before publishing
2. Check event names match exactly
3. Ensure event bus is running
4. Check handler is async

### Memory Leaks

1. Implement proper cleanup()
2. Unsubscribe from events
3. Clear caches and references
4. Check for circular references

## Future Enhancements

- [ ] Skill marketplace
- [ ] Remote skill loading
- [ ] Skill dependencies resolution
- [ ] Skill versioning and compatibility
- [ ] Skill sandboxing
- [ ] Performance profiling per skill
