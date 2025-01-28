import pytest
import pytest_asyncio
import asyncio
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.simulator.control import VehicleControlSystem

@pytest.fixture
def simulator():

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

    task = asyncio.create_task(simulator.start_simulation())
    await asyncio.sleep(0.2)  # Allow simulator to initialize
    
    try:
        yield simulator
    finally:
        simulator.stop_simulation()
        await asyncio.sleep(0.1)  # Allow cleanup time
        await task

@pytest_asyncio.fixture
async def control_system(simulator):

    cs = VehicleControlSystem(simulator)
    return cs

@pytest_asyncio.fixture
async def running_control_system(control_system):

    task = asyncio.create_task(control_system.start())
    await asyncio.sleep(0.2)  # Allow control system to initialize
    
    try:
        yield control_system
    finally:
        control_system.running = False
        await asyncio.sleep(0.1)  # Allow cleanup time
        await task

@pytest.fixture(autouse=True)
async def cleanup_tasks():

    yield
    # Clean up any pending tasks
    tasks = [t for t in asyncio.all_tasks() 
             if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass