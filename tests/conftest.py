import pytest
from telemetry_toolkit.simulator.generator import TelemetrySimulator

@pytest.fixture
def simulator():
    """
    Provides a clean simulator instance for each test.

    """
    sim = TelemetrySimulator(
        update_interval=0.1,  # Fast updates for testing
        noise_factor=0.0,     # No noise for predictable tests
        initial_altitude=100.0,
        initial_speed=0.0,
        initial_battery=100.0,
        initial_position=(0.0, 0.0)  # Start at prime meridian for easy calculations
    )
    return sim

@pytest.fixture
def running_simulator(simulator):
    """
    Provides a simulator that's already running.

    """
    import asyncio
    
    async def setup_running_simulator():
        task = asyncio.create_task(simulator.start_simulation())
        await asyncio.sleep(0.2)  # Let it generate some initial data
        return simulator, task
    
    sim, task = asyncio.run(setup_running_simulator())
    yield sim
    
    # Cleanup after the test
    sim.stop_simulation()
    asyncio.run(task)