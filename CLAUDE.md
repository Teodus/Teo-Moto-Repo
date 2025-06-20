# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid motorcycle powertrain simulation project designed to help understand trade-offs between power, weight, electric range, petrol range, and riding cycle impact. The project targets CEOs and engineers who want to experiment with innovative motorcycle powertrain designs through an interactive Google Colab interface.

## Development Environment

### Setup Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Code formatting (when needed)
black .
```

### Key Dependencies
- **Core**: numpy, pandas, scipy, matplotlib
- **Notebooks**: jupyter, ipywidgets (for interactive components)
- **GPS Processing**: gpxpy, geopy
- **Development**: black (for code formatting)

## Architecture Overview

### Core Simulation Framework
- **`motorbike.py`**: Top-level motorcycle class that orchestrates all components
- **`trajectory.py`**: Handles GPX/JSON track loading and processing for simulation routes
- **`components/`**: Physical component implementations (engines, motors, brakes, gearbox)
- **`energy_sources/`**: Energy storage systems (chemical fuel tanks, electrical batteries)
- **`energy_sinks/`**: Energy consumption models (drag, rolling resistance, gravity, inertia)
- **`efficiency_definitions/`**: Performance curves for components (constant, RPM-dependent)

### Component Library System
- **`component_library/`**: User-friendly component creation and selection system
- **`component_specs.py`**: Standardized database of realistic component specifications
- **`interactive_picker.py`**: Colab widget utilities for component selection
- **Custom builders**: Generic component builders (engines.py, motors.py, batteries.py, fuel_systems.py)

### Energy Flow Model
1. Energy sources (fuel/battery) provide power with capacity constraints
2. Components (engines/motors) convert energy with efficiency losses
3. Energy sinks (aerodynamic drag, rolling resistance, gravity) consume power
4. Physics simulation calculates achievable speeds and energy consumption over time

## Component Hierarchy

All components inherit from abstract base classes:
- **`AbstractComponent`**: Base class for all physical components
- **`AbstractElectricalComponent`**: Electrical system components
- **`AbstractMechanicalComponent`**: Mechanical system components
- **`AbstractEnergySink`**: Energy consumption components
- **`AbstractEnergySource`**: Energy storage components

## Testing Strategy

**Current**: Manual testing through Jupyter notebooks
- **Integration tests**: `notebooks/component_library_integration_test.ipynb`
- **Basic functionality**: `notebooks/file_import_test.ipynb`
- **Simple trajectories**: `notebooks/straight_line_test.ipynb`

**No formal testing framework** is currently implemented. Tests are validated manually through notebook execution and visual verification.

## Key Notebooks

### Primary User Interface
- **`notebooks/ithaka_master_notebook.ipynb`**: Clean CEO-ready interface for complete simulations
- **`notebooks/interactive_component_picker.ipynb`**: Interactive widget-based component selection

### Development and Testing
- **`notebooks/component_library_demo.ipynb`**: Showcases generic component capabilities
- **`notebooks/component_library_integration_test.ipynb`**: Validates component library integration

## Adding New Components

### Preset Components
1. Add specifications to `component_library/component_specs.py`
2. Create builder function in appropriate module (engines.py, motors.py, etc.)
3. Update `__init__.py` exports
4. Test integration in component_library_integration_test.ipynb

### Interactive Widgets
1. Add widget creation function in `component_library/interactive_picker.py`
2. Integrate with main notebook interface
3. Ensure real-time validation and feedback

## Data Files

### GPS Tracks
- **`docs/gpx_files/`**: Real-world GPS tracks for simulation (various terrain types)
- **`docs/json_files/`**: Track data in JSON format for faster processing

### Track Processing
- Supports both GPX and JSON formats
- Automatic elevation and distance calculations
- Physics-based energy demand calculations for each trajectory segment

## Design Principles

- **Physics-based validation**: All component parameters must be within realistic engineering bounds
- **Educational focus**: Tool teaches powertrain engineering principles through interactive experimentation
- **Zero modification policy**: New features are added without modifying existing codebase
- **Colab compatibility**: All notebooks work in both local and Google Colab environments
- **No session persistence**: Users copy/paste configurations between sessions

## Performance Considerations

- Component creation is optimized for real-time interaction (< 100ms updates)
- Large trajectory files may require progress indicators for future optimizations
- GPU acceleration available in Colab for computationally intensive simulations

## Code Style

- Follow existing patterns in abstract base classes
- Use descriptive quantitative naming (Engine_650cc_50kW vs brand names)
- Maintain backward compatibility with existing simulation code
- Format code with `black` when making significant changes