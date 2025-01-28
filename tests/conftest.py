import pytest
import pytest_asyncio
import asyncio
import logging
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.simulator.control import VehicleControlSystem

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

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
        logger.debug("Stopping simulator")
        simulator.stop_simulation()
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning("Simulator task timeout - forcing cancellation")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

@pytest_asyncio.fixture
async def control_system(simulator):

    cs = VehicleControlSystem(simulator)
    yield cs

@pytest_asyncio.fixture
async def running_control_system(control_system):

    task = asyncio.create_task(control_system.start())
    await asyncio.sleep(0.2)  # Allow control system to initialize
    
    try:
        yield control_system
    finally:
        logger.debug("Stopping control system")
        control_system.running = False
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning("Control system task timeout - forcing cancellation")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

@pytest.fixture(autouse=True)
async def cleanup_tasks():
    """Clean up any pending tasks after each test."""
    yield
    
    # Get all tasks except the current one
    pending = [t for t in asyncio.all_tasks() 
              if not t.done() and t is not asyncio.current_task()]
    
    if pending:
        logger.debug(f"Cleaning up {len(pending)} pending tasks")
        # Cancel all pending tasks
        for task in pending:
            task.cancel()
        
        # Wait for all tasks to complete with timeout
        try:
            await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), 
                                 timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning("Task cleanup timeout - some tasks may remain")