import asyncio
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.visualization.dashboard import TelemetryDashboard
import webbrowser
import time

def main():
    # Create our simulator
    simulator = TelemetrySimulator(
        update_interval=0.5,
        noise_factor=0.05,
        initial_altitude=100.0,
        initial_speed=0.0
    )
    
    # Create our dashboard
    dashboard = TelemetryDashboard(simulator)
    
    # Start the simulation in a separate thread
    import threading
    simulation_thread = threading.Thread(
        target=lambda: asyncio.run(simulator.start_simulation())
    )
    simulation_thread.daemon = True
    simulation_thread.start()

    # Give the server a moment to start
    time.sleep(2)
    
    # Open the browser
    webbrowser.open('http://127.0.0.1:8050/')
    
    # Run the dashboard
    dashboard.run(debug=False, port=8050)

if __name__ == "__main__":
    main()