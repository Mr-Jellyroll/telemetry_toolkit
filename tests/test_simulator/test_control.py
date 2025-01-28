import pytest
import asyncio
from telemetry_toolkit.simulator.control import ControlCommand

@pytest.mark.asyncio
async def test_control_command_creation():
    """
    Control commands with different params.
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
    Test E stop start and stop.
    """
    # Set initial conditions
    await running_control_system.send_command(ControlCommand(
        target_altitude=200.0,
        target_speed=20.0
    ))
    await asyncio.sleep(0.2)
    
    assert running_simulator.target_altitude == 200.0
    assert running_simulator.target_speed == 20.0
    
    command = ControlCommand(emergency_stop=True)
    await running_control_system.send_command(command)
    
    await asyncio.sleep(0.3)
    
    assert running_control_system.is_emergency_mode
    assert running_simulator.target_speed == 0.0, "Speed should be set to 0 in emergency"
    assert running_simulator.target_altitude == 0.0, "Altitude should be set to 0 in emergency"
    
    await running_control_system.send_command(ControlCommand(
        target_altitude=100.0,
        target_speed=10.0
    ))
    await asyncio.sleep(0.2)
    
    assert running_control_system.is_emergency_mode, "Emergency mode should persist"
    assert running_simulator.target_speed == 0.0, "Speed should remain 0 in emergency"
    assert running_simulator.target_altitude == 0.0, "Altitude should remain 0 in emergency"
@pytest.mark.asyncio
async def test_command_processing(running_simulator, running_control_system):
    """
    Normal commands.
    """
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

    running_control_system.execute_takeoff_sequence(target_altitude=300.0)
    
    await asyncio.sleep(0.5)
    
    assert running_simulator.target_altitude > 0.0
    assert running_simulator.target_speed > 0.0

@pytest.mark.asyncio
async def test_landing_sequence(running_simulator, running_control_system):

    running_simulator.current_state['altitude'] = 200.0
    

    running_control_system.execute_landing_sequence()
    

    await asyncio.sleep(0.5)
    
    assert running_simulator.target_altitude == 0.0
    assert running_simulator.target_speed <= 10.0

@pytest.mark.asyncio
async def test_emergency_stop_blocks_commands(running_simulator, running_control_system):

    # Activate emergency mode
    await running_control_system.send_command(ControlCommand(emergency_stop=True))
    await asyncio.sleep(0.2)
    
    # Try to send a normal command
    await running_control_system.send_command(ControlCommand(
        target_altitude=500.0,
        target_speed=30.0
    ))
    await asyncio.sleep(0.2)
    
    # Verify command was blocked
    assert running_simulator.target_altitude == 0.0
    assert running_simulator.target_speed == 0.0