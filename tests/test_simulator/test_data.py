from datetime import datetime
import pytest
from telemetry_toolkit.simulator.data import TelemetryData

def test_telemetry_data_creation():
    """
    Verifies the basic initialization.
    """
    data = TelemetryData(
        timestamp=datetime.now(),
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        sensor_readings={'temperature': 20.0, 'pressure': 101.325}
    )
    
    assert isinstance(data.timestamp, datetime)
    assert data.altitude == 100.0
    assert data.speed == 50.0
    assert data.battery_level == 75.0
    assert 'temperature' in data.sensor_readings
    assert 'pressure' in data.sensor_readings

def test_telemetry_data_validation():
    """
    Ensures data constraints are working.
    """
    # Create valid data
    valid_data = TelemetryData(
        timestamp=datetime.now(),
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        sensor_readings={'temperature': 20.0}
    )
    assert valid_data.validate() is True
    
    # Test invalid altitude (negative)
    invalid_altitude = TelemetryData(
        timestamp=datetime.now(),
        altitude=-10.0,  # Invalid: negative altitude
        speed=50.0,
        battery_level=75.0,
        sensor_readings={'temperature': 20.0}
    )
    assert invalid_altitude.validate() is False
    
    # Test invalid battery level (over 100%)
    invalid_battery = TelemetryData(
        timestamp=datetime.now(),
        altitude=100.0,
        speed=50.0,
        battery_level=150.0,  # Invalid: over 100%
        sensor_readings={'temperature': 20.0}
    )
    assert invalid_battery.validate() is False
    
    # Test invalid sensor reading (non-numeric)
    invalid_sensor = TelemetryData(
        timestamp=datetime.now(),
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        sensor_readings={'temperature': 'warm'}  # Invalid: non-numeric
    )
    assert invalid_sensor.validate() is False

def test_telemetry_data_to_dict():
    """
    Tests data serialization works.
    """
    timestamp = datetime.now()
    original_data = TelemetryData(
        timestamp=timestamp,
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        sensor_readings={'temperature': 20.0}
    )
    
    dict_data = original_data.to_dict()
    
    # Verify dictionary structure
    assert isinstance(dict_data, dict)
    assert dict_data['timestamp'] == timestamp.isoformat()
    assert dict_data['altitude'] == 100.0
    assert dict_data['speed'] == 50.0
    assert dict_data['battery_level'] == 75.0
    assert dict_data['sensor_readings']['temperature'] == 20.0