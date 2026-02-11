#!/usr/bin/env python3
"""
Cortana God-Tier AI Assistant
Memory-optimized, privacy-first personal AI assistant
with modular skills-based architecture
"""

import sys
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import psutil
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from cortana.core.event_bus import EventBus
from cortana.core.skills_manager import SkillsManager
from cortana.skills.base_skill import SkillCapability

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()

class CortanaAssistant:
    """
    Cortana God-Tier - Advanced AI Personal Assistant
    
    Features:
    - Modular skills-based architecture
    - Event-driven skill communication
    - Hot-reloadable skills
    - 50-75% RAM reduction through quantization
    - Memory-optimized architecture
    - Privacy-first design
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        self.version = "1.0.0-modular"
        self.start_time = datetime.now()
        self.config = self._load_config(config_path)
        
        # Initialize core components
        self.event_bus: Optional[EventBus] = None
        self.skills_manager: Optional[SkillsManager] = None
        self._initialized = False
        
        console.print(Panel.fit(
            "[bold cyan]Cortana God-Tier AI Assistant[/bold cyan]\n"
            "[green]Modular Skills | Event-Driven | Privacy-First[/green]",
            border_style="cyan"
        ))
        self._check_system()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            return {}
    
    async def initialize(self) -> bool:
        """Initialize the assistant asynchronously"""
        try:
            logger.info("Initializing Cortana Assistant...")
            
            # Initialize event bus
            event_bus_config = self.config.get('event_bus', {})
            max_queue_size = event_bus_config.get('max_queue_size', 1000)
            self.event_bus = EventBus(max_queue_size=max_queue_size)
            await self.event_bus.start()
            logger.info("Event bus started")
            
            # Initialize skills manager
            skills_config = self.config.get('skills', {})
            self.skills_manager = SkillsManager(self.event_bus, skills_config)
            success = await self.skills_manager.initialize()
            
            if not success:
                logger.error("Failed to initialize all skills")
                return False
            
            self._initialized = True
            logger.info("Cortana Assistant initialized successfully")
            
            # Display skills status
            self._display_skills_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    def _display_skills_status(self):
        """Display loaded skills status"""
        if not self.skills_manager:
            return
        
        skills = self.skills_manager.list_skills()
        console.print("\n[bold]Loaded Skills:[/bold]")
        for skill in skills:
            status_color = "green" if skill['status'] == 'ready' else "yellow"
            console.print(f"  [{status_color}]✓[/{status_color}] {skill['name']} v{skill['version']} - {skill['description']}")
    
    def _check_system(self):
        """Check system resources"""
        memory = psutil.virtual_memory()
        console.print(f"\n[bold]System Status:[/bold]")
        console.print(f"  Memory Available: {memory.available / (1024**3):.2f} GB")
        console.print(f"  Memory Usage: {memory.percent}%")
        console.print(f"  CPU Count: {psutil.cpu_count()}")
    
    async def process_query(self, query: str) -> str:
        """
        Process user query using skills system
        
        Args:
            query: User input query
            
        Returns:
            AI-generated response
        """
        if not self._initialized:
            return "Error: Assistant not initialized. Please wait..."
        
        logger.info(f"Processing query: {query[:50]}...")
        
        try:
            # Route query to appropriate skill based on content
            query_lower = query.lower()
            
            # Memory-related queries
            if any(word in query_lower for word in ['remember', 'recall', 'memory', 'context']):
                result = await self.skills_manager.execute_skill('memory', query, {'operation': 'search'})
                if result['success']:
                    return self._format_response(result, 'memory')
            
            # System-related queries
            elif any(word in query_lower for word in ['memory', 'cpu', 'system', 'status', 'health']):
                result = await self.skills_manager.execute_skill('system', query, {'operation': 'info'})
                if result['success']:
                    return self._format_response(result, 'system')
            
            # Research-related queries
            elif any(word in query_lower for word in ['search', 'find', 'research', 'what is', 'how to']):
                result = await self.skills_manager.execute_skill('research', query)
                if result['success']:
                    return self._format_response(result, 'research')
            
            # Code-related queries
            elif any(word in query_lower for word in ['code', 'execute', 'run', 'file', 'github']):
                result = await self.skills_manager.execute_skill('code', query, {'type': 'command'})
                if result['success']:
                    return self._format_response(result, 'code')
            
            # Built-in commands
            elif 'hello' in query_lower:
                return self._get_hello_message()
            elif 'help' in query_lower:
                return self._get_help()
            elif 'skills' in query_lower:
                return self._get_skills_info()
            else:
                return (
                    f"I understand you're asking: '{query}'. "
                    "I'm running with modular skills architecture. "
                    "Try: 'help', 'status', 'skills', or ask me to research something!"
                )
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing query: {e}"
    
    def _format_response(self, result: Dict[str, Any], skill_name: str) -> str:
        """Format skill result for display"""
        if not result.get('success'):
            return f"Error from {skill_name} skill: {result.get('error', 'Unknown error')}"
        
        data = result.get('result', {})
        
        if skill_name == 'system':
            return self._format_system_response(data)
        elif skill_name == 'memory':
            return self._format_memory_response(data)
        elif skill_name == 'research':
            return self._format_research_response(data)
        elif skill_name == 'code':
            return self._format_code_response(data)
        else:
            return str(data)
    
    def _format_system_response(self, data: Dict[str, Any]) -> str:
        """Format system skill response"""
        if 'platform' in data:
            return (
                f"System: {data.get('platform', 'Unknown')}\n"
                f"CPU: {data.get('cpu_count', 0)} cores @ {data.get('cpu_percent', 0):.1f}%\n"
                f"Memory: {data.get('memory_available_gb', 0):.2f}GB available ({data.get('memory_percent', 0):.1f}% used)"
            )
        return str(data)
    
    def _format_memory_response(self, data: Dict[str, Any]) -> str:
        """Format memory skill response"""
        if 'results' in data:
            count = data.get('count', 0)
            return f"Found {count} memory entries matching your query."
        return str(data)
    
    def _format_research_response(self, data: Dict[str, Any]) -> str:
        """Format research skill response"""
        if 'summary' in data:
            return data['summary']
        return str(data)
    
    def _format_code_response(self, data: Dict[str, Any]) -> str:
        """Format code skill response"""
        if 'output' in data:
            return f"Output:\n{data['output']}\n{data.get('error', '')}"
        return str(data)
    
    def _get_hello_message(self) -> str:
        """Get hello message"""
        return (
            "Hello! I'm Cortana God-Tier with modular skills architecture. "
            "I can help you with research, code execution, memory management, and system monitoring. "
            "Type 'help' to see what I can do!"
        )
    
    def _get_status(self) -> str:
        """Get system status"""
        uptime = datetime.now() - self.start_time
        memory = psutil.virtual_memory()
        
        skills_info = ""
        if self.skills_manager:
            skills = self.skills_manager.list_skills()
            skills_info = f"\nActive Skills: {len(skills)}"
        
        return (
            f"Cortana God-Tier v{self.version}\n"
            f"Uptime: {uptime.seconds}s\n"
            f"Memory: {memory.percent}% used\n"
            f"Status: OPERATIONAL ✓{skills_info}"
        )
    
    def _get_help(self) -> str:
        """Get help information"""
        return (
            "Available Commands:\n"
            "  'hello' - Greet Cortana\n"
            "  'status' - View system status\n"
            "  'skills' - List loaded skills\n"
            "  'memory' - Check memory usage\n"
            "  'research <query>' - Research a topic\n"
            "  'help' - Show this message\n"
            "  'quit' - Exit Cortana\n\n"
            "Skills Architecture:\n"
            "  Research - Web search and information gathering\n"
            "  Code - Execute commands and manage files\n"
            "  Memory - Context and memory management\n"
            "  System - OS-level operations and monitoring"
        )
    
    def _get_skills_info(self) -> str:
        """Get skills information"""
        if not self.skills_manager:
            return "Skills manager not initialized"
        
        skills = self.skills_manager.list_skills()
        info = "Loaded Skills:\n"
        for skill in skills:
            status = "✓" if skill['status'] == 'ready' else "✗"
            info += f"  {status} {skill['name']} v{skill['version']}\n"
            info += f"    {skill['description']}\n"
            info += f"    Capabilities: {', '.join(skill['capabilities'])}\n"
        
        return info
    
    def run(self):
        """Run interactive assistant"""
        # Initialize async components
        try:
            asyncio.run(self._async_run())
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
        except Exception as e:
            logger.error(f"Error running assistant: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    async def _async_run(self):
        """Async run loop"""
        # Initialize
        success = await self.initialize()
        if not success:
            console.print("[red]Failed to initialize assistant[/red]")
            return
        
        console.print("\n[bold green]Cortana is ready![/bold green] Type 'help' for commands or 'quit' to exit.\n")
        
        # Main interaction loop
        while True:
            try:
                query = await asyncio.to_thread(console.input, "[bold cyan]You:[/bold cyan] ")
                
                if query.lower() in ['quit', 'exit', 'bye']:
                    console.print("[yellow]Goodbye! Cortana shutting down...[/yellow]")
                    break
                
                if not query.strip():
                    continue
                
                # Process query asynchronously
                response = await self.process_query(query)
                console.print(f"[bold magenta]Cortana:[/bold magenta] {response}\n")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                console.print(f"[red]Error: {e}[/red]\n")
        
        # Cleanup
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up...")
            
            if self.skills_manager:
                await self.skills_manager.cleanup()
            
            if self.event_bus:
                await self.event_bus.stop()
            
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """Main entry point"""
    try:
        assistant = CortanaAssistant()
        assistant.run()
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
