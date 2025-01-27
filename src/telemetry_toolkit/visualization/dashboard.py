import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import numpy as np

class TelemetryDashboard:
    """
    An interactive dashboard.
    """
    
    def __init__(self, simulator, update_interval_ms=1000):
        """
        Args:
            simulator: Instance of TelemetrySimulator that provides our data
            update_interval_ms: How often to update the display (in milliseconds)
        """
        self.simulator = simulator
        self.update_interval = update_interval_ms
        
        # Initialize the Dash application
        self.app = Dash(__name__)
        
        # Create the dashboard layout
        self._setup_layout()
        
        # Set up the callback functions that update our plots
        self._setup_callbacks()
    
    def _setup_layout(self):
        """
        Visual layout of dashboard.
        """
        self.app.layout = html.Div([
            # Dashboard title and header section
            html.Div([
                html.H1('Vehicle Telemetry Dashboard',
                        className='text-center mb-4'),
                html.P('Real-time monitoring and analysis of vehicle telemetry data',
                       className='text-center text-muted mb-4')
            ], className='container mt-4'),
            
            # Main content area
            html.Div([
                # Row 1: Key metrics and status
                html.Div([
                    # Vehicle altitude and speed
                    html.Div([
                        dcc.Graph(id='altitude-speed-chart')
                    ], className='col-md-8'),
                    
                    # Battery status
                    html.Div([
                        dcc.Graph(id='battery-gauge')
                    ], className='col-md-4')
                ], className='row mb-4'),
                
                # Row 2: Environmental data and position
                html.Div([
                    # Environmental sensors
                    html.Div([
                        dcc.Graph(id='environmental-chart')
                    ], className='col-md-6'),
                    
                    # Position tracking
                    html.Div([
                        dcc.Graph(id='position-map')
                    ], className='col-md-6')
                ], className='row mb-4')
            ], className='container-fluid'),
            
            # Hidden div for storing intermediate data
            html.Div(id='telemetry-store', style={'display': 'none'}),
            
            # Update interval
            dcc.Interval(
                id='update-timer',
                interval=self.update_interval,
                n_intervals=0
            )
        ])
    
    def _setup_callbacks(self):
        """
        Configure new data.
        """
        @self.app.callback(
            [Output('altitude-speed-chart', 'figure'),
             Output('battery-gauge', 'figure'),
             Output('environmental-chart', 'figure'),
             Output('position-map', 'figure')],
            [Input('update-timer', 'n_intervals')]
        )
        def update_dashboard(_):
            # Get the latest telemetry data
            if not self.simulator.data_buffer:
                return self._create_empty_figures()
            
            # Convert recent data points to a pandas DataFrame for easier handling
            df = pd.DataFrame([vars(d) for d in self.simulator.data_buffer[-100:]])
            
            # Update all visualizations with new data
            altitude_speed_fig = self._create_altitude_speed_chart(df)
            battery_fig = self._create_battery_gauge(df)
            environmental_fig = self._create_environmental_chart(df)
            position_fig = self._create_position_map(df)
            
            return altitude_speed_fig, battery_fig, environmental_fig, position_fig
    
    def _create_altitude_speed_chart(self, df):
        """
        Dual-axis chart showing altitude and speed over time.
        """
        fig = go.Figure()
        
        # Add altitude line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['altitude'],
            name='Altitude (m)',
            line=dict(color='blue')
        ))
        
        # Add speed line on secondary axis
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['speed'],
            name='Speed (m/s)',
            line=dict(color='red'),
            yaxis='y2'
        ))
        
        # Configure layout with dual axes
        fig.update_layout(
            title='Altitude and Speed Over Time',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Altitude (m)', side='left'),
            yaxis2=dict(title='Speed (m/s)', side='right', overlaying='y'),
            height=400
        )
        
        return fig
    
    def _create_battery_gauge(self, df):
        """
        Current battery levl.
        """
        current_battery = df['battery_level'].iloc[-1]
        
        return go.Figure(go.Indicator(
            mode='gauge+number',
            value=current_battery,
            title={'text': 'Battery Level'},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': self._get_battery_color(current_battery)},
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(255, 0, 0, 0.2)'},
                    {'range': [20, 60], 'color': 'rgba(255, 255, 0, 0.2)'},
                    {'range': [60, 100], 'color': 'rgba(0, 255, 0, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 20
                }
            }
        ))
    
    def _create_environmental_chart(self, df):
        """
        Sensor readings.
        """
        fig = go.Figure()
        
        # Extract sensor readings into separate columns
        latest_readings = pd.json_normalize(df['sensor_readings'].iloc[-1])
        
        for sensor, value in latest_readings.items():
            fig.add_trace(go.Indicator(
                mode='number+delta',
                value=value.iloc[0],
                title={'text': sensor.capitalize()},
                domain={'row': 0, 'column': len(fig.data)}
            ))
        
        fig.update_layout(
            title='Environmental Sensors',
            grid={'rows': 1, 'columns': len(latest_readings.columns)},
            height=300
        )
        
        return fig
    
    def _create_position_map(self, df):
        """
        Map showing the AV's current position and recent path.
        """
        return px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            title='Vehicle Position',
            zoom=13,
            height=400
        ).update_layout(
            mapbox_style='open-street-map',
            margin={'r': 0, 't': 30, 'l': 0, 'b': 0}
        )
    
    def _create_empty_figures(self):
        """
        Placeholders when no data available.
        """
        empty_fig = go.Figure().update_layout(
            title='Waiting for telemetry data...',
            height=400
        )
        return [empty_fig] * 4
    
    @staticmethod
    def _get_battery_color(level):

        if level <= 20:
            return 'red'
        elif level <= 60:
            return 'yellow'
        else:
            return 'green'
    
    def run(self, debug=False, port=8050):
        """
        Start dashboard server.
        """
        self.app.run_server(debug=debug, port=port)