import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import numpy as np

class TelemetryDashboard:

    def __init__(self, simulator, update_interval_ms=1000):
        """
        Initialize the dashboard
        """
        self.simulator = simulator
        self.update_interval = update_interval_ms
        self.app = Dash(__name__)
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """
        - Real-time status indicators
        - 3D flight path visualization
        - Performance metrics charts
        - Position tracking map
        """
        self.app.layout = html.Div([
            # Header section
            html.Div([
                html.H1('AV Telemetry Dashboard',
                        className='text-center mb-4'),
                html.P('Real-time monitoring of AV telemetry data',
                       className='text-center text-muted mb-4')
            ], className='container mt-4'),
            
            # Main content area
            html.Div([
                # First row: Status and 3D visualization
                html.Div([
                    html.Div([
                        dcc.Graph(id='status-display')
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
            ], className='container-fluid'),
            
            # Update timer for real-time updates
            dcc.Interval(
                id='update-timer',
                interval=self.update_interval,
                n_intervals=0
            )
        ])
    
    def _setup_callbacks(self):

        @self.app.callback(
            [Output('status-display', 'figure'),
             Output('flight-path-3d', 'figure'),
             Output('performance-metrics', 'figure'),
             Output('position-map', 'figure')],
            [Input('update-timer', 'n_intervals')]
        )
        def update_dashboard(_):
            if not self.simulator.data_buffer:
                return [go.Figure()] * 4
            
            # Convert recent data points to a DataFrame for easier handling
            df = pd.DataFrame([vars(d) for d in self.simulator.data_buffer[-100:]])
            
            return (
                self._create_status_indicators(df),
                self._create_3d_flight_path(df),
                self._create_performance_metrics(df),
                self._create_position_map(df)
            )
    
    def _create_status_indicators(self, df):
        """
        Key status indicators..
        """
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2] if len(df) > 1 else latest_data
        
        fig = go.Figure()
        
        # Add altitude indicator
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=latest_data['altitude'],
            delta={'reference': previous_data['altitude'],
                   'relative': True,
                   'position': "top"},
            title={'text': "Altitude (m)"},
            domain={'row': 0, 'column': 0}
        ))
        
        fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def _create_3d_flight_path(self, df):
        """
        3D visualization of flight path.
        """
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

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add altitude line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['altitude'],
                name='Altitude',
                line=dict(color='blue')
            ),
            secondary_y=False
        )
        
        # Add speed line on secondary axis
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
        
        # Update axis labels
        fig.update_yaxes(title_text="Altitude (m)", secondary_y=False)
        fig.update_yaxes(title_text="Speed (m/s)", secondary_y=True)
        
        return fig
    
    def _create_position_map(self, df):
        """
        Create a map showing current position and path.
        """
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
        """""
        Args:
            debug: Enable debug mode for development
            port: Port number to run the server on
        """
        self.app.run_server(debug=debug, port=port)