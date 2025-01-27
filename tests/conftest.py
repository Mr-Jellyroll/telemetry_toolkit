import pytest
from telemetry_toolkit.simulator.generator import TelemetrySimulator

@pytest.fixture
def simulator():
    """
    Clean sim instance for each test.
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

@pytest.fixture
async def running_simulator(simulator):
    """
    A sim that's already running.
    """
    import asyncio
    
    task = asyncio.create_task(simulator.start_simulation())
    await asyncio.sleep(0.2)
    
    yield simulator
    
    # Cleanup
    simulator.stop_simulation()
    await task