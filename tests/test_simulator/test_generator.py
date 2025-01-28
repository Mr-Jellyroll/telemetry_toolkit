import pytest
import asyncio
import numpy as np
from telemetry_toolkit.simulator.generator import TelemetrySimulator

pytestmark = pytest.mark.asyncio

async def test_initial_state(simulator):
    """
    Tests sim initializes with the correct starting values.
    """
    assert simulator.current_state['altitude'] == 100.0
    assert simulator.current_state['speed'] == 0.0
    assert simulator.current_state['battery_level'] == 100.0
    assert simulator.current_state['latitude'] == 0.0
    assert simulator.current_state['longitude'] == 0.0

async def test_data_generation(simulator):
    """
    Tests sim can generate valid telemetry data.
    """
    data = await simulator.generate_data()
    
    # Verify data point structure
    assert data.validate()
    assert data.altitude >= 0
    assert data.speed >= 0
    assert 0 <= data.battery_level <= 100
    
    # Verify sensor readings
    assert 'temperature' in data.sensor_readings
    assert 'pressure' in data.sensor_readings
    assert 'humidity' in data.sensor_readings
    assert 'vibration' in data.sensor_readings

async def test_altitude_changes(simulator):
    """
    Tests sim handles altitude changes.
    """
    # Set a target altitude
    target_altitude = 500.0
    simulator.set_target_altitude(target_altitude)
    
    # Generate data points
    initial_altitude = simulator.current_state['altitude']
    data_points = []
    for _ in range(10):
        data = await simulator.generate_data()
        data_points.append(data.altitude)
        await asyncio.sleep(0.1)
    
    # Verify altitude
    assert data_points[-1] > initial_altitude  # Should be climbing
    assert all(0 <= alt <= target_altitude for alt in data_points)  # Within bounds
    assert all(abs(data_points[i] - data_points[i-1]) <= 10.0 
              for i in range(1, len(data_points)))  # Rate limited

async def test_battery_drain(running_simulator):
    """
    Tests battery drains.
    """
    # Get initial battery level
    initial_battery = running_simulator.current_state['battery_level']
    
    # Run for a while with movement
    running_simulator.set_target_altitude(500.0)  # Climbing should drain more battery
    running_simulator.set_target_speed(30.0)      # Moving should drain battery
    
    await asyncio.sleep(1.0)
    
    # Get final battery level
    final_battery = running_simulator.current_state['battery_level']
    
    assert final_battery < initial_battery  # Battery should drain
    assert final_battery >= 0  # Battery shouldn't go negative

async def test_sensor_correlations(simulator):
    """
    Tests sensor readings correlate properly with vehicle state.
    """
    # Generate data at ground level
    ground_data = await simulator.generate_data()
    ground_temp = ground_data.sensor_readings['temperature']
    ground_pressure = ground_data.sensor_readings['pressure']
    
    # Move to high altitude
    simulator.current_state['altitude'] = 5000.0
    high_data = await simulator.generate_data()
    high_temp = high_data.sensor_readings['temperature']
    high_pressure = high_data.sensor_readings['pressure']
    

    assert high_temp < ground_temp  # Temperature should decrease with altitude
    assert high_pressure < ground_pressure  # Pressure should decrease with altitude

async def test_movement_physics(simulator):
    """
    Tests that the simulator respects basic physics.
    """

    target_speed = 50.0
    simulator.set_target_speed(target_speed)
    
    # Track acceleration
    speeds = []
    for _ in range(10):
        data = await simulator.generate_data()
        speeds.append(data.speed)
        await asyncio.sleep(0.1)
    
    # Verify acceleration behavior
    accelerations = [speeds[i] - speeds[i-1] for i in range(1, len(speeds))]
    max_acceleration = max(abs(acc) for acc in accelerations)
    
    # Check physical constraints
    assert max_acceleration <= 2.0  # Should not exceed max acceleration
    assert all(speed >= 0 for speed in speeds)  # Speed should never be negative
    assert speeds[-1] <= target_speed  # Should not exceed target speed

@pytest.mark.asyncio
async def test_data_buffer_management(running_simulator):
    """
    Tests to prevent memory issues.
    """
    # Generate lots of data points
    for _ in range(20):  # Iterations
        await asyncio.sleep(0.01)
    
    # Verify buffer size management
    assert len(running_simulator.data_buffer) <= 1000  # Should not exceed max size