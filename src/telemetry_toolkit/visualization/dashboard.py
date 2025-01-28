# src/telemetry_toolkit/visualization/dashboard.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import asyncio
import threading
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
                        dcc.Graph(id='performance-metrics')
                    ], className='col-md-6'),
                    html.Div([
                        dcc.Graph(id='position-map')
                    ], className='col-md-6')
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
            Output('control-state', 'children'),
            [Input('vehicle-control-altitude', 'value'),
             Input('vehicle-control-speed', 'value'),
             Input('vehicle-control-takeoff', 'n_clicks'),
             Input('vehicle-control-land', 'n_clicks'),
             Input('vehicle-control-emergency', 'n_clicks')],
            [State('control-state', 'children')]
        )
        def handle_control_inputs(altitude, speed, takeoff_clicks, land_clicks, emergency_clicks, current_state):
            """Handle control panel inputs."""
            if not ctx.triggered:
                raise PreventUpdate
                
            trigger_id = ctx.triggered_id
            
            try:
                if trigger_id == 'vehicle-control-emergency':
                    command = ControlCommand(emergency_stop=True)
                    # Handle emergency directly through simulator
                    self.simulator.set_target_speed(0.0)
                    self.simulator.set_target_altitude(0.0)
                    
                elif trigger_id == 'vehicle-control-takeoff':
                    # Handle takeoff directly through simulator
                    self.simulator.set_target_altitude(300.0)
                    self.simulator.set_target_speed(20.0)
                    
                elif trigger_id == 'vehicle-control-land':
                    # Handle landing directly through simulator
                    self.simulator.set_target_speed(5.0)
                    self.simulator.set_target_altitude(0.0)
                    
                else:
                    # Handle slider updates
                    if altitude is not None:
                        self.simulator.set_target_altitude(float(altitude))
                    if speed is not None:
                        self.simulator.set_target_speed(float(speed))
                    
            except Exception as e:
                print(f"Error handling control input: {e}")
            
            return "updated"

        @self.app.callback(
            [Output('flight-path-3d', 'figure'),
             Output('performance-metrics', 'figure'),
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
                self._create_performance_metrics(df),
                self._create_position_map(df)
            )
    
    def _create_3d_flight_path(self, df):
        """Create 3D visualization of flight path."""
        fig = go.Figure(data=[go.Scatter3d(
            x=df['longitude'],
            y=df['latitude'],
            z=df['altitude'],
            mode='lines+markers',
            marker=dict(
                size=2,
                color=df.index,
                colorscale='Viridis',
            ),
            line=dict(
                color='darkblue',
                width=2
            )
        )])
        
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
    
    def _create_performance_metrics(self, df):
        """Create performance metrics visualization."""
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
        
        fig.update_layout(
            title='Vehicle Performance',
            xaxis_title='Time',
            height=400,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        fig.update_yaxes(title_text="Altitude (m)", secondary_y=False)
        fig.update_yaxes(title_text="Speed (m/s)", secondary_y=True)
        
        return fig
    
    def _create_position_map(self, df):
        """Create map showing current position and path."""
        fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            title='Vehicle Position',
            zoom=13,
            height=400
        )
        
        fig.update_layout(
            mapbox_style='open-street-map',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig
    
    def run(self, debug=False, port=8050):
        """Run the dashboard server."""
        self.app.run_server(debug=debug, port=port)