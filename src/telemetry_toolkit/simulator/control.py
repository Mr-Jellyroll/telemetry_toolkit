from dataclasses import dataclass
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class ControlCommand:
    """
    Control command sent to Av
    """
    target_altitude: Optional[float] = None
    target_speed: Optional[float] = None
    target_heading: Optional[float] = None
    emergency_stop: bool = False

class VehicleControlSystem:
    """
    Control commands with the telemetry sim.
    """
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.is_emergency_mode = False
        self._command_queue = asyncio.Queue()
        self.running = False
        self._pending_tasks = set()
    
    async def start(self):

        logger.info("Starting vehicle control system")
        self.running = True
        
        try:
            while self.running:
                try:
                    # Get next command with timeout
                    command = await asyncio.wait_for(
                        self._command_queue.get(), 
                        timeout=0.5
                    )
                    
                    # Process the command
                    await self._process_command(command)
                    
                    # Mark command as done
                    self._command_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # Normal timeout, just continue
                    continue
                except asyncio.CancelledError:
                    logger.info("Control system processing cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    continue
        finally:
            self.running = False
            # Clean up any pending tasks
            await self._cleanup_tasks()
    
    async def _cleanup_tasks(self):

        if self._pending_tasks:
            logger.debug(f"Cleaning up {len(self._pending_tasks)} pending tasks")
            for task in self._pending_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            self._pending_tasks.clear()
    
    async def _process_command(self, command: ControlCommand):
        """
        Process a single control command.
        """
        logger.info(f"Processing command: {command}")
        
        if command.emergency_stop:
            await self._activate_emergency_mode()
            return
            
        if self.is_emergency_mode:
            logger.warning("Command rejected: Emergency mode active")
            return
            
        # Update vehicle parameters
        if command.target_altitude is not None:
            self.simulator.set_target_altitude(float(command.target_altitude))
            
        if command.target_speed is not None:
            self.simulator.set_target_speed(float(command.target_speed))
            
        if command.target_heading is not None:
            self.simulator.set_heading(float(command.target_heading))
    
    async def _activate_emergency_mode(self):

        logger.warning("EMERGENCY MODE ACTIVATED")
        self.is_emergency_mode = True
        
        # Emergency landing sequence
        self.simulator.set_target_speed(0.0)
        await asyncio.sleep(0.1)
        self.simulator.set_target_altitude(0.0)
    
    async def send_command(self, command: ControlCommand):
        """Queue a new control command."""
        if not self.running:
            raise RuntimeError("Control system not running")
        await self._command_queue.put(command)
    
    def execute_takeoff_sequence(self, target_altitude: float = 300.0):

        if not self.is_emergency_mode:
            task = asyncio.create_task(self._takeoff_sequence(target_altitude))
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)
    
    async def _takeoff_sequence(self, target_altitude: float):

        logger.info("Initiating takeoff sequence")
        
        await self.send_command(ControlCommand(
            target_altitude=50.0,
            target_speed=5.0
        ))
        await asyncio.sleep(1)
        
        await self.send_command(ControlCommand(
            target_altitude=target_altitude,
            target_speed=20.0
        ))
    
    def execute_landing_sequence(self):

        if not self.is_emergency_mode:
            task = asyncio.create_task(self._landing_sequence())
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)
    
    async def _landing_sequence(self):

        logger.info("Initiating landing sequence")
        
        await self.send_command(ControlCommand(
            target_speed=10.0
        ))
        await asyncio.sleep(1)
        
        await self.send_command(ControlCommand(
            target_altitude=0.0,
            target_speed=5.0
        ))