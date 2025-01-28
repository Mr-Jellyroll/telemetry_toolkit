# src/telemetry_toolkit/visualization/dashboard.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import asyncio
import numpy as np
from .components.control_panel import VehicleControlPanel
from ..simulator.control import ControlCommand

class TelemetryDashboard:
    def __init__(self, simulator, control_system, update_interval_ms=1000):
        """Initialize the dashboard with simulator and control system."""
        self.simulator = simulator
        self.control_system = control_system
        self.update_interval = update_interval_ms
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Set up the dashboard layout with controls and visualizations."""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1('AV Telemetry Dashboard',
                        className='text-center mb-4'),
                html.P('Real-time monitoring and control of AV telemetry data',
                       className='text-center text-muted mb-4')
            ], className='container mt-4'),
            
            # Main content
            html.Div([
                # First row: Controls and 3D visualization
                html.Div([
                    html.Div([
                        VehicleControlPanel().create_layout()
                    ], className='col-md-4'),
                    html.Div([
                        dcc.Graph(id='flight-path-3d')
                    ], className='col-md-8')
                ], className='row mb-4'),
                
                # Second row: Performance metrics and map
                html.Div([
                    html.Div([
                        dcc.Graph(id='telemetry-plot', className='mb-4'),
                    ], className='col-md-6'),
                    html.Div([
                        dcc.Graph(id='position-map', className='mb-4'),
                    ], className='col-md-6')
                ], className='row'),

                # Status Display
                html.Div([
                    html.Div(id='status-display', className='text-center p-3 bg-light')
                ], className='row mb-4'),
                
                # Hidden div for storing state
                html.Div(id='control-state', style={'display': 'none'}),
                
                # Update interval
                dcc.Interval(
                    id='update-timer',
                    interval=self.update_interval,
                    n_intervals=0
                )
            ], className='container-fluid')
        ])
    
    def _setup_callbacks(self):
        """Set up all the dashboard callbacks."""
        
        @self.app.callback(
            [Output('control-state', 'children'),
             Output('status-display', 'children')],
            [Input('vehicle-control-altitude', 'value'),
             Input('vehicle-control-speed', 'value'),
             Input('vehicle-control-heading', 'value'),
             Input('vehicle-control-takeoff', 'n_clicks'),
             Input('vehicle-control-land', 'n_clicks'),
             Input('vehicle-control-emergency', 'n_clicks')],
            [State('control-state', 'children')]
        )
        def handle_control_inputs(altitude, speed, heading, takeoff_clicks, 
                                land_clicks, emergency_clicks, current_state):
            """Handle control panel inputs."""
            if not ctx.triggered:
                raise PreventUpdate
                
            trigger_id = ctx.triggered_id
            status_message = "Ready"
            
            try:
                if trigger_id == 'vehicle-control-emergency':
                    self.simulator.set_target_speed(0.0)
                    self.simulator.set_target_altitude(0.0)
                    status_message = "EMERGENCY STOP ACTIVATED"
                    
                elif trigger_id == 'vehicle-control-takeoff':
                    self.simulator.set_target_altitude(300.0)
                    self.simulator.set_target_speed(20.0)
                    status_message = "Executing takeoff sequence"
                    
                elif trigger_id == 'vehicle-control-land':
                    self.simulator.set_target_speed(5.0)
                    self.simulator.set_target_altitude(0.0)
                    status_message = "Executing landing sequence"
                    
                else:
                    # Handle slider updates
                    if altitude is not None:
                        self.simulator.set_target_altitude(float(altitude))
                        status_message = f"Adjusting altitude to {altitude}m"
                        
                    if speed is not None:
                        self.simulator.set_target_speed(float(speed))
                        status_message = f"Adjusting speed to {speed}m/s"
                        
                    if heading is not None:
                        self.simulator.set_heading(float(heading))
                        # Convert heading to cardinal direction
                        cardinal = self._heading_to_cardinal(heading)
                        status_message = f"Turning to heading {heading}° ({cardinal})"
                    
            except Exception as e:
                print(f"Error handling control input: {e}")
                status_message = f"Error: {str(e)}"
            
            status_html = html.Div([
                html.H4("Vehicle Status"),
                html.P(status_message),
                html.Div([
                    html.Span(f"Current Altitude: {self.simulator.current_state['altitude']:.1f}m | "),
                    html.Span(f"Speed: {self.simulator.current_state['speed']:.1f}m/s | "),
                    html.Span(f"Heading: {self.simulator.heading:.1f}° ({self._heading_to_cardinal(self.simulator.heading)})")
                ])
            ])
            
            return "updated", status_html

        @self.app.callback(
            [Output('flight-path-3d', 'figure'),
             Output('telemetry-plot', 'figure'),
             Output('position-map', 'figure')],
            [Input('update-timer', 'n_intervals')]
        )
        def update_visualizations(n):
            """Update all visualization components."""
            if not self.simulator.data_buffer:
                return {}, {}, {}
            
            df = pd.DataFrame([vars(d) for d in self.simulator.data_buffer[-100:]])
            
            return (
                self._create_3d_flight_path(df),
                self._create_telemetry_plot(df),
                self._create_position_map(df)
            )
    
    def _heading_to_cardinal(self, heading):
        """Convert heading in degrees to cardinal direction."""
        cardinals = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = round(((heading % 360) / 45)) % 8
        return cardinals[idx]
    
    def _create_3d_flight_path(self, df):
        """Create 3D visualization of flight path."""
        # Calculate heading vectors for visualization
        heading_len = 0.001  # Length of heading indicator
        current_pos = df.iloc[-1]
        heading_rad = np.radians(self.simulator.heading)
        dx = heading_len * np.sin(heading_rad)
        dy = heading_len * np.cos(heading_rad)
        
        fig = go.Figure()
        
        # Add flight path
        fig.add_trace(go.Scatter3d(
            x=df['longitude'],
            y=df['latitude'],
            z=df['altitude'],
            mode='lines+markers',
            name='Flight Path',
            marker=dict(
                size=2,
                color=df.index,
                colorscale='Viridis',
            ),
            line=dict(
                color='darkblue',
                width=2
            )
        ))
        
        # Add heading indicator
        fig.add_trace(go.Scatter3d(
            x=[current_pos['longitude'], current_pos['longitude'] + dx],
            y=[current_pos['latitude'], current_pos['latitude'] + dy],
            z=[current_pos['altitude'], current_pos['altitude']],
            mode='lines',
            name='Heading',
            line=dict(
                color='red',
                width=4
            )
        ))
        
        fig.update_layout(
            title='3D Flight Path',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Altitude (m)'
            ),
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig
    
    def _create_telemetry_plot(self, df):
        """Create telemetry visualization."""
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['altitude'],
                name='Altitude',
                line=dict(color='blue')
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['speed'],
                name='Speed',
                line=dict(color='red')
            ),
            secondary_y=True
        )
        
        # Add heading trace
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=[self.simulator.heading] * len(df),
                name='Heading',
                line=dict(color='green', dash='dash')
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title='Vehicle Telemetry',
            xaxis_title='Time',
            height=400,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        fig.update_yaxes(title_text="Altitude (m)", secondary_y=False)
        fig.update_yaxes(title_text="Speed (m/s) / Heading (°)", secondary_y=True)
        
        return fig
    
    def _create_position_map(self, df):
        """Create map showing current position and path."""
        # Calculate heading vector for current position
        current_pos = df.iloc[-1]
        heading_rad = np.radians(self.simulator.heading)
        arrow_length = 0.001  # Length of the heading arrow
        
        # Create the main path trace
        fig = go.Figure()
        
        # Add the flight path
        fig.add_trace(go.Scattermapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            mode='lines+markers',
            marker=dict(size=6),
            line=dict(width=2),
            name='Flight Path'
        ))
        
        # Add heading indicator arrow
        fig.add_trace(go.Scattermapbox(
            lat=[current_pos['latitude'], 
                 current_pos['latitude'] + arrow_length * np.cos(heading_rad)],
            lon=[current_pos['longitude'], 
                 current_pos['longitude'] + arrow_length * np.sin(heading_rad)],
            mode='lines',
            line=dict(width=3, color='red'),
            name='Heading'
        ))
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(
                    lat=df['latitude'].mean(),
                    lon=df['longitude'].mean()
                ),
                zoom=13
            ),
            title='Vehicle Position',
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True
        )
        
        return fig
    
    def run(self, debug=False, port=8050):
        """Run the dashboard server."""
        self.app.run_server(debug=debug, port=port)