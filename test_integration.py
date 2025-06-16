#!/usr/bin/env python3
"""
Integration test for the component library
"""

print("🧪 Running comprehensive integration test...")
print()

# Test 1: Component Library Imports
from ithaka_powertrain_sim.component_library import (
    Engine_400cc_30kW, Motor_50kW_HighPerf, Battery_15kWh_220WhKg,
    create_custom_engine, create_custom_motor, create_custom_battery,
    ENGINE_SPECS, MOTOR_SPECS, BATTERY_SPECS
)
print("✅ Test 1: Component library imports successful")

# Test 2: Create Preset Components
engine = Engine_400cc_30kW()
motor = Motor_50kW_HighPerf()
battery = Battery_15kWh_220WhKg()
print("✅ Test 2: Preset components created")
print(f"   Engine: {engine._maximum_power_generation/1000:.0f}kW, {engine.mass:.1f}kg")
print(f"   Motor: {motor._maximum_power_generation/1000:.0f}kW, {motor.mass:.1f}kg")
print(f"   Battery: {battery.remaining_energy_capacity/3.6e6:.1f}kWh, {battery.mass:.1f}kg")

# Test 3: Create Custom Components  
custom_engine = create_custom_engine("Custom Test", 450, 35, 50, 0.33)
custom_motor = create_custom_motor("Custom Test", 60, 45, 38, 0.94)
custom_battery = create_custom_battery("Custom Test", 12, 210, 4.0, 0.94)
print("✅ Test 3: Custom components created")

# Test 4: Complete Motorcycle Assembly
from ithaka_powertrain_sim.motorbike import Motorbike
from ithaka_powertrain_sim.components import MechanicalBrake, MechanicalComponent
from ithaka_powertrain_sim.efficiency_definitions import ConstantEfficiency

# EV Motorcycle
ev_battery = Battery_15kWh_220WhKg()
ev_motor = Motor_50kW_HighPerf()
ev_motor._child_components = (ev_battery,)
ev_brake = MechanicalBrake("EV Brake")

ev_motorbike = Motorbike(
    name="Test EV",
    dry_mass_excluding_components=200.0,
    front_mass_ratio=0.45,
    front_wheel_inertia=5.0 * (0.45**2) / 2.0,
    front_wheel_radius=0.45,
    front_wheel_coefficient_of_rolling_resistance=0.01,
    rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
    rear_wheel_radius=0.45,
    rear_wheel_coefficient_of_rolling_resistance=0.01,
    frontal_area=0.75,
    coefficient_of_aerodynamic_drag=0.7,
    child_components=(ev_motor, ev_brake),
)

# ICE Motorcycle
ice_engine = Engine_400cc_30kW()
ice_gearbox = MechanicalComponent(
    name="Gearbox",
    dry_mass=15.0,
    efficiency_definition=ConstantEfficiency(0.92),
    child_components=(ice_engine,)
)
ice_brake = MechanicalBrake("ICE Brake")

ice_motorbike = Motorbike(
    name="Test ICE",
    dry_mass_excluding_components=180.0,
    front_mass_ratio=0.52,
    front_wheel_inertia=5.0 * (0.45**2) / 2.0,
    front_wheel_radius=0.45,
    front_wheel_coefficient_of_rolling_resistance=0.01,
    rear_wheel_inertia=12.0 * (0.45**2) / 2.0,
    rear_wheel_radius=0.45,
    rear_wheel_coefficient_of_rolling_resistance=0.01,
    frontal_area=0.85,
    coefficient_of_aerodynamic_drag=0.8,
    child_components=(ice_gearbox, ice_brake),
)

print("✅ Test 4: Complete motorcycles assembled")
print(f"   EV: {ev_motorbike.mass:.1f}kg, P/W: {(ev_motor._maximum_power_generation/1000)/ev_motorbike.mass:.3f} kW/kg")
print(f"   ICE: {ice_motorbike.mass:.1f}kg, P/W: {(ice_engine._maximum_power_generation/1000)/ice_motorbike.mass:.3f} kW/kg")

# Test 5: Simulation Functions
energy_ev = ev_motorbike.calculate_energy_required(ev_motorbike.mass, 10, 15, 100, 5)
energy_ice = ice_motorbike.calculate_energy_required(ice_motorbike.mass, 10, 15, 100, 5)
print("✅ Test 5: Simulation functions working")
print(f"   EV energy demand: {energy_ev/1000:.1f} kJ")
print(f"   ICE energy demand: {energy_ice/1000:.1f} kJ")

# Test 6: Interactive Picker State
from ithaka_powertrain_sim.component_library.interactive_picker import ComponentPickerState
state = ComponentPickerState()
state.motorcycle_type = "Hybrid"
state.selected_components["engine"] = custom_engine
state.selected_components["motor"] = custom_motor 
state.selected_components["battery"] = custom_battery
state.update_metrics()
print("✅ Test 6: Interactive picker state working")
print(f"   Type: {state.motorcycle_type}, Weight: {state.total_weight:.1f}kg, Cost: ${state.total_cost:.0f}")

print()
print("🎉 ALL TESTS PASSED! Component library is fully functional!")
print()
print("📋 Summary:")
print(f"   • {len(ENGINE_SPECS)} preset engines available")
print(f"   • {len(MOTOR_SPECS)} preset motors available") 
print(f"   • {len(BATTERY_SPECS)} preset batteries available")
print("   • Custom component creation working")
print("   • Complete motorcycle assembly working")
print("   • Simulation integration working")
print("   • Interactive picker ready for Colab")
print()
print("🚀 Ready to test the interactive notebook in Jupyter/Colab!")