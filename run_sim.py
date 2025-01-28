import asyncio
import threading
import webbrowser
import time
from telemetry_toolkit.simulator.generator import TelemetrySimulator
from telemetry_toolkit.visualization.dashboard import TelemetryDashboard
from telemetry_toolkit.simulator.control import VehicleControlSystem

def main():
    # Create sim with SD coordinates
    simulator = TelemetrySimulator(
        update_interval=0.5,
        noise_factor=0.05,
        initial_altitude=100.0,
        initial_speed=0.0,
        initial_battery=100.0,
        initial_position=(32.7157, -117.1611)  # San Diego coordinates
    )
    
    # Control system
    control_system = VehicleControlSystem(simulator)
    
    loop = asyncio.new_event_loop()
    
    def run_async_components():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            asyncio.gather(
                simulator.start_simulation(),
                control_system.start()
            )
        )
    
    # Start sim and control system in background
    background_thread = threading.Thread(
        target=run_async_components,
        daemon=True
    )
    background_thread.start()
    
    dashboard = TelemetryDashboard(
        simulator=simulator,
        control_system=control_system
    )

    time.sleep(2)
    
    # Open browser to display dash
    webbrowser.open('http://127.0.0.1:8050/')
    
    print("\nDashboard is now running!")
    print("You can view it in your web browser at: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the program")
    
    try:
        # Start dash
        dashboard.run(debug=False, port=8050)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:

        simulator.stop_simulation()
        loop.stop()

if __name__ == "__main__":
    main()