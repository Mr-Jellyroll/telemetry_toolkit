from datetime import datetime
from telemetry_toolkit.simulator.data import TelemetryData

def test_telemetry_data_creation():
    """
    Verifies telemetry data.
    """
    data = TelemetryData(
        timestamp=datetime.now(),
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        latitude=37.7749,
        longitude=-122.4194,
        sensor_readings={'temperature': 20.0, 'pressure': 101.325}
    )
    
    assert isinstance(data.timestamp, datetime)
    assert data.altitude == 100.0
    assert data.speed == 50.0
    assert data.battery_level == 75.0
    assert data.latitude == 37.7749
    assert data.longitude == -122.4194
    assert 'temperature' in data.sensor_readings
    assert 'pressure' in data.sensor_readings

def test_telemetry_data_validation():

    # Create valid data
    valid_data = TelemetryData(
        timestamp=datetime.now(),
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        latitude=37.7749,
        longitude=-122.4194,
        sensor_readings={'temperature': 20.0}
    )
    assert valid_data.validate() is True

    # Test invalid altitude (negative)
    invalid_altitude = TelemetryData(
        timestamp=datetime.now(),
        altitude=-10.0,
        speed=50.0,
        battery_level=75.0,
        latitude=37.7749,
        longitude=-122.4194,
        sensor_readings={'temperature': 20.0}
    )
    assert invalid_altitude.validate() is False

def test_telemetry_data_to_dict():

    timestamp = datetime.now()
    original_data = TelemetryData(
        timestamp=timestamp,
        altitude=100.0,
        speed=50.0,
        battery_level=75.0,
        latitude=37.7749,
        longitude=-122.4194,
        sensor_readings={'temperature': 20.0}
    )
    
    dict_data = original_data.to_dict()
    
    assert isinstance(dict_data, dict)
    assert dict_data['timestamp'] == timestamp.isoformat()
    assert dict_data['altitude'] == 100.0
    assert dict_data['speed'] == 50.0
    assert dict_data['battery_level'] == 75.0
    assert dict_data['latitude'] == 37.7749
    assert dict_data['longitude'] == -122.4194
    assert dict_data['sensor_readings']['temperature'] == 20.0