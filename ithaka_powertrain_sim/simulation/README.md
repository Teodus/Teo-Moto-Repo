# Simulation Module Documentation

## Overview

The `simulation` module provides improved track data processing, speed calculations, and simulation orchestration for the Ithaka Powertrain Simulator.

## Key Components

### TrackProcessor
Handles consistent filtering and validation of GPS track data:
- Filters stopped sections below configurable minimum speed (default: 10 km/h)
- Validates and bounds speeds to realistic values (0-300 km/h)
- Provides detailed processing statistics and warnings

### SpeedCalculator
Offers multiple methods for calculating speeds and efficiency:
- **distance_time**: Traditional average speed (total distance / total time)
- **mean_speeds**: Arithmetic mean of instantaneous speeds
- **weighted**: Time-weighted average of speeds
- Energy efficiency analysis by speed ranges

### SimulationRunner
Orchestrates the complete simulation workflow:
- Loads and processes track data with consistent parameters
- Runs physics simulation with proper error handling
- Calculates comprehensive metrics and statistics
- Supports batch simulations across multiple tracks

## Quick Start

```python
from ithaka_powertrain_sim.simulation import SimulationRunner

# Create runner with desired parameters
runner = SimulationRunner(
    min_speed_kmh=10.0,
    max_speed_kmh=300.0,
    use_filter=True,
    speed_calculation_method='distance_time'
)

# Run single track simulation
result = runner.simulate_motorcycle_on_track(
    motorcycle, 
    'path/to/track.gpx',
    'Track Name'
)

# Run batch simulations
tracks = [('Track 1', 'track1.gpx'), ('Track 2', 'track2.gpx')]
results = runner.run_batch_simulations(motorcycle, tracks)
```

## Configuration Options

- **min_speed_kmh**: Minimum speed to consider as moving (filters stops)
- **max_speed_kmh**: Maximum realistic motorcycle speed
- **use_filter**: Whether to filter stopped sections
- **speed_calculation_method**: How to calculate average speed

## Output Metrics

Each simulation provides:
- Total distance and time
- Average, maximum, and minimum speeds
- Energy consumption and efficiency
- Data quality metrics and warnings
- Processing statistics