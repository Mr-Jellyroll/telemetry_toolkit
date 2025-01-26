from dataclasses import dataclass
from datetime import datetime
from typing import Dict

@dataclass
class TelemetryData:
    """
    Represents a single telemetry data point.
    
        timestamp: The exact time when this data point was recorded
        altitude: Current altitude in meters above sea level
        speed: Current speed in meters per second
        battery_level: Remaining battery charge as a percentage (0-100)
        sensor_readings: Dictionary containing various sensor measurements
    """
    timestamp: datetime
    altitude: float
    speed: float
    battery_level: float
    sensor_readings: Dict[str, float]
    
    def validate(self) -> bool:
        """
        Validates data fields.
        
        Returns:
            bool: True if all values are within expected ranges
        """
        try:
            # Check basic range validations
            validations = [
                self.altitude >= 0,  # Altitude can't be negative
                self.speed >= 0,     # Speed can't be negative
                0 <= self.battery_level <= 100,  # Battery must be 0-100%
                # Ensure all sensor readings are numeric
                all(isinstance(v, (int, float)) for v in self.sensor_readings.values())
            ]
            
            return all(validations)
            
        except (TypeError, ValueError):
            return False
    
    def to_dict(self) -> Dict:
        """
        Converts the telemetry data to a dictionary format.
        
        Returns:
            Dict: Dictionary of the telemetry data
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'altitude': float(self.altitude),
            'speed': float(self.speed),
            'battery_level': float(self.battery_level),
            'sensor_readings': dict(self.sensor_readings)
        }