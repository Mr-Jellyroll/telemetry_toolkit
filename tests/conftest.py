import pytest
import pytest_asyncio
from telemetry_toolkit.simulator.generator import TelemetrySimulator

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
    import asyncio
    
    # Start the sim
    task = asyncio.create_task(simulator.start_simulation())
    
    # Generate some data
    await asyncio.sleep(0.2)
    
    try:
        yield simulator
    finally:
        # Cleanup
        simulator.stop_simulation()
        try:
            await task
        except asyncio.CancelledError:
            pass