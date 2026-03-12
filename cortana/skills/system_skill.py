#!/usr/bin/env python3
"""
System Skill for Cortana-God-Tier
Handles OS-level operations, system monitoring, and resource management
"""

import asyncio
import psutil
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from cortana.skills.base_skill import (
    BaseSkill, SkillMetadata, SkillStatus, SkillCapability
)
from cortana.core.event_bus import EventBus, EventPriority

logger = logging.getLogger(__name__)


class SystemSkill(BaseSkill):
    """
    System Skill - OS-level integration and monitoring
    
    Capabilities:
    - System resource monitoring
    - Process management
    - File system operations
    - OS integration
    - Performance optimization
    """
    
    def _create_metadata(self) -> SkillMetadata:
        """Create skill metadata"""
        return SkillMetadata(
            name="system",
            version="1.0.0",
            description="OS-level operations and system monitoring",
            capabilities=[SkillCapability.SYSTEM],
            dependencies=["psutil"],
            privacy_level="local",
            experimental=False
        )
    
    async def initialize(self) -> bool:
        """Initialize the system skill"""
        try:
            self.logger.info("Initializing SystemSkill...")
            
            # System information
            self._platform = platform.system()
            self._cpu_count = psutil.cpu_count()
            
            # Monitoring settings
            self._monitoring_enabled = self.config.get('monitoring_enabled', True)
            self._monitor_interval = self.config.get('monitor_interval', 60)  # seconds
            
            # Resource thresholds
            self._memory_threshold = self.config.get('memory_threshold', 80)  # percent
            self._cpu_threshold = self.config.get('cpu_threshold', 90)  # percent
            
            # Monitoring task
            self._monitor_task: Optional[asyncio.Task] = None
            
            # Subscribe to system-related events
            self.subscribe_to_event("system.check", self._handle_check_event)
            self.subscribe_to_event("system.optimize", self._handle_optimize_event)
            
            # Start monitoring if enabled
            if self._monitoring_enabled:
                self._monitor_task = asyncio.create_task(self._monitor_system())
            
            self.status = SkillStatus.READY
            self.logger.info("SystemSkill initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SystemSkill: {e}")
            self.status = SkillStatus.ERROR
            return False
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute system task
        
        Args:
            task: System operation (check, optimize, info, etc.)
            context: Optional context with operation parameters
            
        Returns:
            Operation results dictionary
        """
        context = context or {}
        operation = context.get('operation', 'info')
        
        try:
            if operation == 'info':
                result = await self._get_system_info()
            elif operation == 'memory':
                result = await self._get_memory_info()
            elif operation == 'cpu':
                result = await self._get_cpu_info()
            elif operation == 'disk':
                result = await self._get_disk_info()
            elif operation == 'processes':
                result = await self._get_process_info()
            elif operation == 'optimize':
                result = await self._optimize_system()
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
            self.logger.error(f"System operation error: {e}")
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information
        
        Returns:
            System info dictionary
        """
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'success': True,
                'platform': self._platform,
                'platform_version': platform.version(),
                'python_version': platform.python_version(),
                'cpu_count': self._cpu_count,
                'cpu_percent': cpu_percent,
                'memory_total_gb': memory.total / (1024 ** 3),
                'memory_available_gb': memory.available / (1024 ** 3),
                'memory_percent': memory.percent,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_memory_info(self) -> Dict[str, Any]:
        """
        Get detailed memory information
        
        Returns:
            Memory info dictionary
        """
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'success': True,
                'virtual': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'free': memory.free,
                    'percent': memory.percent
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_cpu_info(self) -> Dict[str, Any]:
        """
        Get detailed CPU information
        
        Returns:
            CPU info dictionary
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            return {
                'success': True,
                'count': self._cpu_count,
                'percent_total': sum(cpu_percent) / len(cpu_percent),
                'percent_per_cpu': cpu_percent,
                'frequency': {
                    'current': cpu_freq.current if cpu_freq else None,
                    'min': cpu_freq.min if cpu_freq else None,
                    'max': cpu_freq.max if cpu_freq else None
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_disk_info(self) -> Dict[str, Any]:
        """
        Get disk information
        
        Returns:
            Disk info dictionary
        """
        try:
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
            
            return {
                'success': True,
                'partitions': partitions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_process_info(self) -> Dict[str, Any]:
        """
        Get process information
        
        Returns:
            Process info dictionary
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 1.0 or info['memory_percent'] > 1.0:
                        processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                'success': True,
                'process_count': len(psutil.pids()),
                'top_processes': processes[:10],  # Top 10
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _optimize_system(self) -> Dict[str, Any]:
        """
        Optimize system resources
        
        Returns:
            Optimization results
        """
        try:
            optimizations = []
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self._memory_threshold:
                optimizations.append({
                    'type': 'memory',
                    'status': 'warning',
                    'message': f'Memory usage high: {memory.percent}%'
                })
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self._cpu_threshold:
                optimizations.append({
                    'type': 'cpu',
                    'status': 'warning',
                    'message': f'CPU usage high: {cpu_percent}%'
                })
            
            return {
                'success': True,
                'optimizations': optimizations,
                'memory_percent': memory.percent,
                'cpu_percent': cpu_percent,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _monitor_system(self):
        """Background task to monitor system resources"""
        self.logger.info("System monitoring started")
        
        while self._monitoring_enabled and self.status == SkillStatus.READY:
            try:
                # Check system resources
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Alert if thresholds exceeded
                if memory.percent > self._memory_threshold:
                    await self.event_bus.publish(
                        event_name="system.alert.memory",
                        data={
                            'type': 'memory',
                            'percent': memory.percent,
                            'threshold': self._memory_threshold
                        },
                        source=self.metadata.name,
                        priority=EventPriority.HIGH
                    )
                
                if cpu_percent > self._cpu_threshold:
                    await self.event_bus.publish(
                        event_name="system.alert.cpu",
                        data={
                            'type': 'cpu',
                            'percent': cpu_percent,
                            'threshold': self._cpu_threshold
                        },
                        source=self.metadata.name,
                        priority=EventPriority.HIGH
                    )
                
                # Wait before next check
                await asyncio.sleep(self._monitor_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring: {e}")
                await asyncio.sleep(self._monitor_interval)
        
        self.logger.info("System monitoring stopped")
    
    async def _handle_check_event(self, event):
        """Handle system check events"""
        result = await self._get_system_info()
        
        await self.event_bus.publish(
            event_name="system.check_result",
            data=result,
            source=self.metadata.name
        )
    
    async def _handle_optimize_event(self, event):
        """Handle system optimize events"""
        result = await self._optimize_system()
        
        await self.event_bus.publish(
            event_name="system.optimize_result",
            data=result,
            source=self.metadata.name
        )
    
    async def cleanup(self) -> bool:
        """Cleanup skill resources"""
        try:
            self.logger.info("Cleaning up SystemSkill...")
            
            # Stop monitoring
            self._monitoring_enabled = False
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass
            
            self.status = SkillStatus.DISABLED
            self.logger.info("SystemSkill cleanup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return False
    
    def get_capabilities(self) -> List[SkillCapability]:
        """Get skill capabilities"""
        return [SkillCapability.SYSTEM]
