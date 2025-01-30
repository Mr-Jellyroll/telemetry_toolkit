# Telemetry Toolkit

A Python toolkit for real-time telemetry visualization. Dashboard shows simulated vehicle system with live data monitoring and control capabilities.

## Features

- Real-time telemetry data sim
- Dashboard for monitoring and control
- 3D flight path visualization
- Live performance metrics
- Position tracking with map integration

## Requirements

- Python 3.11+
- Dependencies listed in `pyproject.toml`/`setup.py`

## Installation

1. Clone the repo and you can install the package directly from PyPI:
```bash
pip install telemetry_toolkit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install package and deps:
```bash
pip install -e .
```

For dev, install additional deps:
```bash
pip install -e ".[dev]"
```

## Usage

### Running the Sim

To start the telemetry dash:

```bash
python run_sim.py
```

This will:
- Initialize the telemetry sim
- Start the control system
- Launch a web browser with the dashboard
