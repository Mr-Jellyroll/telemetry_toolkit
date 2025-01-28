from dataclasses import dataclass
from typing import Optional
import asyncio
import logging

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class ControlCommand:

    target_altitude: Optional[float] = None
    target_speed: Optional[float] = None
    target_heading: Optional[float] = None
    emergency_stop: bool = False

    def __str__(self):

        params = []
        if self.target_altitude is not None:
            params.append(f"altitude={self.target_altitude:.1f}m")
        if self.target_speed is not None:
            params.append(f"speed={self.target_speed:.1f}m/s")
        if self.target_heading is not None:
            params.append(f"heading={self.target_heading:.1f}°")
        if self.emergency_stop:
            params.append("EMERGENCY STOP")
        return f"ControlCommand({', '.join(params)})"

class VehicleControlSystem:

    
    def __init__(self, simulator):

        self.simulator = simulator
        self.is_emergency_mode = False
        self._command_queue = asyncio.Queue()
        self.running = False
        self._pending_tasks = set()
        logger.info("Initialized control system")
    
    async def start(self):

        logger.info("Starting vehicle control system")
        self.running = True
        
        try:
            while self.running:
                try:

                    command = await asyncio.wait_for(
                        self._command_queue.get(), 
                        timeout=0.5
                    )
                    

                    await self._process_command(command)
                    

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

            await self._cleanup_tasks()
    
    async def _cleanup_tasks(self):
        """Clean up any pending tasks."""
        if self._pending_tasks:
            logger.debug(f"Cleaning up {len(self._pending_tasks)} pending tasks")
            for task in self._pending_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            self._pending_tasks.clear()
    
    async def _process_command(self, command: ControlCommand):
        """Process a single control command."""
        logger.info(f"Processing command: {command}")
        
        try:
            # Handle emergency stop first
            if command.emergency_stop:
                await self._activate_emergency_mode()
                return
                
            # Don't process other commands in emergency mode
            if self.is_emergency_mode:
                logger.warning("Command rejected: Emergency mode active")
                return
                
            # Update vehicle parameters
            if command.target_altitude is not None:
                self.simulator.set_target_altitude(float(command.target_altitude))
                logger.debug(f"Set target altitude to {command.target_altitude}")
                
            if command.target_speed is not None:
                self.simulator.set_target_speed(float(command.target_speed))
                logger.debug(f"Set target speed to {command.target_speed}")
                
            if command.target_heading is not None:
                self.simulator.set_heading(float(command.target_heading))
                logger.debug(f"Set heading to {command.target_heading}")
                
        except Exception as e:
            logger.exception(f"Error processing command: {e}")
            raise
    
    async def _activate_emergency_mode(self):

        logger.warning("EMERGENCY MODE ACTIVATED")
        self.is_emergency_mode = True
        
        try:

            logger.debug("Emergency sequence - Setting speed to 0")
            self.simulator.set_target_speed(0.0)
            await asyncio.sleep(0.1)  # Brief pause
            

            logger.debug("Emergency sequence - Setting altitude to 0")
            self.simulator.set_target_altitude(0.0)
            
            # Verify emergency parameters were set
            if self.simulator.target_speed != 0.0 or self.simulator.target_altitude != 0.0:
                logger.error("Failed to set emergency parameters")
                logger.debug(f"Current state - Speed: {self.simulator.target_speed}, "
                           f"Altitude: {self.simulator.target_altitude}")
            
        except Exception as e:
            logger.exception(f"Error in emergency mode activation: {e}")
            raise
    
    async def send_command(self, command: ControlCommand):

        if not self.running:
            raise RuntimeError("Control system not running")
        logger.debug(f"Queueing command: {command}")
        await self._command_queue.put(command)
    
    def execute_takeoff_sequence(self, target_altitude: float = 300.0):

        if not self.is_emergency_mode:
            logger.info(f"Starting takeoff sequence to {target_altitude}m")
            task = asyncio.create_task(self._takeoff_sequence(target_altitude))
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)
    
    async def _takeoff_sequence(self, target_altitude: float):

        try:
            logger.debug("Takeoff phase 1: Initial climb")
            await self.send_command(ControlCommand(
                target_altitude=50.0,
                target_speed=5.0
            ))
            await asyncio.sleep(1)
            
            logger.debug("Takeoff phase 2: Climbing to target altitude")
            await self.send_command(ControlCommand(
                target_altitude=target_altitude,
                target_speed=20.0
            ))
            

            await self._command_queue.join()
            
        except Exception as e:
            logger.error(f"Error in takeoff sequence: {e}")
            raise
    
    def execute_landing_sequence(self):

        if not self.is_emergency_mode:
            logger.info("Starting landing sequence")
            task = asyncio.create_task(self._landing_sequence())
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)
    
    async def _landing_sequence(self):

        try:
            logger.debug("Landing phase 1: Reducing speed")
            await self.send_command(ControlCommand(
                target_speed=10.0
            ))
            await asyncio.sleep(1)
            
            logger.debug("Landing phase 2: Final approach")
            await self.send_command(ControlCommand(
                target_altitude=0.0,
                target_speed=5.0
            ))
            
            # Wait for commands to be processed
            await self._command_queue.join()
            
        except Exception as e:
            logger.error(f"Error in landing sequence: {e}")
            raise