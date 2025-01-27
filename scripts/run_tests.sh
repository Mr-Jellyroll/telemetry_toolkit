#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
echo "Running tests with coverage..."
pytest tests/ -v --cov=telemetry_toolkit --cov-report=html

# Generate coverage report
echo "Coverage report generated in htmlcov/index.html"

# Run tests with verbose output
echo "Running detailed test output..."
pytest tests/ -v