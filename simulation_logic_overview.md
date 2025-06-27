# Simulation Logic Overview

This document describes where the core simulation logic is implemented in the motorcycle powertrain simulation codebase.

## Main Simulation Engine

### Primary Time-Stepping Loop
**Location**: `ithaka_powertrain_sim/motorbike.py:177-258`

**Method**: `calculate_achieved_speed()`

```python
def calculate_achieved_speed(
    self,
    current_speed: float,
    target_next_speed: float,
    delta_time: float,
    delta_distance: float,
    delta_elevation: float,
) -> tuple[float, pd.DataFrame]:
```

**Key Operations**:
- **Energy demand calculation** (Lines 204-210): Calculates total energy required for the timestep
- **Inertial energy calculation** (Lines 212-221): Separates inertial forces from other resistance forces  
- **Energy delivery resolution** (Lines 227-231): Determines what energy can actually be delivered by components
- **Speed integration** (Lines 251-256): Updates speed based on available vs required energy

## Physics Models and Mathematical Equations

### Energy Sink Implementations
These files contain the fundamental physics equations used in simulation:

#### Aerodynamic Drag
**Location**: `ithaka_powertrain_sim/energy_sinks/aerodynamic_drag_sink.py`
- **Equation**: `E = 0.5 * ρ * Cd * A * v² * distance`
- **Implementation**: Lines 33-40

#### Rolling Resistance
**Location**: `ithaka_powertrain_sim/energy_sinks/rolling_resistance_sink.py`
- **Equation**: `E = Cr * mass_ratio * mass * g * distance`

#### Gravitational Potential Energy
**Location**: `ithaka_powertrain_sim/energy_sinks/gravitational_sink.py`
- **Equation**: `E = m * g * Δh`

#### Linear Inertia
**Location**: `ithaka_powertrain_sim/energy_sinks/linear_inertia_sink.py`
- **Equation**: `KE = 0.5 * m * v²`

## Energy Resolution System

### Component Energy Delivery
**Location**: `ithaka_powertrain_sim/components/abstract_component.py:342-450`

**Method**: `calculate_energy_delivered()`

This implements an iterative solver that:
- Applies power limits based on component constraints (Lines 385-393)
- Accounts for efficiency losses (Lines 395-399) 
- Iteratively balances energy demand across multiple components (Lines 409-441)
- Resolves complex hybrid powertrain energy sharing

## Integration Algorithm

### Speed Calculation
**Location**: `ithaka_powertrain_sim/motorbike.py:260-308`

**Method**: `calculate_next_speed()`

```python
def calculate_next_speed(
    self,
    current_mass: float,
    current_speed: float,
    available_energy: float,
    demanded_energy: float,
) -> float:
```

**Integration Process**:
- Calculates kinetic energy coefficient for all inertial components (Lines 289-294)
- Applies energy balance: `Δ(KE) = available_energy` (Line 296)
- Solves for new speed: `v_new = √(v_current² + 2*ΔE/m)` (Lines 298-301)

## Simulation Execution Pattern

### Main Loop Structure
**Example Location**: `notebooks/straight_line_test.ipynb` (Cell ID: 79ffb16633d25899)

```python
for index in range(1, len(dataframe)):
    achieved_speed, reporting_dataframe_row = motorbike.calculate_achieved_speed(
        achieved_speeds[index - 1],
        target_speed[index],
        approximate_time[index] - approximate_time[index - 1],
        delta_distance[index],
        delta_elevation[index],
    )
    achieved_speeds.append(achieved_speed)
    # Update timing based on achieved vs target speeds
```

## Trajectory Processing and Data Preparation

### Track Data Processing
**Location**: `ithaka_powertrain_sim/trajectory.py`

**Key Functions**:
- **GPS data loading**: `load_gpx()` and `load_json()` functions
- **Trajectory resampling**: `append_and_resample_dataframe()` (Lines 11-108)
- **Speed calculation**: Uses gradient-based numerical differentiation (Lines 94-96)

## Simulation Architecture Summary

The simulation uses a **time-stepping approach** with the following workflow:

1. **Energy Demand Calculation**: Each timestep calculates energy demand from all physics models (drag, inertia, gravity, rolling resistance)

2. **Energy Resolution**: Components attempt to deliver the required energy subject to power and efficiency constraints

3. **Speed Integration**: Achieved speed is calculated based on energy balance using kinetic energy principles

4. **Time Progression**: The simulation advances to the next timestep and repeats

## Key Design Principles

- **Energy-based simulation** rather than force-based, making it well-suited for powertrain efficiency analysis
- **Iterative energy balance solver** that can distribute power demands across multiple energy sources
- Support for **complex hybrid powertrains** with different constraints and efficiencies
- **Physics-validated calculations** with realistic engineering constraints

The core mathematical foundation enables accurate analysis of energy consumption patterns across different riding scenarios and powertrain configurations.