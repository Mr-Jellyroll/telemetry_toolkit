import asyncio
import threading
import webbrowser
import time
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.visualization.dashboard import TelemetryDashboard
from telemetry_toolkit.simulator.control import VehicleControlSystem

def main():
    # Create simulator with San Diego coordinates
    simulator = TelemetrySimulator(
        update_interval=0.5,
        noise_factor=0.05,
        initial_altitude=100.0,
        initial_speed=0.0,
        initial_battery=100.0,
        initial_position=(32.7157, -117.1611)  # San Diego coordinates
    )
    
    # Create control system
    control_system = VehicleControlSystem(simulator)
    
    # Create dashboard with both simulator and control system
    dashboard = TelemetryDashboard(
        simulator=simulator,
        control_system=control_system
    )
    
    # Create and initialize event loop for async operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Function to run simulator in the event loop
    def run_simulator():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(simulator.start_simulation())
    
    # Function to run control system in the event loop
    def run_control():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(control_system.start())
    
    # Create and start simulator thread
    simulator_thread = threading.Thread(target=run_simulator)
    simulator_thread.daemon = True
    simulator_thread.start()
    
    # Create and start control system thread
    control_thread = threading.Thread(target=run_control)
    control_thread.daemon = True
    control_thread.start()
    
    # Wait for threads to initialize
    time.sleep(2)
    
    # Open browser to display dashboard
    webbrowser.open('http://127.0.0.1:8050/')
    
    print("\nDashboard is now running!")
    print("You can view it in your web browser at: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the program")
    
    # Start the dashboard
    dashboard.run(debug=False, port=8050)

if __name__ == "__main__":
    main()