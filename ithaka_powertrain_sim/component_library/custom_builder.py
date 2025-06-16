"""
Custom component builder for creating user-defined powertrain components.

This module provides functions to create custom components with user-specified
parameters, including validation and integration with the existing component architecture.
"""

from math import inf
from typing import Tuple

from ithaka_powertrain_sim.components import CombustionEngine, ElectricMotor
from ithaka_powertrain_sim.energy_sources import ChemicalSource, ElectricalSource
from ithaka_powertrain_sim.efficiency_definitions import (
    ConstantEfficiency,
    AngularVelocityEfficiency,
)


def validate_engine_parameters(
    displacement_cc: float,
    max_power_kW: float,
    dry_mass_kg: float,
    efficiency_peak: float
) -> Tuple[bool, str]:
    """
    Validate custom engine parameters against realistic bounds.
    
    Parameters
    ----------
    displacement_cc : float
        Engine displacement in cubic centimeters
    max_power_kW : float
        Maximum power output in kilowatts
    dry_mass_kg : float
        Dry mass of engine in kilograms
    efficiency_peak : float
        Peak efficiency ratio (0-1)
        
    Returns
    -------
    Tuple[bool, str]
        (is_valid, warning_message)
    """
    warnings = []
    
    # Check displacement bounds
    if displacement_cc < 50 or displacement_cc > 2000:
        warnings.append(f"Displacement {displacement_cc}cc is outside typical range (50-2000cc)")
    
    # Check power density (typical: 40-120 kW/L)
    power_density = max_power_kW / (displacement_cc / 1000)
    if power_density < 20:
        warnings.append(f"Power density {power_density:.1f} kW/L is very low")
    elif power_density > 150:
        warnings.append(f"Power density {power_density:.1f} kW/L is extremely high")
    
    # Check mass (typical: 1-3 kg/kW)
    specific_mass = dry_mass_kg / max_power_kW
    if specific_mass < 0.8:
        warnings.append(f"Specific mass {specific_mass:.1f} kg/kW is unrealistically low")
    elif specific_mass > 5:
        warnings.append(f"Specific mass {specific_mass:.1f} kg/kW is very high")
    
    # Check efficiency bounds
    if efficiency_peak < 0.15 or efficiency_peak > 0.50:
        warnings.append(f"Peak efficiency {efficiency_peak*100:.1f}% is outside typical range (15-50%)")
    
    warning_message = "; ".join(warnings) if warnings else "Parameters look reasonable"
    return len(warnings) == 0, warning_message


def validate_motor_parameters(
    max_power_kW: float,
    continuous_power_kW: float,
    dry_mass_kg: float,
    efficiency_peak: float
) -> Tuple[bool, str]:
    """
    Validate custom motor parameters against realistic bounds.
    
    Parameters
    ----------
    max_power_kW : float
        Maximum power output in kilowatts
    continuous_power_kW : float
        Continuous power output in kilowatts
    dry_mass_kg : float
        Dry mass of motor in kilograms
    efficiency_peak : float
        Peak efficiency ratio (0-1)
        
    Returns
    -------
    Tuple[bool, str]
        (is_valid, warning_message)
    """
    warnings = []
    
    # Check power relationship
    if continuous_power_kW > max_power_kW:
        warnings.append("Continuous power cannot exceed maximum power")
    
    power_ratio = continuous_power_kW / max_power_kW if max_power_kW > 0 else 0
    if power_ratio < 0.5:
        warnings.append(f"Continuous/peak ratio {power_ratio:.2f} is low (typical: 0.6-0.8)")
    
    # Check specific power (typical: 1-6 kW/kg for electric motors)
    specific_power = max_power_kW / dry_mass_kg if dry_mass_kg > 0 else 0
    if specific_power < 0.5:
        warnings.append(f"Specific power {specific_power:.1f} kW/kg is very low")
    elif specific_power > 8:
        warnings.append(f"Specific power {specific_power:.1f} kW/kg is extremely high")
    
    # Check efficiency bounds
    if efficiency_peak < 0.75 or efficiency_peak > 0.98:
        warnings.append(f"Peak efficiency {efficiency_peak*100:.1f}% is outside typical range (75-98%)")
    
    warning_message = "; ".join(warnings) if warnings else "Parameters look reasonable"
    return len(warnings) == 0, warning_message


def validate_battery_parameters(
    capacity_kWh: float,
    energy_density_WhKg: float,
    max_discharge_C: float,
    efficiency: float
) -> Tuple[bool, str]:
    """
    Validate custom battery parameters against realistic bounds.
    
    Parameters
    ----------
    capacity_kWh : float
        Battery capacity in kilowatt-hours
    energy_density_WhKg : float
        Energy density in watt-hours per kilogram
    max_discharge_C : float
        Maximum discharge rate in C-rate
    efficiency : float
        Battery efficiency ratio (0-1)
        
    Returns
    -------
    Tuple[bool, str]
        (is_valid, warning_message)
    """
    warnings = []
    
    # Check energy density bounds (current Li-ion: 100-300 Wh/kg)
    if energy_density_WhKg < 50:
        warnings.append(f"Energy density {energy_density_WhKg} Wh/kg is very low")
    elif energy_density_WhKg > 350:
        warnings.append(f"Energy density {energy_density_WhKg} Wh/kg exceeds current technology")
    
    # Check C-rate bounds
    if max_discharge_C < 0.5:
        warnings.append(f"Discharge rate {max_discharge_C}C is very low")
    elif max_discharge_C > 10:
        warnings.append(f"Discharge rate {max_discharge_C}C is extremely high")
    
    # Check efficiency bounds
    if efficiency < 0.80 or efficiency > 0.99:
        warnings.append(f"Efficiency {efficiency*100:.1f}% is outside typical range (80-99%)")
    
    # Check capacity bounds
    if capacity_kWh < 1 or capacity_kWh > 100:
        warnings.append(f"Capacity {capacity_kWh} kWh is outside practical range (1-100 kWh)")
    
    warning_message = "; ".join(warnings) if warnings else "Parameters look reasonable"
    return len(warnings) == 0, warning_message


def create_custom_engine(
    name: str,
    displacement_cc: float,
    max_power_kW: float,
    dry_mass_kg: float,
    efficiency_peak: float,
    fuel_capacity_L: float = 15.0,
    allow_refueling: bool = True
) -> CombustionEngine:
    """
    Create a custom combustion engine with user-specified parameters.
    
    Parameters
    ----------
    name : str
        Name for the custom engine
    displacement_cc : float
        Engine displacement in cubic centimeters
    max_power_kW : float
        Maximum power output in kilowatts
    dry_mass_kg : float
        Dry mass of engine in kilograms
    efficiency_peak : float
        Peak efficiency ratio (0-1)
    fuel_capacity_L : float, optional
        Fuel tank capacity in liters (default: 15.0)
    allow_refueling : bool, optional
        Whether to allow mid-journey refueling (default: True)
        
    Returns
    -------
    CombustionEngine
        Custom engine component with integrated fuel tank
    """
    # Create fuel tank
    fuel_density_kg_per_L = 0.75
    energy_density_MJ_per_kg = 43.0
    
    fuel_tank = ChemicalSource(
        name=f"{name} Fuel Tank {fuel_capacity_L}L",
        energy_density=energy_density_MJ_per_kg * 1e6,
        dry_mass=2.0 + fuel_capacity_L * 0.2,
        initial_fuel_mass=fuel_capacity_L * fuel_density_kg_per_L,
        allow_negative_fuel=False,
        allow_refueling=allow_refueling,
    )
    
    # Create simple efficiency curve
    efficiency_curve = ConstantEfficiency(efficiency_peak)
    
    engine = CombustionEngine(
        name=name,
        dry_mass=dry_mass_kg,
        efficiency_definition=efficiency_curve,
        child_components=(fuel_tank,),
        minimum_power_generation=0.0,
        maximum_power_generation=max_power_kW * 1e3,
    )
    
    return engine


def create_custom_motor(
    name: str,
    max_power_kW: float,
    continuous_power_kW: float,
    dry_mass_kg: float,
    efficiency_peak: float,
    regen_power_ratio: float = 0.8
) -> ElectricMotor:
    """
    Create a custom electric motor with user-specified parameters.
    
    Parameters
    ----------
    name : str
        Name for the custom motor
    max_power_kW : float
        Maximum power output in kilowatts
    continuous_power_kW : float
        Continuous power output in kilowatts
    dry_mass_kg : float
        Dry mass of motor in kilograms
    efficiency_peak : float
        Peak efficiency ratio (0-1)
    regen_power_ratio : float, optional
        Ratio of regenerative power to max power (default: 0.8)
        
    Returns
    -------
    ElectricMotor
        Custom motor component
    """
    motor = ElectricMotor(
        name=name,
        dry_mass=dry_mass_kg,
        efficiency_definition=ConstantEfficiency(efficiency_peak),
        child_components=(),
        minimum_power_generation=-max_power_kW * 1e3 * regen_power_ratio,
        maximum_power_generation=max_power_kW * 1e3,
    )
    
    return motor


def create_custom_battery(
    name: str,
    capacity_kWh: float,
    energy_density_WhKg: float,
    max_discharge_C: float,
    efficiency: float,
    pack_overhead_ratio: float = 0.3,
    allow_negative: bool = False
) -> ElectricalSource:
    """
    Create a custom battery pack with user-specified parameters.
    
    Parameters
    ----------
    name : str
        Name for the custom battery
    capacity_kWh : float
        Battery capacity in kilowatt-hours
    energy_density_WhKg : float
        Energy density in watt-hours per kilogram
    max_discharge_C : float
        Maximum discharge rate in C-rate
    efficiency : float
        Battery efficiency ratio (0-1)
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
    cell_mass = (capacity_kWh * 1000) / energy_density_WhKg
    pack_overhead = cell_mass * pack_overhead_ratio
    
    # Calculate power limits
    max_power_W = capacity_kWh * 1000 * max_discharge_C
    max_regen_power_W = max_power_W * 0.8
    
    battery_pack = ElectricalSource(
        name=name,
        energy_density=energy_density_WhKg * 3600,
        non_cell_mass=pack_overhead,
        cell_mass=cell_mass,
        efficiency_definition=ConstantEfficiency(efficiency),
        minimum_power_generation=-max_regen_power_W,
        maximum_power_generation=max_power_W,
        allow_negative_fuel=allow_negative,
        allow_refueling=False,
    )
    
    return battery_pack


def create_custom_fuel_tank(
    name: str,
    capacity_L: float,
    fuel_density_kg_per_L: float = 0.75,
    energy_density_MJ_per_kg: float = 43.0,
    tank_mass_per_liter: float = 0.35,
    allow_refueling: bool = True
) -> ChemicalSource:
    """
    Create a custom fuel tank with user-specified parameters.
    
    Parameters
    ----------
    name : str
        Name for the custom fuel tank
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
        name=name,
        energy_density=energy_density_MJ_per_kg * 1e6,
        dry_mass=tank_dry_mass,
        initial_fuel_mass=fuel_mass,
        allow_negative_fuel=False,
        allow_refueling=allow_refueling,
    )
    
    return fuel_tank


def estimate_component_cost(component_type: str, **kwargs) -> float:
    """
    Estimate the cost of a custom component based on its specifications.
    
    Parameters
    ----------
    component_type : str
        Type of component ('engine', 'motor', 'battery', 'fuel_tank')
    **kwargs
        Component specifications
        
    Returns
    -------
    float
        Estimated cost in USD
    """
    if component_type == "engine":
        # Cost based on power and displacement
        power_kW = kwargs.get("max_power_kW", 30)
        displacement_cc = kwargs.get("displacement_cc", 500)
        base_cost = 1500 + (power_kW * 80) + (displacement_cc * 2)
        return base_cost
        
    elif component_type == "motor":
        # Cost based on power
        power_kW = kwargs.get("max_power_kW", 30)
        base_cost = 800 + (power_kW * 120)
        return base_cost
        
    elif component_type == "battery":
        # Cost based on capacity
        capacity_kWh = kwargs.get("capacity_kWh", 10)
        energy_density = kwargs.get("energy_density_WhKg", 200)
        base_cost_per_kWh = 200 + (energy_density - 150) * 3  # Higher density costs more
        return capacity_kWh * base_cost_per_kWh
        
    elif component_type == "fuel_tank":
        # Simple cost based on capacity
        capacity_L = kwargs.get("capacity_L", 15)
        return 100 + (capacity_L * 8)
        
    else:
        return 0.0