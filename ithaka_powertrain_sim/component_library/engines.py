"""
Generic engine component builders for hybrid motorcycle powertrain simulation.

This module provides factory functions to create combustion engine components
with realistic efficiency curves and specifications based on displacement and power.
"""

from typing import Collection

from ithaka_powertrain_sim.components import CombustionEngine
from ithaka_powertrain_sim.energy_sources import ChemicalSource
from ithaka_powertrain_sim.efficiency_definitions import AngularVelocityEfficiency
from .component_specs import ENGINE_SPECS


def _create_engine_efficiency_curve(
    rpm_max: int,
    efficiency_peak: float,
    rpm_peak_efficiency: int
) -> AngularVelocityEfficiency:
    """
    Create a realistic efficiency curve for an internal combustion engine.
    
    Parameters
    ----------
    rpm_max : int
        Maximum RPM of the engine
    efficiency_peak : float
        Peak efficiency ratio (0-1)
    rpm_peak_efficiency : int
        RPM at which peak efficiency occurs
        
    Returns
    -------
    AngularVelocityEfficiency
        Engine efficiency definition with realistic curve
    """
    # Create RPM points across the engine's operating range
    rpm_points = [
        0,
        rpm_max * 0.1,
        rpm_max * 0.2,
        rpm_max * 0.3,
        rpm_max * 0.4,
        rpm_max * 0.5,
        rpm_max * 0.6,
        rpm_max * 0.7,
        rpm_max * 0.8,
        rpm_max * 0.9,
        rpm_max
    ]
    
    # Convert to rad/s (RPM * 2π / 60)
    angular_velocity_points = [rpm * 2 * 3.14159 / 60 for rpm in rpm_points]
    
    # Create efficiency curve - low at idle, peak in middle, drops at redline
    efficiency_ratios = [
        efficiency_peak * 0.15,  # Very low at idle
        efficiency_peak * 0.25,  # Low at low RPM
        efficiency_peak * 0.40,  # Building up
        efficiency_peak * 0.65,  # Getting better
        efficiency_peak * 0.85,  # Near peak
        efficiency_peak * 0.95,  # Close to peak
        efficiency_peak * 1.00,  # Peak efficiency
        efficiency_peak * 0.90,  # Dropping off
        efficiency_peak * 0.75,  # Higher RPM losses
        efficiency_peak * 0.60,  # Near redline
        efficiency_peak * 0.45   # At redline
    ]
    
    return AngularVelocityEfficiency(angular_velocity_points, efficiency_ratios)


def _create_engine_with_fuel_tank(
    engine_key: str,
    fuel_capacity_L: float = 15.0,
    allow_refueling: bool = True
) -> CombustionEngine:
    """
    Create a combustion engine with integrated fuel tank.
    
    Parameters
    ----------
    engine_key : str
        Key from ENGINE_SPECS dictionary
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 15.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    specs = ENGINE_SPECS[engine_key]
    
    # Gasoline properties
    fuel_density_kg_per_L = 0.75
    energy_density_MJ_per_kg = 43.0
    
    fuel_tank = ChemicalSource(
        name=f"Fuel Tank {fuel_capacity_L}L",
        energy_density=energy_density_MJ_per_kg * 1e6,  # Convert to J/kg
        dry_mass=2.0 + fuel_capacity_L * 0.2,  # Tank weight + mounting
        initial_fuel_mass=fuel_capacity_L * fuel_density_kg_per_L,
        allow_negative_fuel=False,
        allow_refueling=allow_refueling,
    )
    
    efficiency_curve = _create_engine_efficiency_curve(
        specs["rpm_max"],
        specs["efficiency_peak"],
        specs["rpm_peak_efficiency"]
    )
    
    engine = CombustionEngine(
        name=f"Engine {specs['displacement_cc']}cc {specs['max_power_kW']}kW",
        dry_mass=specs["dry_mass_kg"],
        efficiency_definition=efficiency_curve,
        child_components=(fuel_tank,),
        minimum_power_generation=0.0,
        maximum_power_generation=specs["max_power_kW"] * 1e3,  # Convert to watts
    )
    
    return engine


def Engine_250cc_20kW(fuel_capacity_L: float = 12.0, allow_refueling: bool = True) -> CombustionEngine:
    """
    Create a 250cc, 20kW single cylinder engine.
    
    Parameters
    ----------
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 12.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    return _create_engine_with_fuel_tank("250cc_20kW", fuel_capacity_L, allow_refueling)


def Engine_400cc_30kW(fuel_capacity_L: float = 15.0, allow_refueling: bool = True) -> CombustionEngine:
    """
    Create a 400cc, 30kW single cylinder engine.
    
    Parameters
    ----------
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 15.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    return _create_engine_with_fuel_tank("400cc_30kW", fuel_capacity_L, allow_refueling)


def Engine_500cc_40kW(fuel_capacity_L: float = 18.0, allow_refueling: bool = True) -> CombustionEngine:
    """
    Create a 500cc, 40kW single cylinder engine.
    
    Parameters
    ----------
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 18.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    return _create_engine_with_fuel_tank("500cc_40kW", fuel_capacity_L, allow_refueling)


def Engine_650cc_50kW(fuel_capacity_L: float = 20.0, allow_refueling: bool = True) -> CombustionEngine:
    """
    Create a 650cc, 50kW twin cylinder engine.
    
    Parameters
    ----------
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 20.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    return _create_engine_with_fuel_tank("650cc_50kW", fuel_capacity_L, allow_refueling)


def Engine_750cc_60kW(fuel_capacity_L: float = 22.0, allow_refueling: bool = True) -> CombustionEngine:
    """
    Create a 750cc, 60kW twin cylinder engine.
    
    Parameters
    ----------
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 22.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    return _create_engine_with_fuel_tank("750cc_60kW", fuel_capacity_L, allow_refueling)


def Engine_1000cc_80kW(fuel_capacity_L: float = 25.0, allow_refueling: bool = True) -> CombustionEngine:
    """
    Create a 1000cc, 80kW four cylinder engine.
    
    Parameters
    ----------
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 25.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Complete engine component with fuel tank
    """
    return _create_engine_with_fuel_tank("1000cc_80kW", fuel_capacity_L, allow_refueling)