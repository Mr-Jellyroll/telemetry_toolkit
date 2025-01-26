import asyncio
from telemetry_toolkit.simulator.generator import TelemetrySimulator

async def main():
    # Create a simulator with 0.5 second updates and 5% noise
    simulator = TelemetrySimulator(
        update_interval=0.5,
        noise_factor=0.05,
        initial_altitude=100.0,
        initial_speed=0.0
    )
    
    # Start the simulation in the background
    simulation_task = asyncio.create_task(simulator.start_simulation())
    
    try:
        # Simulate a simple flight pattern
        await asyncio.sleep(2)  # Wait 2 seconds at initial position
        
        # Command the vehicle to climb to 500 meters
        print("Climbing to 500 meters...")
        simulator.set_target_altitude(500.0)
        await asyncio.sleep(5)
        
        # Start moving forward
        print("Accelerating to 30 m/s...")
        simulator.set_target_speed(30.0)
        await asyncio.sleep(5)
        
        # Turn to a new heading
        print("Turning to heading 45 degrees...")
        simulator.set_heading(45.0)
        await asyncio.sleep(5)
        
        # Begin descent
        print("Beginning descent...")
        simulator.set_target_altitude(100.0)
        await asyncio.sleep(5)
        
        # Slow down and stop
        print("Slowing down...")
        simulator.set_target_speed(0.0)
        await asyncio.sleep(5)
        
    finally:
        # Clean up
        simulator.stop_simulation()
        await simulation_task
        
        # Print the final buffer of data points
        print("\nFinal telemetry data:")
        for data_point in simulator.data_buffer[-5:]:  # Last 5 points
            print(f"Time: {data_point.timestamp}")
            print(f"Altitude: {data_point.altitude:.1f} m")
            print(f"Speed: {data_point.speed:.1f} m/s")
            print(f"Battery: {data_point.battery_level:.1f}%")
            print(f"Sensor Readings: {data_point.sensor_readings}")
            print("---")

if __name__ == "__main__":
    asyncio.run(main())