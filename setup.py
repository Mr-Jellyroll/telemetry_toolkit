from setuptools import setup, find_packages

setup(
    name="telemetry_toolkit",
    version="0.2.0",
    description="A toolkit for real-time telemetry visualization and analysis",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "plotly>=5.3.0",
        "dash>=2.0.0",
        "aiohttp>=3.8.0",
        "pydantic>=1.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=0.940",
            "pre-commit>=2.17.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.18.0",
        ],
    },
    package_data={
        "telemetry_toolkit": [
            "visualization/components/*.jsx",
            "visualization/static/*",
        ]
    },
    include_package_data=True,
)