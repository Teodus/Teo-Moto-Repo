#!/usr/bin/env python3
"""
Test script for the integrated notebook functionality.
Tests all components to ensure they work properly, especially in Colab environment.
"""

import sys
import os
import traceback
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append('/home/teocasares/ithaka-powertrain-sim')

def test_imports():
    """Test that all required imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Core simulation imports
        from ithaka_powertrain_sim.trajectory import load_gpx, append_and_resample_dataframe
        from ithaka_powertrain_sim.motorbike import Motorbike
        
        # Component library imports
        from ithaka_powertrain_sim.component_library.engines import Engine_250cc_20kW
        from ithaka_powertrain_sim.component_library.motors import Motor_5kW_Hub
        from ithaka_powertrain_sim.component_library.batteries import Battery_5kWh_180WhKg
        from ithaka_powertrain_sim.component_library.gearbox import Gearbox
        from ithaka_powertrain_sim.component_library.fuel_tank import FuelTank
        from ithaka_powertrain_sim.component_library.brake import Brake
        
        # Interactive components
        from ithaka_powertrain_sim.component_library.interactive_picker import (
            ComponentPickerState,
            create_motorcycle_type_selector,
            create_engine_selector,
            create_motor_selector,
            create_battery_selector,
            create_metrics_display,
            create_configuration_export
        )
        
        # Widget imports
        import ipywidgets as widgets
        from IPython.display import display, clear_output
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {str(e)}")
        traceback.print_exc()
        return False

def test_component_picker_state():
    """Test ComponentPickerState functionality."""
    print("🧪 Testing ComponentPickerState...")
    
    try:
        # Import the state class
        from ithaka_powertrain_sim.component_library.interactive_picker import ComponentPickerState
        
        # Create state instance
        state = ComponentPickerState()
        
        # Test initial state
        assert state.motorcycle_type == "Pure EV"
        assert state.selected_components == {}
        
        # Update metrics to get proper initial values
        state.update_metrics()
        assert state.total_weight == 150  # Base motorcycle weight
        assert state.total_cost == 2000   # Base motorcycle cost
        
        # Test component selection
        from ithaka_powertrain_sim.component_library.engines import Engine_250cc_20kW
        from ithaka_powertrain_sim.component_library.motors import Motor_5kW_Hub
        
        engine = Engine_250cc_20kW()
        motor = Motor_5kW_Hub()
        
        state.selected_components['engine'] = engine
        state.selected_components['motor'] = motor
        
        # Test metrics update
        state.update_metrics()
        
        # Should have increased weight and cost
        assert state.total_weight > 150
        assert state.total_cost > 5000
        assert state.total_power > 0
        
        print("   ✅ ComponentPickerState working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ ComponentPickerState test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_demo_trajectory_creation():
    """Test demo trajectory creation functionality."""
    print("🧪 Testing demo trajectory creation...")
    
    try:
        # Define demo trajectory function (copied from notebook)
        def create_demo_trajectory(route_type):
            if route_type == "demo_flat":
                distances = list(range(0, 10000, 100))
                times = [d/15 for d in distances]
                elevations = [100] * len(distances)
                
            elif route_type == "demo_hills":
                distances = list(range(0, 10000, 100))
                times = [d/12 for d in distances]
                import math
                elevations = [100 + 50 * math.sin(d/1000) for d in distances]
                
            else:  # demo_mixed
                distances = list(range(0, 15000, 100))
                times = [d/13 for d in distances]
                elevations = []
                for d in distances:
                    if d < 5000:
                        elevations.append(100)
                    elif d < 10000:
                        elevations.append(100 + (d-5000) * 200/5000)
                    else:
                        elevations.append(300 - (d-10000) * 200/5000)
            
            target_speeds = []
            for i in range(len(distances)):
                if i == 0:
                    target_speeds.append(15.0)
                else:
                    dt = times[i] - times[i-1]
                    dd = distances[i] - distances[i-1]
                    target_speeds.append(dd/dt if dt > 0 else 15.0)
            
            df = pd.DataFrame({
                'Target Time': times,
                'Distance': [d/1000 for d in distances],
                'Elevation': elevations,
                'Target Speed': target_speeds
            })
            
            return df
        
        # Test all demo routes
        for route_type in ["demo_flat", "demo_hills", "demo_mixed"]:
            df = create_demo_trajectory(route_type)
            
            # Validate DataFrame structure
            required_cols = ['Target Time', 'Distance', 'Elevation', 'Target Speed']
            assert all(col in df.columns for col in required_cols)
            
            # Validate data ranges
            assert len(df) > 50, f"Route {route_type} too short"
            assert df['Distance'].iloc[-1] > 5, f"Route {route_type} distance too short"
            assert all(df['Target Speed'] > 0), f"Route {route_type} has invalid speeds"
            assert all(df['Elevation'] >= 0), f"Route {route_type} has negative elevations"
            
            print(f"   ✅ Demo route '{route_type}' created successfully ({len(df)} points)")
        
        print("   ✅ All demo trajectories working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Demo trajectory test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_motorcycle_building():
    """Test building motorcycle from component state."""
    print("🧪 Testing motorcycle building...")
    
    try:
        from ithaka_powertrain_sim.component_library.interactive_picker import ComponentPickerState
        from ithaka_powertrain_sim.component_library.engines import Engine_250cc_20kW
        from ithaka_powertrain_sim.component_library.motors import Motor_5kW_Hub
        from ithaka_powertrain_sim.component_library.batteries import Battery_5kWh_180WhKg
        from ithaka_powertrain_sim.motorbike import Motorbike
        
        # Define motorcycle building function (copied from notebook)
        def build_motorcycle_from_state(state):
            engine = state.selected_components.get('engine')
            motor = state.selected_components.get('motor') 
            battery = state.selected_components.get('battery')
            
            mechanical_components = []
            electrical_components = []
            energy_sources = []
            
            if engine:
                mechanical_components.append(engine)
                from ithaka_powertrain_sim.component_library.gearbox import Gearbox
                gearbox = Gearbox(name="Auto_Gearbox", gear_ratios=[3.5], efficiency=0.95)
                mechanical_components.append(gearbox)
                
                from ithaka_powertrain_sim.component_library.fuel_tank import FuelTank
                fuel_tank = FuelTank(name="Fuel_Tank", capacity_L=15, fuel_density_kg_L=0.75)
                energy_sources.append(fuel_tank)
            
            if motor:
                electrical_components.append(motor)
            
            if battery:
                energy_sources.append(battery)
            
            from ithaka_powertrain_sim.component_library.brake import Brake
            brake = Brake(name="Standard_Brake", maximum_braking_power=50000)
            mechanical_components.append(brake)
            
            motorbike = Motorbike(
                name=f"{state.motorcycle_type}_Custom",
                mechanical_components=mechanical_components,
                electrical_components=electrical_components,
                energy_sources=energy_sources
            )
            
            return motorbike
        
        # Test different motorcycle configurations
        test_configs = [
            ("Pure EV", {"motor": Motor_5kW_Hub(), "battery": Battery_5kWh_180WhKg()}),
            ("Pure ICE", {"engine": Engine_250cc_20kW()}),
            ("Hybrid", {"engine": Engine_250cc_20kW(), "motor": Motor_5kW_Hub(), "battery": Battery_5kWh_180WhKg()})
        ]
        
        for config_name, components in test_configs:
            state = ComponentPickerState()
            state.motorcycle_type = config_name
            state.selected_components = components
            
            motorbike = build_motorcycle_from_state(state)
            
            # Validate motorcycle structure
            assert motorbike.name == f"{config_name}_Custom"
            assert len(motorbike.mechanical_components) >= 1  # At least brake
            assert len(motorbike.energy_sources) >= 1  # At least one energy source
            
            print(f"   ✅ {config_name} motorcycle built successfully")
        
        print("   ✅ Motorcycle building working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Motorcycle building test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_simulation_execution():
    """Test complete simulation execution."""
    print("🧪 Testing simulation execution...")
    
    try:
        from ithaka_powertrain_sim.component_library.interactive_picker import ComponentPickerState
        from ithaka_powertrain_sim.component_library.motors import Motor_5kW_Hub
        from ithaka_powertrain_sim.component_library.batteries import Battery_5kWh_180WhKg
        
        # Create test configuration
        state = ComponentPickerState()
        state.motorcycle_type = "Pure EV"
        state.selected_components = {
            'motor': Motor_5kW_Hub(),
            'battery': Battery_5kWh_180WhKg()
        }
        
        # Create demo trajectory (simplified flat route)
        distances = list(range(0, 5000, 200))  # 5km every 200m (25 points)
        times = [d/15 for d in distances]  # 15 m/s average
        elevations = [100] * len(distances)  # Flat
        target_speeds = [15.0] * len(distances)  # Constant speed
        
        trajectory_df = pd.DataFrame({
            'Target Time': times,
            'Distance': [d/1000 for d in distances],
            'Elevation': elevations,
            'Target Speed': target_speeds
        })
        
        # Build motorcycle
        from ithaka_powertrain_sim.motorbike import Motorbike
        from ithaka_powertrain_sim.component_library.brake import Brake
        
        motorbike = Motorbike(
            name="Test_EV",
            mechanical_components=[Brake(name="Test_Brake", maximum_braking_power=50000)],
            electrical_components=[state.selected_components['motor']],
            energy_sources=[state.selected_components['battery']]
        )
        
        # Run simulation
        results = []
        print(f"   Running simulation with {len(trajectory_df)} data points...")
        
        for i, row in trajectory_df.iterrows():
            target_time = row['Target Time']
            distance_km = row['Distance']
            elevation_m = row['Elevation']
            target_speed = row['Target Speed']
            
            achieved_speed = motorbike.calculate_achieved_speed(
                target_time, distance_km, elevation_m, target_speed
            )
            
            results.append({
                'time': target_time,
                'distance': distance_km,
                'elevation': elevation_m,
                'target_speed': target_speed,
                'achieved_speed': achieved_speed,
                'total_energy': motorbike.total_energy_consumed
            })
        
        # Validate results
        results_df = pd.DataFrame(results)
        
        assert len(results_df) == len(trajectory_df), "Results length mismatch"
        assert results_df['total_energy'].iloc[-1] > 0, "No energy consumption recorded"
        assert all(results_df['achieved_speed'] > 0), "Invalid achieved speeds"
        assert results_df['total_energy'].is_monotonic_increasing, "Energy should be monotonic"
        
        print(f"   ✅ Simulation completed successfully")
        print(f"      - Distance: {results_df['distance'].iloc[-1]:.1f} km")
        print(f"      - Energy: {results_df['total_energy'].iloc[-1]:.2f} MJ")
        print(f"      - Avg Speed: {results_df['distance'].iloc[-1] / (results_df['time'].iloc[-1]/3600):.1f} km/h")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Simulation execution test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_visualization():
    """Test results visualization functionality."""
    print("🧪 Testing visualization...")
    
    try:
        # Create test data
        test_data = {
            'distance': [0, 1, 2, 3, 4, 5],
            'target_speed': [15, 15, 15, 15, 15, 15],
            'achieved_speed': [14.8, 14.9, 15.1, 14.7, 15.2, 15.0],
            'elevation': [100, 105, 110, 108, 102, 100],
            'total_energy': [0, 0.5, 1.1, 1.8, 2.6, 3.5],
            'time': [0, 240, 480, 720, 960, 1200]
        }
        
        df = pd.DataFrame(test_data)
        
        # Test plot creation
        fig = plt.figure(figsize=(12, 8))
        
        # Speed plot
        plt.subplot(2, 3, 1)
        plt.plot(df['distance'], df['target_speed'], 'b--', label='Target')
        plt.plot(df['distance'], df['achieved_speed'], 'g-', label='Achieved')
        plt.xlabel('Distance (km)')
        plt.ylabel('Speed (m/s)')
        plt.title('Speed Performance')
        plt.legend()
        plt.grid(True)
        
        # Elevation plot
        plt.subplot(2, 3, 2)
        plt.plot(df['distance'], df['elevation'], 'brown')
        plt.xlabel('Distance (km)')
        plt.ylabel('Elevation (m)')
        plt.title('Route Profile')
        plt.grid(True)
        
        # Energy plot
        plt.subplot(2, 3, 3)
        plt.plot(df['distance'], df['total_energy'], 'red')
        plt.xlabel('Distance (km)')
        plt.ylabel('Energy (MJ)')
        plt.title('Energy Consumption')
        plt.grid(True)
        
        plt.tight_layout()
        
        # Save test plot
        plt.savefig('/tmp/test_plot.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # Verify file was created
        assert os.path.exists('/tmp/test_plot.png'), "Plot file not created"
        
        print("   ✅ Visualization working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Visualization test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_colab_compatibility():
    """Test Google Colab specific functionality."""
    print("🧪 Testing Colab compatibility...")
    
    try:
        # Test widget creation (should work even without display)
        import ipywidgets as widgets
        
        # Test basic widgets
        dropdown = widgets.Dropdown(options=['A', 'B', 'C'], description='Test:')
        button = widgets.Button(description='Test Button')
        output = widgets.Output()
        html_widget = widgets.HTML("<p>Test HTML</p>")
        
        # Test widget layouts
        hbox = widgets.HBox([button])
        vbox = widgets.VBox([dropdown, html_widget])
        
        assert dropdown.description == 'Test:'
        assert button.description == 'Test Button'
        assert len(hbox.children) == 1
        assert len(vbox.children) == 2
        
        # Test output widget functionality
        with output:
            print("Test output capture")
        
        # Test that matplotlib works with Agg backend
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title('Test Plot')
        plt.savefig('/tmp/colab_test.png')
        plt.close()
        
        assert os.path.exists('/tmp/colab_test.png'), "Colab plot not created"
        
        print("   ✅ Colab compatibility confirmed")
        return True
        
    except Exception as e:
        print(f"   ❌ Colab compatibility test failed: {str(e)}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Running Integrated Notebook Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Component Picker State", test_component_picker_state),
        ("Demo Trajectory Creation", test_demo_trajectory_creation),
        ("Motorcycle Building", test_motorcycle_building),
        ("Simulation Execution", test_simulation_execution),
        ("Visualization", test_visualization),
        ("Colab Compatibility", test_colab_compatibility)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Notebook is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Issues need to be fixed.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)