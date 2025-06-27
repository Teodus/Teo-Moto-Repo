# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid motorcycle powertrain simulation project designed to help understand trade-offs between power, weight, electric range, petrol range, and riding cycle impact. The project targets CEOs and engineers who want to experiment with innovative motorcycle powertrain designs through an interactive Google Colab interface.

## Development Environment

### Package Installation

This project uses setuptools for package management:

```bash
# Install in development mode (recommended)
pip install -e .

# Or install from requirements only
pip install -r requirements.txt

# Code formatting (when needed)
black .
```

**Note**: The `shortuuid` dependency may need manual installation in some environments.

### Key Dependencies
- **Core**: numpy, pandas, scipy, matplotlib
- **Notebooks**: jupyter, ipywidgets (critical for Colab interface)
- **GPS Processing**: gpxpy, geopy
- **Utilities**: shortuuid, setuptools
- **Development**: black[jupyter] (for code formatting)

### Local Development Setup

```bash
# Using direnv (optional)
echo "use python" > .envrc
direnv allow

# Standard setup
pip install -r requirements.txt
pip install -e .
```

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

### Core Inheritance Architecture

```python
AbstractComponent (Base)
├── AbstractElectricalComponent (shared_abstract_classes/)
├── AbstractMechanicalComponent (shared_abstract_classes/)
└── Motorbike (multiple inheritance from both)
```

All components inherit from abstract base classes:
- **`AbstractComponent`**: Base class for all physical components
- **`AbstractElectricalComponent`**: Electrical system components
- **`AbstractMechanicalComponent`**: Mechanical system components
- **`AbstractEnergySink`**: Energy consumption components
- **`AbstractEnergySource`**: Energy storage components

### Package Structure
- **Root package**: `ithaka_powertrain_sim/` (installable via setup.py)
- **Component library**: Factory pattern with specifications database
- **Interactive system**: ipywidgets-based interface for Google Colab

## Testing Strategy

**Current Approach**: Manual testing through interactive notebooks
- **Primary validation**: `ithaka_master_notebook.ipynb` end-to-end workflow
- **Component testing**: `custom_build_motorcycles.ipynb`
- **Physics validation**: `straight_line_test.ipynb`
- **Basic functionality**: `file_import_test.ipynb`

**No formal test framework** - all validation through notebook execution.
**Empty `tests/` directory** - reserved for future unit tests.

## Key Notebooks

### Primary User Interface

**Main Interface**: `notebooks/ithaka_master_notebook.ipynb`
- Complete CEO-ready workflow with 5-step process
- Automatic environment detection (Colab vs local)
- Self-healing repository setup with fallback URLs
- Interactive component selection with real-time validation

### Development and Testing
- **`custom_build_motorcycles.ipynb`**: Component library testing and custom builds
- **`prebuilt_motorcycles.ipynb`**: Predefined motorcycle showcase
- **`file_import_test.ipynb`**: Basic trajectory loading tests
- **`straight_line_test.ipynb`**: Simple physics validation

### Google Colab Integration

The master notebook includes sophisticated auto-setup:
- Detects Colab vs local environment
- Auto-clones repository with fallback URLs
- Validates all dependencies and provides diagnostics
- Handles common installation issues (shortuuid, etc.)

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