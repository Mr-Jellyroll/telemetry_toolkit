import pytest
import asyncio
from telemetry_toolkit.simulator.control import VehicleControlSystem, ControlCommand

@pytest.mark.asyncio
async def test_control_command_creation():
    """
    Test creating control commands with different parameters.
    """
    command = ControlCommand(
        target_altitude=100.0,
        target_speed=20.0,
        target_heading=45.0
    )
    assert command.target_altitude == 100.0
    assert command.target_speed == 20.0
    assert command.target_heading == 45.0
    assert not command.emergency_stop

@pytest.mark.asyncio
async def test_emergency_mode(running_simulator, running_control_system):
    """
    Test E stop on and off.
    """
    # Test E stop
    command = ControlCommand(emergency_stop=True)
    await running_control_system.send_command(command)
    
    await asyncio.sleep(0.2)
    
    # Check E mode
    assert running_control_system.is_emergency_mode
    
    # Verify AV params in emergency
    await asyncio.sleep(0.2)  # Allow simu to update
    assert running_simulator.current_state['speed'] == 0.0
    assert running_simulator.target_altitude == 0.0

@pytest.mark.asyncio
async def test_command_processing(running_simulator, running_control_system):
    """Test normal command processing."""
    # Send a normal command
    command = ControlCommand(
        target_altitude=200.0,
        target_speed=15.0,
        target_heading=90.0
    )
    await running_control_system.send_command(command)
    
    await asyncio.sleep(0.2)
    
    # Verify sim received the commands
    assert running_simulator.target_altitude == 200.0
    assert running_simulator.target_speed == 15.0
    assert running_simulator.heading == 90.0


@pytest.mark.asyncio
async def test_takeoff_sequence(running_simulator, running_control_system):
    """Test the automated takeoff sequence."""
    # Start takeoff
    running_control_system.execute_takeoff_sequence(target_altitude=300.0)
    
    await asyncio.sleep(0.5)
    
    # Verify climb
    assert running_simulator.target_altitude > 0.0
    assert running_simulator.target_speed > 0.0

@pytest.mark.asyncio
async def test_landing_sequence(running_simulator, running_control_system):
    """Test the automated landing sequence."""
    # Set initial altitude
    running_simulator.current_state['altitude'] = 200.0
    
    # Start landing
    running_control_system.execute_landing_sequence()
    
    await asyncio.sleep(0.5)
    
    # Verify descent
    assert running_simulator.target_altitude == 0.0
    assert running_simulator.target_speed <= 10.0  # Slow for landing