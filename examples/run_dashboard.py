import asyncio
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.visualization.dashboard import TelemetryDashboard
from telemetry_toolkit.simulator.control import VehicleControlSystem
import webbrowser
import time
import threading

def main():
    # Create our simulator starting in downtown SD
    simulator = TelemetrySimulator(
        update_interval=0.5,
        noise_factor=0.05,
        initial_altitude=100.0,
        initial_speed=0.0,
        initial_battery=100.0,
        initial_position=(32.7157, -117.1611)  # San Diego coordinates
    )
    
    # Create the dashboard
    dashboard = TelemetryDashboard(simulator)
    
    # Run the simulation in a separate thread
    import threading

    def run_simulator():
        asyncio.run(simulator.start_simulation())
    
    def run_control_system():
        asyncio.run(dashboard.control_system.start())
    
    simulator_thread = threading.Thread(target=run_simulator)
    control_thread = threading.Thread(target=run_control_system)
    
    simulator_thread.daemon = True
    control_thread.daemon = True
    
    simulator_thread.start()
    control_thread.start()
    
    # Start the dashboard
    dashboard.run(debug=False, port=8050)
    
    async def flight_pattern():

        await asyncio.sleep(2)  # Wait for systems to initialize

        print("Taking off from downtown San Diego...")
        simulator.set_target_altitude(300.0) 
        simulator.set_target_speed(20.0)
        await asyncio.sleep(5)
        
        print("Flying to Balboa Park...")
        simulator.set_heading(45.0)
        await asyncio.sleep(8)
        
        print("Circling Balboa Park...")
        for heading in range(0, 360, 45):
            simulator.set_heading(float(heading))
            await asyncio.sleep(3)
            
        print("Moving to the USS Midway")
        simulator.set_heading(270.0)
        await asyncio.sleep(6)
        
        print("Flying over Coronado Bridge...")
        simulator.set_heading(225.0)
        simulator.set_target_altitude(200.0)
        await asyncio.sleep(8)
        
        print("Heading to Point Loma...")
        simulator.set_heading(315.0)  # Northwest
        simulator.set_target_altitude(250.0)
        await asyncio.sleep(10)

        print("Returning to downtown San Diego...")
        simulator.set_heading(90.0)  # East
        simulator.set_target_speed(15.0)  # Slowing down
        await asyncio.sleep(8)
        
        print("Beginning final approach...")
        simulator.set_target_altitude(100.0)
        simulator.set_target_speed(5.0)
        await asyncio.sleep(5)
        
        print("Landing...")
        simulator.set_target_altitude(0.0)
        simulator.set_target_speed(0.0)
        
    # Create and run the simulation task
    simulation_thread = threading.Thread(
        target=lambda: asyncio.run(simulator.start_simulation())
    )
    simulation_thread.daemon = True
    simulation_thread.start()
    
    # Create and run the flight pattern task
    flight_pattern_thread = threading.Thread(
        target=lambda: asyncio.run(flight_pattern())
    )
    flight_pattern_thread.daemon = True
    flight_pattern_thread.start()
    
    time.sleep(2)
    
    # Open the browser to show the dashboard
    webbrowser.open('http://127.0.0.1:8050/')
    
    print("\nDashboard is now running. You can view it in your web browser.")
    print("Watch as the vehicle tours San Diego's landmarks!")
    print("Press Ctrl+C to stop the program when you're done.")
    
    # Start the dashboard
    dashboard.run(debug=False, port=8050)

if __name__ == "__main__":
    main()