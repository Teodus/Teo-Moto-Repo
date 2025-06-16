"""
Generic battery pack component builders for hybrid motorcycle powertrain simulation.

This module provides factory functions to create battery pack components
with realistic energy density, power characteristics, and efficiency curves.
"""

from math import inf

from ithaka_powertrain_sim.energy_sources import ElectricalSource
from ithaka_powertrain_sim.efficiency_definitions import ConstantEfficiency
from .component_specs import BATTERY_SPECS


def _create_battery_pack(
    battery_key: str,
    allow_negative: bool = False,
    custom_capacity_kWh: float | None = None
) -> ElectricalSource:
    """
    Create a battery pack component.
    
    Parameters
    ----------
    battery_key : str
        Key from BATTERY_SPECS dictionary
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
    custom_capacity_kWh : float | None, optional
        Override the default capacity (default: None uses spec capacity)
        
    Returns
    -------
    ElectricalSource
        Complete battery pack component
    """
    specs = BATTERY_SPECS[battery_key]
    
    # Use custom capacity if provided, otherwise use spec
    capacity_kWh = custom_capacity_kWh if custom_capacity_kWh is not None else specs["capacity_kWh"]
    
    # Calculate masses based on capacity
    scale_factor = capacity_kWh / specs["capacity_kWh"]
    cell_mass = specs["cell_mass_kg"] * scale_factor
    pack_overhead = specs["pack_overhead_kg"] * scale_factor
    
    # Calculate power limits based on C-rate and capacity
    max_power_W = capacity_kWh * 1000 * specs["max_discharge_rate_C"]
    max_regen_power_W = max_power_W * 0.8  # Slightly lower regen power
    
    battery_pack = ElectricalSource(
        name=f"Battery {capacity_kWh:.1f}kWh {specs['energy_density_WhKg']:.0f}Wh/kg",
        energy_density=specs["energy_density_WhKg"] * 3600,  # Convert Wh/kg to J/kg
        non_cell_mass=pack_overhead,
        cell_mass=cell_mass,
        efficiency_definition=ConstantEfficiency(specs["efficiency"]),
        minimum_power_generation=-max_regen_power_W,
        maximum_power_generation=max_power_W,
        allow_negative_fuel=allow_negative,
        allow_refueling=False,
    )
    
    return battery_pack


def Battery_5kWh_180WhKg(allow_negative: bool = False, custom_capacity_kWh: float | None = None) -> ElectricalSource:
    """
    Create a 5kWh battery pack with 180 Wh/kg energy density.
    
    Parameters
    ----------
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
    custom_capacity_kWh : float | None, optional
        Override the default 5kWh capacity (default: None)
        
    Returns
    -------
    ElectricalSource
        5kWh battery pack component
    """
    return _create_battery_pack("5kWh_180WhKg", allow_negative, custom_capacity_kWh)


def Battery_10kWh_200WhKg(allow_negative: bool = False, custom_capacity_kWh: float | None = None) -> ElectricalSource:
    """
    Create a 10kWh battery pack with 200 Wh/kg energy density.
    
    Parameters
    ----------
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
    custom_capacity_kWh : float | None, optional
        Override the default 10kWh capacity (default: None)
        
    Returns
    -------
    ElectricalSource
        10kWh battery pack component
    """
    return _create_battery_pack("10kWh_200WhKg", allow_negative, custom_capacity_kWh)


def Battery_15kWh_220WhKg(allow_negative: bool = False, custom_capacity_kWh: float | None = None) -> ElectricalSource:
    """
    Create a 15kWh battery pack with 220 Wh/kg energy density.
    
    Parameters
    ----------
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
    custom_capacity_kWh : float | None, optional
        Override the default 15kWh capacity (default: None)
        
    Returns
    -------
    ElectricalSource
        15kWh battery pack component
    """
    return _create_battery_pack("15kWh_220WhKg", allow_negative, custom_capacity_kWh)


def Battery_20kWh_180WhKg(allow_negative: bool = False, custom_capacity_kWh: float | None = None) -> ElectricalSource:
    """
    Create a 20kWh battery pack with 180 Wh/kg energy density (power optimized).
    
    Parameters
    ----------
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
    custom_capacity_kWh : float | None, optional
        Override the default 20kWh capacity (default: None)
        
    Returns
    -------
    ElectricalSource
        20kWh battery pack component
    """
    return _create_battery_pack("20kWh_180WhKg", allow_negative, custom_capacity_kWh)


def Battery_25kWh_200WhKg(allow_negative: bool = False, custom_capacity_kWh: float | None = None) -> ElectricalSource:
    """
    Create a 25kWh battery pack with 200 Wh/kg energy density.
    
    Parameters
    ----------
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
    custom_capacity_kWh : float | None, optional
        Override the default 25kWh capacity (default: None)
        
    Returns
    -------
    ElectricalSource
        25kWh battery pack component
    """
    return _create_battery_pack("25kWh_200WhKg", allow_negative, custom_capacity_kWh)


def Battery_Custom(
    capacity_kWh: float,
    energy_density_WhKg: float = 200,
    power_density_WKg: float = 1000,
    max_discharge_rate_C: float = 3.5,
    efficiency: float = 0.93,
    pack_overhead_ratio: float = 0.3,
    allow_negative: bool = False
) -> ElectricalSource:
    """
    Create a custom battery pack with specified parameters.
    
    Parameters
    ----------
    capacity_kWh : float
        Battery pack capacity in kWh
    energy_density_WhKg : float, optional
        Energy density in Wh/kg (default: 200)
    power_density_WKg : float, optional
        Power density in W/kg (default: 1000)
    max_discharge_rate_C : float, optional
        Maximum discharge rate in C-rate (default: 3.5)
    efficiency : float, optional
        Battery efficiency (default: 0.93)
    pack_overhead_ratio : float, optional
        Pack overhead mass as ratio of cell mass (default: 0.3)
    allow_negative : bool, optional
        Whether to allow negative state of charge (default: False)
        
    Returns
    -------
    ElectricalSource
        Custom battery pack component
    """
    # Calculate masses
    cell_mass = (capacity_kWh * 1000) / energy_density_WhKg  # kg
    pack_overhead = cell_mass * pack_overhead_ratio  # kg
    
    # Calculate power limits
    max_power_W = capacity_kWh * 1000 * max_discharge_rate_C
    max_regen_power_W = max_power_W * 0.8
    
    battery_pack = ElectricalSource(
        name=f"Battery Custom {capacity_kWh:.1f}kWh {energy_density_WhKg:.0f}Wh/kg",
        energy_density=energy_density_WhKg * 3600,  # Convert Wh/kg to J/kg
        non_cell_mass=pack_overhead,
        cell_mass=cell_mass,
        efficiency_definition=ConstantEfficiency(efficiency),
        minimum_power_generation=-max_regen_power_W,
        maximum_power_generation=max_power_W,
        allow_negative_fuel=allow_negative,
        allow_refueling=False,
    )
    
    return battery_pack