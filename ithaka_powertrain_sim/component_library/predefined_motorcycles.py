"""
Predefined Motorcycle Configurations

This module contains factory functions for creating complete motorcycle configurations
using the generic component library. Each motorcycle represents a realistic 
powertrain configuration suitable for different use cases.
"""

from ..motorbike import Motorbike
from ..components import MechanicalBrake, MechanicalComponent, ElectricalComponent
from ..efficiency_definitions import ConstantEfficiency

from .engines import (
    Engine_250cc_20kW, Engine_400cc_30kW, Engine_650cc_50kW, 
    Engine_750cc_60kW, Engine_900cc_70kW, Engine_1000cc_80kW
)
from .motors import (
    Motor_5kW_Hub, Motor_10kW_Hub, Motor_15kW_MidDrive, Motor_30kW_MidDrive,
    Motor_50kW_HighPerf, Motor_80kW_HighPerf, Motor_120kW_HighPerf, Motor_15kW_Generator
)
from .batteries import (
    Battery_5kWh_180WhKg, Battery_8kWh_190WhKg, Battery_10kWh_200WhKg,
    Battery_15kWh_220WhKg, Battery_25kWh_200WhKg
)
from .fuel_systems import FuelTank_8L, FuelTank_15L, FuelTank_25L


def create_commuter_ev():
    """Urban commuter electric motorcycle - efficient and lightweight"""
    battery = Battery_8kWh_190WhKg()
    motor = Motor_15kW_MidDrive(regen_power_ratio=0.8)
    motor._child_components = (battery,)
    brake = MechanicalBrake("Commuter EV Brake")
    
    return Motorbike(
        name="Commuter EV",
        dry_mass_excluding_components=180.0,
        front_mass_ratio=0.45,
        front_wheel_inertia=4.0 * (0.4**2) / 2.0,
        front_wheel_radius=0.4,
        front_wheel_coefficient_of_rolling_resistance=0.008,
        rear_wheel_inertia=10.0 * (0.4**2) / 2.0,
        rear_wheel_radius=0.4,
        rear_wheel_coefficient_of_rolling_resistance=0.008,
        frontal_area=0.7,
        coefficient_of_aerodynamic_drag=0.65,
        child_components=(motor, brake),
    )


def create_sport_ev():
    """High-performance electric sport motorcycle"""
    battery = Battery_15kWh_220WhKg()
    motor = Motor_80kW_HighPerf(regen_power_ratio=0.9)
    motor._child_components = (battery,)
    brake = MechanicalBrake("Sport EV Brake")
    
    return Motorbike(
        name="Sport EV",
        dry_mass_excluding_components=200.0,
        front_mass_ratio=0.48,
        front_wheel_inertia=5.0 * (0.45**2) / 2.0,
        front_wheel_radius=0.45,
        front_wheel_coefficient_of_rolling_resistance=0.01,
        rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
        rear_wheel_radius=0.45,
        rear_wheel_coefficient_of_rolling_resistance=0.01,
        frontal_area=0.75,
        coefficient_of_aerodynamic_drag=0.7,
        child_components=(motor, brake),
    )


def create_touring_ev():
    """Long-range electric touring motorcycle"""
    battery = Battery_25kWh_200WhKg()
    motor = Motor_50kW_HighPerf(regen_power_ratio=0.85)
    motor._child_components = (battery,)
    brake = MechanicalBrake("Touring EV Brake")
    
    return Motorbike(
        name="Touring EV",
        dry_mass_excluding_components=220.0,
        front_mass_ratio=0.46,
        front_wheel_inertia=5.5 * (0.45**2) / 2.0,
        front_wheel_radius=0.45,
        front_wheel_coefficient_of_rolling_resistance=0.009,
        rear_wheel_inertia=13.0 * (0.45**2) / 2.0,
        rear_wheel_radius=0.45,
        rear_wheel_coefficient_of_rolling_resistance=0.009,
        frontal_area=0.8,
        coefficient_of_aerodynamic_drag=0.72,
        child_components=(motor, brake),
    )


def create_entry_level_ice():
    """Entry-level ICE motorcycle for beginners"""
    engine = Engine_250cc_20kW(fuel_capacity_L=10.0)
    gearbox = MechanicalComponent(
        name="Entry ICE Gearbox",
        dry_mass=12.0,
        efficiency_definition=ConstantEfficiency(0.90),
        child_components=(engine,)
    )
    brake = MechanicalBrake("Entry ICE Brake")
    
    return Motorbike(
        name="Entry Level ICE",
        dry_mass_excluding_components=160.0,
        front_mass_ratio=0.52,
        front_wheel_inertia=4.0 * (0.4**2) / 2.0,
        front_wheel_radius=0.4,
        front_wheel_coefficient_of_rolling_resistance=0.012,
        rear_wheel_inertia=8.0 * (0.4**2) / 2.0,
        rear_wheel_radius=0.4,
        rear_wheel_coefficient_of_rolling_resistance=0.012,
        frontal_area=0.75,
        coefficient_of_aerodynamic_drag=0.8,
        child_components=(gearbox, brake),
    )


def create_middleweight_ice():
    """Versatile middleweight ICE motorcycle"""
    engine = Engine_650cc_50kW(fuel_capacity_L=15.0)
    gearbox = MechanicalComponent(
        name="Middleweight ICE Gearbox",
        dry_mass=15.0,
        efficiency_definition=ConstantEfficiency(0.92),
        child_components=(engine,)
    )
    brake = MechanicalBrake("Middleweight ICE Brake")
    
    return Motorbike(
        name="Middleweight ICE",
        dry_mass_excluding_components=180.0,
        front_mass_ratio=0.51,
        front_wheel_inertia=5.0 * (0.45**2) / 2.0,
        front_wheel_radius=0.45,
        front_wheel_coefficient_of_rolling_resistance=0.01,
        rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
        rear_wheel_radius=0.45,
        rear_wheel_coefficient_of_rolling_resistance=0.01,
        frontal_area=0.8,
        coefficient_of_aerodynamic_drag=0.78,
        child_components=(gearbox, brake),
    )


def create_superbike_ice():
    """High-performance ICE superbike"""
    engine = Engine_1000cc_80kW(fuel_capacity_L=18.0)
    gearbox = MechanicalComponent(
        name="Superbike ICE Gearbox",
        dry_mass=18.0,
        efficiency_definition=ConstantEfficiency(0.94),
        child_components=(engine,)
    )
    brake = MechanicalBrake("Superbike ICE Brake")
    
    return Motorbike(
        name="Superbike ICE",
        dry_mass_excluding_components=190.0,
        front_mass_ratio=0.50,
        front_wheel_inertia=5.0 * (0.45**2) / 2.0,
        front_wheel_radius=0.45,
        front_wheel_coefficient_of_rolling_resistance=0.01,
        rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
        rear_wheel_radius=0.45,
        rear_wheel_coefficient_of_rolling_resistance=0.01,
        frontal_area=0.8,
        coefficient_of_aerodynamic_drag=0.75,
        child_components=(gearbox, brake),
    )


def create_series_hybrid():
    """Series hybrid motorcycle with generator"""
    engine = Engine_400cc_30kW(fuel_capacity_L=12.0)
    generator = Motor_15kW_Generator(fixed_rpm=4000)
    generator._child_components = (engine,)
    
    battery = Battery_10kWh_200WhKg()
    
    electrical_breaker = ElectricalComponent(
        name="Electrical Breaker",
        child_components=(generator,)
    )
    
    traction_motor = Motor_50kW_HighPerf(regen_power_ratio=0.9)
    traction_motor._child_components = (battery, electrical_breaker)
    
    brake = MechanicalBrake("Hybrid Brake")
    
    return Motorbike(
        name="Series Hybrid",
        dry_mass_excluding_components=220.0,
        front_mass_ratio=0.48,
        front_wheel_inertia=5.0 * (0.45**2) / 2.0,
        front_wheel_radius=0.45,
        front_wheel_coefficient_of_rolling_resistance=0.01,
        rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
        rear_wheel_radius=0.45,
        rear_wheel_coefficient_of_rolling_resistance=0.01,
        frontal_area=0.8,
        coefficient_of_aerodynamic_drag=0.75,
        child_components=(traction_motor, brake),
    )


def create_parallel_hybrid():
    """Parallel hybrid motorcycle with direct mechanical connection"""
    engine = Engine_650cc_50kW(fuel_capacity_L=15.0)
    battery = Battery_8kWh_190WhKg()
    
    assist_motor = Motor_30kW_MidDrive(regen_power_ratio=0.8)
    assist_motor._child_components = (battery,)
    
    hybrid_gearbox = MechanicalComponent(
        name="Parallel Hybrid Gearbox",
        dry_mass=20.0,
        efficiency_definition=ConstantEfficiency(0.91),
        child_components=(engine, assist_motor)
    )
    
    brake = MechanicalBrake("Parallel Hybrid Brake")
    
    return Motorbike(
        name="Parallel Hybrid",
        dry_mass_excluding_components=210.0,
        front_mass_ratio=0.49,
        front_wheel_inertia=5.0 * (0.45**2) / 2.0,
        front_wheel_radius=0.45,
        front_wheel_coefficient_of_rolling_resistance=0.01,
        rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
        rear_wheel_radius=0.45,
        rear_wheel_coefficient_of_rolling_resistance=0.01,
        frontal_area=0.82,
        coefficient_of_aerodynamic_drag=0.77,
        child_components=(hybrid_gearbox, brake),
    )


# Dictionary mapping motorcycle names to their factory functions
PREDEFINED_MOTORCYCLES = {
    "Commuter EV": create_commuter_ev,
    "Sport EV": create_sport_ev,
    "Touring EV": create_touring_ev,
    "Entry Level ICE": create_entry_level_ice,
    "Middleweight ICE": create_middleweight_ice,
    "Superbike ICE": create_superbike_ice,
    "Series Hybrid": create_series_hybrid,
    "Parallel Hybrid": create_parallel_hybrid,
}


# Motorcycle specifications for display purposes
MOTORCYCLE_SPECS = {
    "Commuter EV": {
        "type": "Electric",
        "power_kW": 15,
        "battery_kWh": 8,
        "range_km": "~80",
        "description": "Efficient urban commuter with regenerative braking"
    },
    "Sport EV": {
        "type": "Electric",
        "power_kW": 80,
        "battery_kWh": 15,
        "range_km": "~120",
        "description": "High-performance electric sportbike"
    },
    "Touring EV": {
        "type": "Electric",
        "power_kW": 50,
        "battery_kWh": 25,
        "range_km": "~200",
        "description": "Long-range touring with maximum battery capacity"
    },
    "Entry Level ICE": {
        "type": "ICE",
        "power_kW": 20,
        "displacement_cc": 250,
        "fuel_L": 10,
        "description": "Perfect for new riders and city commuting"
    },
    "Middleweight ICE": {
        "type": "ICE", 
        "power_kW": 50,
        "displacement_cc": 650,
        "fuel_L": 15,
        "description": "Versatile all-rounder for various riding conditions"
    },
    "Superbike ICE": {
        "type": "ICE",
        "power_kW": 80,
        "displacement_cc": 1000,
        "fuel_L": 18,
        "description": "Track-focused high-performance machine"
    },
    "Series Hybrid": {
        "type": "Hybrid",
        "power_kW": 50,
        "battery_kWh": 10,
        "engine_cc": 400,
        "description": "Engine as generator only, electric traction"
    },
    "Parallel Hybrid": {
        "type": "Hybrid",
        "power_kW": 80,
        "battery_kWh": 8,
        "engine_cc": 650,
        "description": "Engine and motor work together for maximum power"
    },
}


def get_motorcycle_list():
    """Return list of available predefined motorcycles"""
    return list(PREDEFINED_MOTORCYCLES.keys())


def get_motorcycle_specs(name):
    """Get specifications for a specific motorcycle"""
    return MOTORCYCLE_SPECS.get(name, {})


def create_motorcycle(name):
    """Create a motorcycle by name"""
    if name not in PREDEFINED_MOTORCYCLES:
        raise ValueError(f"Unknown motorcycle: {name}")
    return PREDEFINED_MOTORCYCLES[name]()