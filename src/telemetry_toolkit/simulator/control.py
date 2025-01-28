from dataclasses import dataclass
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class ControlCommand:
    """
    Control command sent to the vehicle.
    """
    target_altitude: Optional[float] = None
    target_speed: Optional[float] = None
    target_heading: Optional[float] = None
    emergency_stop: bool = False

class VehicleControlSystem:
    """
    Interfaces with the telemetry sim.
    """
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.is_emergency_mode = False
        self._command_queue = asyncio.Queue()
        self.running = True
        
    async def start(self):
        """
        Start the control system loop.
        """
        logger.info("Starting vehicle control system")
        self.running = True
        
        while self.running:
            try:
                command = await self._command_queue.get()
                await self._process_command(command)
                self._command_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                continue
    
    async def _process_command(self, command: ControlCommand):
        """
        Process a single control command.
        """
        logger.info(f"Processing command: {command}")
        
        # Handle emergency stop
        if command.emergency_stop:
            await self._activate_emergency_mode()
            return
            
        # Don't process other commands in emergency mode
        if self.is_emergency_mode:
            logger.warning("Command rejected: Emergency mode active")
            return
            
        # Update vehicle parameters
        if command.target_altitude is not None:
            self.simulator.set_target_altitude(command.target_altitude)
            
        if command.target_speed is not None:
            self.simulator.set_target_speed(command.target_speed)
            
        if command.target_heading is not None:
            self.simulator.set_heading(command.target_heading)
    
    async def _activate_emergency_mode(self):
        """
        Activate emergency stop.
        """
        logger.warning("EMERGENCY MODE ACTIVATED")
        self.is_emergency_mode = True
        
        # Emergency landing sequence
        self.simulator.set_target_speed(0)
        await asyncio.sleep(0.5)  # Brief pause
        self.simulator.set_target_altitude(0)
    
    def clear_emergency_mode(self):
        """
        Clear emergency mode if safe.
        """
        if not self.is_emergency_mode:
            return False
        
        if self.simulator.current_state['altitude'] <= 1.0 and \
           self.simulator.current_state['speed'] <= 0.1:
            self.is_emergency_mode = False
            logger.info("Emergency mode cleared")
            return True
        return False
    
    async def send_command(self, command: ControlCommand):

        await self._command_queue.put(command)
    
    def execute_takeoff_sequence(self, target_altitude: float = 300.0):

        if not self.is_emergency_mode:
            asyncio.create_task(self._takeoff_sequence(target_altitude))
    
    async def _takeoff_sequence(self, target_altitude: float):

        logger.info("Initiating takeoff sequence")
        
        # Initial vertical climb
        await self.send_command(ControlCommand(
            target_altitude=50.0,
            target_speed=5.0
        ))
        await asyncio.sleep(5)
        
        # Accelerate and climb to target altitude
        await self.send_command(ControlCommand(
            target_altitude=target_altitude,
            target_speed=20.0
        ))
    
    def execute_landing_sequence(self):

        if not self.is_emergency_mode:
            asyncio.create_task(self._landing_sequence())
    
    async def _landing_sequence(self):

        logger.info("Initiating landing sequence")
        
        # Reduce speed and begin descent
        await self.send_command(ControlCommand(
            target_speed=10.0
        ))
        await asyncio.sleep(2)
        
        # Final approach
        await self.send_command(ControlCommand(
            target_altitude=50.0,
            target_speed=5.0
        ))
        await asyncio.sleep(5)
        
        # Touchdown
        await self.send_command(ControlCommand(
            target_altitude=0.0,
            target_speed=2.0
        ))