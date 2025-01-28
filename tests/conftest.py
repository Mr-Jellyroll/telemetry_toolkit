import pytest
import pytest_asyncio
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.simulator.control import VehicleControlSystem

@pytest.fixture
def simulator():
    """
    Clean simulator instance for each test.
    """
    sim = TelemetrySimulator(
        update_interval=0.1,
        noise_factor=0.0,
        initial_altitude=100.0,
        initial_speed=0.0,
        initial_battery=100.0,
        initial_position=(0.0, 0.0)
    )
    return sim

@pytest_asyncio.fixture
async def running_simulator(simulator):
    """
    Provides a sim that's already running.
    """
    task = asyncio.create_task(simulator.start_simulation())
    await asyncio.sleep(0.2)  # Allow simulator to initialize
    
    try:
        yield simulator
    finally:
        simulator.stop_simulation()
        await task

@pytest.fixture
def control_system(simulator):
    """
    Clean VehicleControlSystem instance for testing.
    """
    cs = VehicleControlSystem(simulator)
    return cs

@pytest_asyncio.fixture
async def running_control_system(control_system):
    """
    Running control system.
    """
    task = asyncio.create_task(control_system.start())
    await asyncio.sleep(0.2)  # Initialize
    
    try:
        yield control_system
    finally:
        control_system.running = False
        await task