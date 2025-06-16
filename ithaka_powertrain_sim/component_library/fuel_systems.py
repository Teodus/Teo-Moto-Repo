"""
Generic fuel tank component builders for hybrid motorcycle powertrain simulation.

This module provides factory functions to create fuel tank components
with realistic fuel properties and capacity specifications.
"""

from ithaka_powertrain_sim.energy_sources import ChemicalSource
from .component_specs import FUEL_TANK_SPECS


def _create_fuel_tank(
    tank_key: str,
    allow_refueling: bool = True,
    custom_capacity_L: float | None = None
) -> ChemicalSource:
    """
    Create a fuel tank component.
    
    Parameters
    ----------
    tank_key : str
        Key from FUEL_TANK_SPECS dictionary
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
    custom_capacity_L : float | None, optional
        Override the default capacity (default: None uses spec capacity)
        
    Returns
    -------
    ChemicalSource
        Complete fuel tank component
    """
    specs = FUEL_TANK_SPECS[tank_key]
    
    # Use custom capacity if provided, otherwise use spec
    capacity_L = custom_capacity_L if custom_capacity_L is not None else specs["capacity_liters"]
    
    # Scale tank mass proportionally
    scale_factor = capacity_L / specs["capacity_liters"]
    tank_dry_mass = specs["dry_mass_kg"] * scale_factor
    
    # Calculate fuel mass
    fuel_mass = capacity_L * specs["fuel_density_kg_per_L"]
    
    fuel_tank = ChemicalSource(
        name=f"Fuel Tank {capacity_L:.1f}L",
        energy_density=specs["energy_density_MJ_per_kg"] * 1e6,  # Convert MJ/kg to J/kg
        dry_mass=tank_dry_mass,
        initial_fuel_mass=fuel_mass,
        allow_negative_fuel=False,
        allow_refueling=allow_refueling,
    )
    
    return fuel_tank


def FuelTank_8L(allow_refueling: bool = True, custom_capacity_L: float | None = None) -> ChemicalSource:
    """
    Create an 8L fuel tank.
    
    Parameters
    ----------
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
    custom_capacity_L : float | None, optional
        Override the default 8L capacity (default: None)
        
    Returns
    -------
    ChemicalSource
        8L fuel tank component
    """
    return _create_fuel_tank("8L", allow_refueling, custom_capacity_L)


def FuelTank_15L(allow_refueling: bool = True, custom_capacity_L: float | None = None) -> ChemicalSource:
    """
    Create a 15L fuel tank.
    
    Parameters
    ----------
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
    custom_capacity_L : float | None, optional
        Override the default 15L capacity (default: None)
        
    Returns
    -------
    ChemicalSource
        15L fuel tank component
    """
    return _create_fuel_tank("15L", allow_refueling, custom_capacity_L)


def FuelTank_25L(allow_refueling: bool = True, custom_capacity_L: float | None = None) -> ChemicalSource:
    """
    Create a 25L fuel tank.
    
    Parameters
    ----------
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
    custom_capacity_L : float | None, optional
        Override the default 25L capacity (default: None)
        
    Returns
    -------
    ChemicalSource
        25L fuel tank component
    """
    return _create_fuel_tank("25L", allow_refueling, custom_capacity_L)


def FuelTank_Custom(
    capacity_L: float,
    fuel_density_kg_per_L: float = 0.75,
    energy_density_MJ_per_kg: float = 43.0,
    tank_mass_per_liter: float = 0.35,
    allow_refueling: bool = True
) -> ChemicalSource:
    """
    Create a custom fuel tank with specified parameters.
    
    Parameters
    ----------
    capacity_L : float
        Fuel tank capacity in liters
    fuel_density_kg_per_L : float, optional
        Fuel density in kg/L (default: 0.75 for gasoline)
    energy_density_MJ_per_kg : float, optional
        Energy density in MJ/kg (default: 43.0 for gasoline)
    tank_mass_per_liter : float, optional
        Tank dry mass per liter of capacity (default: 0.35 kg/L)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    ChemicalSource
        Custom fuel tank component
    """
    tank_dry_mass = capacity_L * tank_mass_per_liter
    fuel_mass = capacity_L * fuel_density_kg_per_L
    
    fuel_tank = ChemicalSource(
        name=f"Fuel Tank Custom {capacity_L:.1f}L",
        energy_density=energy_density_MJ_per_kg * 1e6,  # Convert MJ/kg to J/kg
        dry_mass=tank_dry_mass,
        initial_fuel_mass=fuel_mass,
        allow_negative_fuel=False,
        allow_refueling=allow_refueling,
    )
    
    return fuel_tank