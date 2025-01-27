import asyncio
import logging
from datetime import datetime
import numpy as np
from typing import Dict, List, Optional
from dataclasses import asdict

from .data import TelemetryData

# Set up logging to help us track what's happening in our simulator
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelemetrySimulator:
    """
    Simulates realistic telemetry data from an AV.
    """
    
    def __init__(
        self,
        update_interval: float = 1.0,
        noise_factor: float = 0.1,
        initial_altitude: float = 100.0,
        initial_speed: float = 0.0,
        initial_battery: float = 100.0,
        initial_position: tuple[float, float] = (37.7749, -122.4194)  # San Francisco
    ):
        """
        Initialize the simulator with starting conditions.
        
        Args:
            update_interval: Seconds between data updates (like a sensor sampling rate)
            noise_factor: Amount of random noise to add (0.1 = 10% variation)
            initial_altitude: Starting height in meters
            initial_speed: Starting velocity in meters/second
            initial_battery: Starting battery percentage
            initial_position: Starting (latitude, longitude)
        """
        # Store configuration parameters
        self.update_interval = update_interval
        self.noise_factor = noise_factor
        
        # Initialize current state
        self.current_state = {
            'altitude': initial_altitude,
            'speed': initial_speed,
            'battery_level': initial_battery,
            'latitude': initial_position[0],
            'longitude': initial_position[1]
        }
        
        # Parameters for realistic movement
        self.target_altitude: Optional[float] = None
        self.altitude_change_rate = 0.0  # meters per second
        self.target_speed: Optional[float] = None
        self.acceleration = 0.0  # meters per second squared
        self.battery_drain_rate = -0.05  # percent per second
        self.heading = 0.0  # degrees from north
        
        # Operational state
        self.running = False
        self.data_buffer: List[TelemetryData] = []
        
        logger.info("Telemetry simulator initialized with conditions: %s", 
                   str(self.current_state))

    def _add_noise(self, value: float) -> float:
        """
        Add realistic noise to a measurement.
        """
        noise = np.random.normal(0, abs(value) * self.noise_factor)
        return value + noise

    def _update_movement(self):
        """
        Update position and movement parameters.
        """
        # Update altitude if we have a target
        if self.target_altitude is not None:
            altitude_diff = self.target_altitude - self.current_state['altitude']
            if abs(altitude_diff) < 1.0:
                self.target_altitude = None
            else:
                self.altitude_change_rate = np.clip(altitude_diff / 10.0, -10.0, 10.0)
        
        # Update speed if we have a target
        if self.target_speed is not None:
            speed_diff = self.target_speed - self.current_state['speed']
            if abs(speed_diff) < 0.1:
                self.target_speed = None
            else:
                self.acceleration = np.clip(speed_diff / 5.0, -2.0, 2.0)

        # Apply movement changes
        self.current_state['altitude'] += self.altitude_change_rate * self.update_interval
        self.current_state['speed'] += self.acceleration * self.update_interval
        
        # Update position based on speed and heading
        if self.current_state['speed'] > 0:
            # Convert speed from m/s to degrees of latitude/longitude
            speed_deg = self.current_state['speed'] * 0.00001  # approximate conversion
            
            # Update position based on heading
            heading_rad = np.radians(self.heading)
            self.current_state['latitude'] += speed_deg * np.cos(heading_rad)
            self.current_state['longitude'] += speed_deg * np.sin(heading_rad)

    def _update_battery(self):
        """
        Update battery level based on movement.
        """
        # Start with base battery drain
        drain = self.battery_drain_rate
        
        # Add drain from movement
        drain -= abs(self.acceleration) * 0.01  # More drain during acceleration
        drain -= abs(self.altitude_change_rate) * 0.005  # More drain during climbs
        
        self.current_state['battery_level'] += drain * self.update_interval
        self.current_state['battery_level'] = np.clip(
            self.current_state['battery_level'], 0.0, 100.0
        )

    def _generate_sensor_readings(self) -> Dict[str, float]:
        """
        Generate realistic sensor readings based on current state.
        """
        # Temperature calculation (using standard lapse rate)
        base_temp = 25.0  # ground level temperature in Celsius
        altitude_temp_effect = self.current_state['altitude'] * -0.0065
        temperature = base_temp + altitude_temp_effect
        
        # Pressure calculation (barometric formula)
        base_pressure = 101.325  # sea level pressure in kPa
        pressure = base_pressure * np.exp(-self.current_state['altitude'] / 8400)
        
        # Humidity varies within realistic bounds
        humidity = 60.0 + self._add_noise(0) * 5
        humidity = np.clip(humidity, 0.0, 100.0)
        
        return {
            'temperature': self._add_noise(temperature),
            'pressure': self._add_noise(pressure),
            'humidity': humidity,
            'vibration': self._add_noise(self.current_state['speed'] * 0.1)
        }

    async def generate_data(self) -> TelemetryData:
        """
        1. Updates vehicle movement
        2. Updates battery status
        3. Generates sensor readings
        4. Packages everything into a TelemetryData object
        
        Returns:
            TelemetryData: A new telemetry data point
        """
        # Update vehicle state
        self._update_movement()
        self._update_battery()
        
        # Create telemetry data point
        data = TelemetryData(
            timestamp=datetime.now(),
            altitude=self._add_noise(self.current_state['altitude']),
            speed=self._add_noise(self.current_state['speed']),
            battery_level=self.current_state['battery_level'],
            latitude=self.current_state['latitude'],
            longitude=self.current_state['longitude'],
            sensor_readings=self._generate_sensor_readings()
        )
        
        logger.debug("Generated telemetry data: %s", asdict(data))
        return data

    def set_target_altitude(self, altitude: float):
        """Set a new target altitude for the vehicle."""
        self.target_altitude = max(0.0, altitude)
        logger.info("New target altitude set: %.1f meters", self.target_altitude)

    def set_target_speed(self, speed: float):
        """Set a new target speed for the vehicle."""
        self.target_speed = max(0.0, speed)
        logger.info("New target speed set: %.1f m/s", self.target_speed)

    def set_heading(self, heading: float):
        """Set a new heading for the vehicle (degrees from north)."""
        self.heading = heading % 360.0
        logger.info("New heading set: %.1f degrees", self.heading)

    async def start_simulation(self):
        """
        Start the telemetry sim.
        """
        logger.info("Starting telemetry simulation")
        self.running = True
        
        while self.running:
            try:
                data = await self.generate_data()
                self.data_buffer.append(data)
                
                # Keep a reasonable buffer size
                if len(self.data_buffer) > 1000:
                    self.data_buffer.pop(0)
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error("Error in simulation loop: %s", str(e))
                continue

    def stop_simulation(self):
        """Stop the telemetry simulation."""
        logger.info("Stopping telemetry simulation")
        self.running = False