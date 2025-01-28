from dash import html, dcc
import dash_bootstrap_components as dbc

class VehicleControlPanel:
    def __init__(self):
        self.id_prefix = "vehicle-control"
    
    def create_layout(self):
        return html.Div([
            html.H3("Vehicle Controls", className="mb-4"),
            
            # Altitude Control
            html.Div([
                html.Label("Target Altitude (m)"),
                dcc.Slider(
                    id=f"{self.id_prefix}-altitude",
                    min=0,
                    max=1000,
                    step=10,
                    value=100,
                    marks={0: '0m', 500: '500m', 1000: '1000m'},
                ),
            ], className="mb-4"),
            
            # Speed Control
            html.Div([
                html.Label("Target Speed (m/s)"),
                dcc.Slider(
                    id=f"{self.id_prefix}-speed",
                    min=0,
                    max=50,
                    step=1,
                    value=0,
                    marks={0: '0m/s', 25: '25m/s', 50: '50m/s'},
                ),
            ], className="mb-4"),
            
            # Heading Control
            html.Div([
                html.Label("Heading (degrees)"),
                dcc.Slider(
                    id=f"{self.id_prefix}-heading",
                    min=0,
                    max=359,
                    step=5,
                    value=0,
                    marks={
                        0: 'N',
                        90: 'E',
                        180: 'S',
                        270: 'W',
                        360: 'N'
                    },
                ),
            ], className="mb-4"),
            
            # Quick Action Buttons
            html.Div([
                dbc.Button(
                    "Takeoff",
                    id=f"{self.id_prefix}-takeoff",
                    color="primary",
                    className="me-2"
                ),
                dbc.Button(
                    "Land",
                    id=f"{self.id_prefix}-land",
                    color="info",
                    className="me-2"
                ),
                dbc.Button(
                    "Emergency Stop",
                    id=f"{self.id_prefix}-emergency",
                    color="danger",
                )
            ], className="d-grid gap-2")
        ], className="p-4 border rounded")