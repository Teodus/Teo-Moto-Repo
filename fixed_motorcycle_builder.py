"""
Fixed motorcycle building function that works with the existing component system.
"""

def build_motorcycle_from_state_fixed(state):
    """Build a Motorbike object using available components."""
    
    # Get selected components
    engine = state.selected_components.get('engine')
    motor = state.selected_components.get('motor') 
    battery = state.selected_components.get('battery')
    
    # Create component lists for Motorbike constructor
    mechanical_components = []
    electrical_components = []
    energy_sources = []
    
    # Add engine components
    if engine:
        mechanical_components.append(engine)
        
        # Add simple gearbox using available component
        from ithaka_powertrain_sim.components.gearbox import Gearbox
        gearbox = Gearbox(name="Auto_Gearbox", gear_ratios=[3.5], efficiency=0.95, mass=15.0)
        mechanical_components.append(gearbox)
        
        # Add fuel tank using available component  
        from ithaka_powertrain_sim.energy_sources import ChemicalSource
        fuel_tank = ChemicalSource(
            name="Fuel_Tank",
            energy_density=44e6,  # J/kg for gasoline
            non_fuel_mass=8.0,    # kg (tank mass)
            fuel_mass=11.25,      # kg (15L * 0.75 kg/L)
            efficiency_definition=None,  # Will use engine efficiency
            minimum_power_generation=0,
            maximum_power_generation=float('inf'),
            allow_negative_fuel=False,
            allow_refueling=True
        )
        energy_sources.append(fuel_tank)
    
    # Add motor components
    if motor:
        electrical_components.append(motor)
    
    # Add battery
    if battery:
        energy_sources.append(battery)
    
    # Always add brake using available component
    from ithaka_powertrain_sim.components.mechanical_brake import MechanicalBrake
    brake = MechanicalBrake(name="Standard_Brake", dry_mass=8.0, inertia=0.1)
    mechanical_components.append(brake)
    
    # Create motorbike
    from ithaka_powertrain_sim.motorbike import Motorbike
    motorbike = Motorbike(
        name=f"{state.motorcycle_type}_Custom",
        mechanical_components=mechanical_components,
        electrical_components=electrical_components,
        energy_sources=energy_sources
    )
    
    return motorbike

# Test the function
if __name__ == "__main__":
    import sys
    sys.path.append('/home/teocasares/ithaka-powertrain-sim')
    
    from ithaka_powertrain_sim.component_library.interactive_picker import ComponentPickerState
    from ithaka_powertrain_sim.component_library.motors import Motor_5kW_Hub
    from ithaka_powertrain_sim.component_library.batteries import Battery_5kWh_180WhKg
    
    # Test with EV configuration
    state = ComponentPickerState()
    state.motorcycle_type = "Pure EV"
    state.selected_components = {
        'motor': Motor_5kW_Hub(),
        'battery': Battery_5kWh_180WhKg()
    }
    
    try:
        motorbike = build_motorcycle_from_state_fixed(state)
        print("✅ Fixed motorcycle building successful!")
        print(f"   - Name: {motorbike.name}")
        print(f"   - Mechanical components: {len(motorbike.mechanical_components)}")
        print(f"   - Electrical components: {len(motorbike.electrical_components)}")
        print(f"   - Energy sources: {len(motorbike.energy_sources)}")
    except Exception as e:
        print(f"❌ Fixed motorcycle building failed: {e}")
        import traceback
        traceback.print_exc()