"""
Generic electric motor component builders for hybrid motorcycle powertrain simulation.

This module provides factory functions to create electric motor components
with realistic efficiency curves and power characteristics.
"""

from math import inf

from ithaka_powertrain_sim.components import ElectricMotor
from ithaka_powertrain_sim.efficiency_definitions import ConstantEfficiency
from .component_specs import MOTOR_SPECS


def _create_motor(
    motor_key: str,
    regen_power_ratio: float = 0.8,
    fixed_rpm: float | None = None
) -> ElectricMotor:
    """
    Create an electric motor component.
    
    Parameters
    ----------
    motor_key : str
        Key from MOTOR_SPECS dictionary
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.8)
    fixed_rpm : float | None, optional
        Fixed RPM for generator mode (default: None for variable speed)
        
    Returns
    -------
    ElectricMotor
        Complete electric motor component
    """
    specs = MOTOR_SPECS[motor_key]
    
    motor = ElectricMotor(
        name=f"Motor {specs['max_power_kW']}kW {specs['type'].replace('_', ' ').title()}",
        dry_mass=specs["dry_mass_kg"],
        efficiency_definition=ConstantEfficiency(specs["efficiency_peak"]),
        child_components=(),  # Battery will be added separately
        minimum_power_generation=-specs["max_power_kW"] * 1e3 * regen_power_ratio,
        maximum_power_generation=specs["max_power_kW"] * 1e3,
    )
    
    if fixed_rpm is not None:
        motor._fixed_angular_velocity = fixed_rpm * 2 * 3.14159 / 60  # Convert to rad/s
    
    return motor


def Motor_5kW_Hub(regen_power_ratio: float = 0.6) -> ElectricMotor:
    """
    Create a 5kW hub motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.6)
        
    Returns
    -------
    ElectricMotor
        5kW hub motor component
    """
    return _create_motor("5kW_Hub", regen_power_ratio)


def Motor_10kW_Hub(regen_power_ratio: float = 0.7) -> ElectricMotor:
    """
    Create a 10kW hub motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.7)
        
    Returns
    -------
    ElectricMotor
        10kW hub motor component
    """
    return _create_motor("10kW_Hub", regen_power_ratio)


def Motor_15kW_MidDrive(regen_power_ratio: float = 0.8) -> ElectricMotor:
    """
    Create a 15kW mid-drive motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.8)
        
    Returns
    -------
    ElectricMotor
        15kW mid-drive motor component
    """
    return _create_motor("15kW_MidDrive", regen_power_ratio)


def Motor_30kW_MidDrive(regen_power_ratio: float = 0.8) -> ElectricMotor:
    """
    Create a 30kW mid-drive motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.8)
        
    Returns
    -------
    ElectricMotor
        30kW mid-drive motor component
    """
    return _create_motor("30kW_MidDrive", regen_power_ratio)


def Motor_50kW_HighPerf(regen_power_ratio: float = 0.9) -> ElectricMotor:
    """
    Create a 50kW high performance motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.9)
        
    Returns
    -------
    ElectricMotor
        50kW high performance motor component
    """
    return _create_motor("50kW_HighPerf", regen_power_ratio)


def Motor_80kW_HighPerf(regen_power_ratio: float = 0.9) -> ElectricMotor:
    """
    Create an 80kW high performance motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.9)
        
    Returns
    -------
    ElectricMotor
        80kW high performance motor component
    """
    return _create_motor("80kW_HighPerf", regen_power_ratio)


def Motor_120kW_HighPerf(regen_power_ratio: float = 0.9) -> ElectricMotor:
    """
    Create a 120kW high performance motor.
    
    Parameters
    ----------
    regen_power_ratio : float, optional
        Ratio of regenerative braking power to max power (default: 0.9)
        
    Returns
    -------
    ElectricMotor
        120kW high performance motor component
    """
    return _create_motor("120kW_HighPerf", regen_power_ratio)


def Motor_15kW_Generator(fixed_rpm: float = 3500) -> ElectricMotor:
    """
    Create a 15kW generator motor for hybrid systems.
    
    Parameters
    ----------
    fixed_rpm : float, optional
        Fixed RPM for generator operation (default: 3500)
        
    Returns
    -------
    ElectricMotor
        15kW generator motor component with fixed RPM
    """
    return _create_motor("15kW_MidDrive", regen_power_ratio=0.0, fixed_rpm=fixed_rpm)