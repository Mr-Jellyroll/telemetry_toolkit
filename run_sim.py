import asyncio
import webbrowser
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.visualization.dashboard import TelemetryDashboard
from telemetry_toolkit.simulator.control import VehicleControlSystem

def main():

    simulator = TelemetrySimulator(
        update_interval=0.5,
        noise_factor=0.05,
        initial_altitude=100.0,
        initial_speed=0.0,
        initial_battery=100.0,
        initial_position=(32.7157, -117.1611)  # San Diego coordinates
    )
    
    dashboard = TelemetryDashboard(simulator)
    control_system = VehicleControlSystem(simulator)
    
    # Start simulator in a separate thread
    import threading
    
    def run_simulator():
        asyncio.run(simulator.start_simulation())
    
    def run_control_system():
        asyncio.run(control_system.start())
    
    # Create and start threads
    simulator_thread = threading.Thread(target=run_simulator)
    control_thread = threading.Thread(target=run_control_system)
    
    simulator_thread.daemon = True
    control_thread.daemon = True
    
    simulator_thread.start()
    control_thread.start()
    
    import time
    time.sleep(2)
    
    # Open the browser
    webbrowser.open('http://127.0.0.1:8050/')
    
    print("\nDashboard is now running!")
    print("You can view it in your web browser at: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the program")
    
    # Start the dashboard
    dashboard.run(debug=False, port=8050)

if __name__ == "__main__":
    main()