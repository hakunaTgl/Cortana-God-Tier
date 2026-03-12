#!/usr/bin/env python3
"""
Code Skill for Cortana-God-Tier
Handles code execution, file operations, GitHub integration, and VSCode interaction
"""

import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import logging

from cortana.skills.base_skill import (
    BaseSkill, SkillMetadata, SkillStatus, SkillCapability
)
from cortana.core.event_bus import EventBus, EventPriority

logger = logging.getLogger(__name__)


class CodeSkill(BaseSkill):
    """
    Code Skill - Code execution and development tools integration
    
    Capabilities:
    - Code execution (safe sandboxing)
    - File operations
    - GitHub integration
    - VSCode integration
    - Terminal command execution
    """
    
    def _create_metadata(self) -> SkillMetadata:
        """Create skill metadata"""
        return SkillMetadata(
            name="code",
            version="1.0.0",
            description="Code execution, file operations, and development tools integration",
            capabilities=[SkillCapability.CODE, SkillCapability.SYSTEM],
            dependencies=["GitPython"],
            privacy_level="local",
            experimental=False
        )
    
    async def initialize(self) -> bool:
        """Initialize the code skill"""
        try:
            self.logger.info("Initializing CodeSkill...")
            
            # Configuration
            self._safe_mode = self.config.get('safe_mode', True)
            self._allowed_commands = self.config.get('allowed_commands', [
                'ls', 'pwd', 'echo', 'cat', 'git'
            ])
            self._workspace_path = self.config.get('workspace_path', os.getcwd())
            
            # Execution history
            self._execution_history: List[Dict[str, Any]] = []
            self._max_history = 50
            
            # Subscribe to code-related events
            self.subscribe_to_event("code.execute", self._handle_execute_event)
            self.subscribe_to_event("code.file_operation", self._handle_file_operation_event)
            
            self.status = SkillStatus.READY
            self.logger.info("CodeSkill initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CodeSkill: {e}")
            self.status = SkillStatus.ERROR
            return False
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute code task
        
        Args:
            task: Code task (command, file operation, etc.)
            context: Optional context with task parameters
            
        Returns:
            Execution results dictionary
        """
        context = context or {}
        task_type = context.get('type', 'command')
        
        try:
            if task_type == 'command':
                result = await self._execute_command(task, context)
            elif task_type == 'file_read':
                result = await self._read_file(context.get('file_path', ''))
            elif task_type == 'file_write':
                result = await self._write_file(
                    context.get('file_path', ''),
                    context.get('content', '')
                )
            elif task_type == 'github':
                result = await self._github_operation(task, context)
            else:
                result = {
                    'success': False,
                    'output': '',
                    'error': f'Unknown task type: {task_type}'
                }
            
            # Add to history
            self._add_to_history({
                'task': task,
                'type': task_type,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': result.get('success', False),
                'result': result,
            }
            
        except Exception as e:
            self.logger.error(f"Code execution error: {e}")
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    async def _execute_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute terminal command with safety checks
        
        Args:
            command: Command to execute
            context: Execution context
            
        Returns:
            Execution result
        """
        # Safety check
        if self._safe_mode:
            command_base = command.split()[0] if command.split() else ''
            if command_base not in self._allowed_commands:
                return {
                    'success': False,
                    'output': '',
                    'error': f'Command "{command_base}" not allowed in safe mode'
                }
        
        try:
            self.logger.info(f"Executing command: {command}")
            
            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=context.get('cwd', self._workspace_path)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=context.get('timeout', 30)
                )
                
                return {
                    'success': process.returncode == 0,
                    'output': stdout.decode('utf-8'),
                    'error': stderr.decode('utf-8') if stderr else '',
                    'return_code': process.returncode
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    'success': False,
                    'output': '',
                    'error': 'Command execution timed out'
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file contents
        
        Args:
            file_path: Path to file
            
        Returns:
            File contents
        """
        try:
            # Security: Ensure path is within workspace
            abs_path = os.path.abspath(file_path)
            workspace_abs = os.path.abspath(self._workspace_path)
            
            if not abs_path.startswith(workspace_abs):
                return {
                    'success': False,
                    'content': '',
                    'error': 'File path outside workspace'
                }
            
            with open(abs_path, 'r') as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'path': abs_path,
                'size': len(content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': str(e)
            }
    
    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to file
        
        Args:
            file_path: Path to file
            content: Content to write
            
        Returns:
            Write result
        """
        try:
            # Security: Ensure path is within workspace
            abs_path = os.path.abspath(file_path)
            workspace_abs = os.path.abspath(self._workspace_path)
            
            if not abs_path.startswith(workspace_abs):
                return {
                    'success': False,
                    'error': 'File path outside workspace'
                }
            
            # Create directory if needed
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            with open(abs_path, 'w') as f:
                f.write(content)
            
            return {
                'success': True,
                'path': abs_path,
                'bytes_written': len(content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _github_operation(self, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform GitHub operations
        
        Args:
            operation: GitHub operation (clone, pull, push, status)
            context: Operation context
            
        Returns:
            Operation result
        """
        # Placeholder for GitHub integration
        # In production, this would use PyGithub or GitPython
        return {
            'success': True,
            'operation': operation,
            'message': f'GitHub operation "{operation}" executed (placeholder)'
        }
    
    def _add_to_history(self, entry: Dict[str, Any]):
        """Add execution to history"""
        self._execution_history.append(entry)
        if len(self._execution_history) > self._max_history:
            self._execution_history.pop(0)
    
    async def _handle_execute_event(self, event):
        """Handle code execution events"""
        self.logger.debug(f"Received execute event from {event.source}")
        task = event.data.get('task', '')
        context = event.data.get('context', {})
        
        result = await self._safe_execute(task, context)
        
        # Publish result
        await self.event_bus.publish(
            event_name="code.result",
            data=result,
            source=self.metadata.name,
            priority=EventPriority.NORMAL
        )
    
    async def _handle_file_operation_event(self, event):
        """Handle file operation events"""
        self.logger.debug(f"Received file operation event from {event.source}")
        # Handle file operation
        pass
    
    async def cleanup(self) -> bool:
        """Cleanup skill resources"""
        try:
            self.logger.info("Cleaning up CodeSkill...")
            
            # Clear history
            self._execution_history.clear()
            
            self.status = SkillStatus.DISABLED
            self.logger.info("CodeSkill cleanup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return False
    
    def get_capabilities(self) -> List[SkillCapability]:
        """Get skill capabilities"""
        return [SkillCapability.CODE, SkillCapability.SYSTEM]
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self._execution_history.copy()
