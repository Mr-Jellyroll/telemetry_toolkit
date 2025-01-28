# src/telemetry_toolkit/visualization/dashboard.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from .components.control_panel import VehicleControlPanel

class TelemetryDashboard:
    def __init__(self, simulator, update_interval_ms=1000):
        self.simulator = simulator
        self.update_interval = update_interval_ms
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        self.app.layout = html.Div([
            html.H1('Telemetry Dashboard'),
            
            # Controls
            VehicleControlPanel().create_layout(),
            
            # Plots
            html.Div([
                dcc.Graph(id='telemetry-plot'),
                dcc.Graph(id='position-map')
            ]),
            
            # Update timer
            dcc.Interval(
                id='interval-component',
                interval=self.update_interval,
                n_intervals=0
            )
        ])
    
    def _setup_callbacks(self):
        @self.app.callback(
            [Output('telemetry-plot', 'figure'),
             Output('position-map', 'figure')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_graphs(n):
            if not self.simulator.data_buffer:
                return {}, {}
            
            df = pd.DataFrame([vars(d) for d in self.simulator.data_buffer[-100:]])
            
            # Create telemetry plot
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig1.add_trace(
                go.Scatter(x=df.index, y=df['altitude'], name="Altitude"),
                secondary_y=False,
            )
            
            fig1.add_trace(
                go.Scatter(x=df.index, y=df['speed'], name="Speed"),
                secondary_y=True,
            )
            
            # Create map
            fig2 = px.scatter_mapbox(
                df,
                lat='latitude',
                lon='longitude',
                zoom=13
            )
            
            fig2.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
            
            return fig1, fig2
    
    def run(self, debug=False, port=8050):
        self.app.run_server(debug=debug, port=port)