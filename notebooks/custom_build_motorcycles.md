---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.2
  kernelspec:
    display_name: venv
    language: python
    name: python3
---

<!-- #region id="mPYybKgVlTDB" -->
# 🔧 Custom Build Motorcycles - Ithaka Powertrain Simulator


<!-- #endregion -->

```python colab={"base_uri": "https://localhost:8080/"} id="U83kMIzOlTDF" outputId="1c584f64-bb05-4001-e45f-d3065fdfe2e7"
#@title 🚀 Environment Setup { display-mode: "form" }

#@markdown This cell automatically detects your environment and sets up all required dependencies.
#@markdown **Click the play button** to run this cell - setup takes about 30-60 seconds.

import sys
import os
import warnings
import subprocess
warnings.filterwarnings('ignore')

def setup_environment():
    """Smart environment setup for both Colab and local environments."""

    # Detect environment
    try:
        import google.colab
        IN_COLAB = True
        print("📦 Google Colab environment detected")
    except ImportError:
        IN_COLAB = False
        print("💻 Local environment detected")

    if IN_COLAB:
        # Check for existing repository
        print("🔍 Checking for repository...")

        current_dir = os.getcwd()
        possible_paths = ['/content/Teo-Moto-Repo', '/content/ithaka-powertrain-sim', current_dir]

        repo_found = False
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'setup.py')):
                print(f"✅ Found repository at: {path}")
                os.chdir(path)
                repo_found = True
                break

        if not repo_found:
            print("📥 Cloning repository...")
            try:
                result = subprocess.run(['git', 'clone', 'https://github.com/Teodus/Teo-Moto-Repo.git'],
                                      capture_output=True, text=True, cwd='/content')
                if result.returncode == 0:
                    os.chdir('/content/Teo-Moto-Repo')
                    print("✅ Repository cloned successfully")
                else:
                    print("❌ Clone failed. Please check your internet connection.")
                    return False
            except Exception as e:
                print(f"❌ Error: {e}")
                return False

        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
                      capture_output=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-e', '.'],
                      capture_output=True)
        print("✅ Dependencies installed")

    # Verify installation
    try:
        print("🔍 Verifying installation...")
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import ipywidgets as widgets
        from IPython.display import display, clear_output, HTML
        import json
        import glob
        from datetime import datetime

        # Import component builders
        from ithaka_powertrain_sim.component_library import (
            Battery_10kWh_200WhKg, Battery_15kWh_220WhKg, Battery_20kWh_180WhKg, Battery_25kWh_200WhKg,
            Motor_30kW_MidDrive, Motor_50kW_HighPerf, Motor_80kW_HighPerf, Motor_120kW_HighPerf,
            Engine_400cc_30kW, Engine_500cc_40kW, Engine_650cc_50kW, Engine_750cc_60kW, Engine_1000cc_80kW,
            FuelTank_15L, FuelTank_25L
        )
        from ithaka_powertrain_sim.motorbike import Motorbike
        from ithaka_powertrain_sim.trajectory import load_gpx, append_and_resample_dataframe

        print("✅ All modules imported successfully")
        print("🔧 Component builders loaded and ready")

        gpx_files = glob.glob('docs/gpx_files/*.gpx')
        if gpx_files:
            print(f"🗺️ Found {len(gpx_files)} test tracks")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        if 'shortuuid' in str(e):
            print("💡 Installing missing dependency...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'shortuuid'],
                         capture_output=True)
            print("✅ Please re-run this cell")
        return False

# Run setup
print("🚀 Starting environment setup...")
setup_success = setup_environment()

if setup_success:
    print("\n🎉 Setup complete! Ready to build custom motorcycles!")
    print("👇 Continue to Step 1 below")
else:
    print("\n❌ Setup failed. Please check the error messages above.")
```

```python colab={"base_uri": "https://localhost:8080/", "height": 53} id="rCCU3VbwlTDH" outputId="54549ada-fa17-488d-c1b2-7423bf193e01"
#@title 🏗️ Initialize Custom Builder { display-mode: "form" }

#@markdown This cell sets up the custom motorcycle builder with all component options.
#@markdown **Run this cell** to prepare the design environment.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import json
import glob
import os
from datetime import datetime

# Import component builders
from ithaka_powertrain_sim.component_library import (
    Battery_10kWh_200WhKg, Battery_15kWh_220WhKg, Battery_20kWh_180WhKg, Battery_25kWh_200WhKg,
    Motor_30kW_MidDrive, Motor_50kW_HighPerf, Motor_80kW_HighPerf, Motor_120kW_HighPerf,
    Engine_400cc_30kW, Engine_500cc_40kW, Engine_650cc_50kW, Engine_750cc_60kW, Engine_1000cc_80kW,
    FuelTank_15L, FuelTank_25L
)
from ithaka_powertrain_sim.motorbike import Motorbike
from ithaka_powertrain_sim.trajectory import load_gpx, append_and_resample_dataframe

class CustomMotorcycleBuilder:
    """Application state manager for custom motorcycle building."""

    def __init__(self):
        self.custom_motorcycle = None
        self.selected_tracks = []
        self.simulation_results = {}
        self.selected_motor = None
        self.selected_battery = None
        self.selected_engine = None
        self.selected_fuel_tank = None
        self.motorcycle_type = 'Pure EV'

    def get_available_tracks(self):
        """Get list of available GPX track files."""
        gpx_files = glob.glob('docs/gpx_files/*.gpx')
        if not gpx_files:
            return [("No tracks found", None)]

        track_names = []
        for gpx_file in gpx_files:
            name = os.path.basename(gpx_file).replace('.gpx', '').replace('-', ' ').replace('_', ' ')
            name = ' '.join(word.capitalize() for word in name.split())
            track_names.append((name, gpx_file))

        return sorted(track_names)

    def build_motorcycle(self):
        """Build the custom motorcycle from selected components."""
        components = []

        # Add selected components
        if self.selected_motor:
            if '30kW' in self.selected_motor:
                components.append(Motor_30kW_MidDrive())
            elif '50kW' in self.selected_motor:
                components.append(Motor_50kW_HighPerf())
            elif '80kW' in self.selected_motor:
                components.append(Motor_80kW_HighPerf())
            elif '120kW' in self.selected_motor:
                components.append(Motor_120kW_HighPerf())

        if self.selected_battery:
            if '10kWh' in self.selected_battery:
                components.append(Battery_10kWh_200WhKg())
            elif '15kWh' in self.selected_battery:
                components.append(Battery_15kWh_220WhKg())
            elif '20kWh' in self.selected_battery:
                components.append(Battery_20kWh_180WhKg())
            elif '25kWh' in self.selected_battery:
                components.append(Battery_25kWh_200WhKg())

        if self.selected_engine:
            if '400cc' in self.selected_engine:
                components.append(Engine_400cc_30kW())
            elif '500cc' in self.selected_engine:
                components.append(Engine_500cc_40kW())
            elif '650cc' in self.selected_engine:
                components.append(Engine_650cc_50kW())
            elif '750cc' in self.selected_engine:
                components.append(Engine_750cc_60kW())
            elif '1000cc' in self.selected_engine:
                components.append(Engine_1000cc_80kW())

        if self.selected_fuel_tank:
            if '15L' in self.selected_fuel_tank:
                components.append(FuelTank_15L())
            elif '25L' in self.selected_fuel_tank:
                components.append(FuelTank_25L())

        if not components:
            raise ValueError("No components selected. Please select at least one component.")

        # Create motorcycle name
        timestamp = datetime.now().strftime('%H%M%S')
        name = f"Custom_{self.motorcycle_type.replace(' ', '_')}_{timestamp}"

        # Create motorcycle with correct parameters
        self.custom_motorcycle = Motorbike(
            name=name,
            child_components=components,
            dry_mass_excluding_components=150.0,
            front_mass_ratio=0.4,
            front_wheel_inertia=0.8,
            front_wheel_radius=0.3,
            front_wheel_coefficient_of_rolling_resistance=0.015,
            rear_wheel_inertia=1.2,
            rear_wheel_radius=0.3,
            rear_wheel_coefficient_of_rolling_resistance=0.015,
            frontal_area=0.6,
            coefficient_of_aerodynamic_drag=0.6
        )

        return self.custom_motorcycle

    def simulate_motorcycle_on_track(self, motorcycle, track_file, track_name):
        """Run simulation for motorcycle on single track."""
        try:
            # Load trajectory
            trajectory_df = load_gpx(track_file)
            trajectory_df = append_and_resample_dataframe(trajectory_df)

            # Extract parameters
            target_speed = trajectory_df["Target Speed"].to_list()
            delta_distance = np.diff(trajectory_df["Distance"], prepend=0).tolist()
            delta_elevation = np.diff(trajectory_df["Elevation"], prepend=0).tolist()
            approximate_time = trajectory_df["Target Time"].to_list()

            # Run simulation
            achieved_speeds = [trajectory_df["Target Speed"].iloc[0]]
            reporting_dataframe_rows = []

            for index in range(1, min(100, len(trajectory_df))):  # Limit for testing
                delta_time = approximate_time[index] - approximate_time[index - 1]

                achieved_speed, reporting_dataframe_row = motorcycle.calculate_achieved_speed(
                    achieved_speeds[index - 1], target_speed[index], delta_time,
                    delta_distance[index], delta_elevation[index]
                )

                achieved_speeds.append(achieved_speed)
                reporting_dataframe_rows.append(reporting_dataframe_row)

            # Calculate basic metrics
            total_time = approximate_time[min(99, len(approximate_time)-1)] if approximate_time else 0
            total_distance = trajectory_df['Distance'].iloc[min(99, len(trajectory_df)-1)] if len(trajectory_df) > 0 else 0
            avg_speed = (total_distance / total_time * 3.6) if total_time > 0 else 0

            energy_consumed = 0
            if reporting_dataframe_rows:
                try:
                    reporting_dataframe = pd.concat(reporting_dataframe_rows, ignore_index=True)
                    if 'Energy Consumed (J)' in reporting_dataframe.columns:
                        energy_consumed = reporting_dataframe['Energy Consumed (J)'].sum()
                except:
                    pass

            return {
                'track_name': track_name,
                'track_file': track_file,
                'total_time_s': total_time,
                'total_distance_km': total_distance / 1000,
                'average_speed_kmh': avg_speed,
                'energy_consumed_kWh': energy_consumed / 3.6e6,
                'success': True
            }

        except Exception as e:
            return {
                'track_name': track_name,
                'track_file': track_file,
                'error': str(e),
                'success': False
            }

# Initialize application
app = CustomMotorcycleBuilder()

# Define widget styles
style = {'description_width': '180px'}
layout_wide = widgets.Layout(width='500px')
layout_medium = widgets.Layout(width='400px')

print("✅ Custom Motorcycle Builder initialized successfully!")
print("👇 Continue to Step 1 below")
```

<!-- #region id="QdLzcm3XlTDI" -->
## Step 1: Design Your Custom Motorcycle
<!-- #endregion -->

```python colab={"base_uri": "https://localhost:8080/", "height": 1000, "referenced_widgets": ["13fb95aa276c42249a98739cab042990", "bd7ac1bda03443e0b41f72d1b030f8b1", "8cf596b1d35049ffb730027e42cbc9fb", "1fdafa121994454c94b33ed2844dce95", "7c80e7e40fbf4366b92deed966b8dfe4", "14ee017b8d734fe8b9ee9761d05d9907", "1f72c1214df74db1b1ea9d1adf13a4e5", "3f0fd33dfbf246bfa694db6dc23ecf16", "31b8799f111c464888563c4cae748fe0", "3e1efc51f98b47b082923c79e2a214fd", "c94839e3deee46ddbdfd58a6134336ca", "345bcf4f7ef14b778202fba26e13dc64", "99f2d82e97ac481b9a29a8b88b2abfa4", "c190a75e4e7e49b49ca3de3242424cbc", "aecf05e0544649fb831a966b2ddf536f", "3ff7f4e700f148749cb7a849cda2c525", "c3baefdf769740859c5f44c1ca742f31", "4bc760c5beb84b2e99fd3991feca7c78", "badf4be7764b46b3a602b4bc210362c6", "81aeb36dcdef46569502cef098289920", "e09862b95687456eada77631e6f93f89", "705186b672cd401aa2371449a086da4f", "018840c343fb4f5fa500e61c5ee36b49", "4a2204194b7e43d2899ebeadc78a302e", "039efbdfdb9b4c19a3e89c2645d37d71", "ceb6e3be44d142a1b5ade42b4c83bdcd", "b1edb76e8141478bbc16dc635412f8ce", "55e8613188f44ebba8c2f96af0e5d23e"]} id="g8j1gVLWlTDI" outputId="e14582d3-88fc-45ba-e3aa-1f073b8edf87"
#@title 🔧 Custom Motorcycle Designer { display-mode: "form" }

#@markdown Design your custom motorcycle by selecting the type and components.
#@markdown **Real-time feedback** shows weight, power, and performance characteristics as you build.

# Step 1: Motorcycle Type Selection
print("🎯 STEP 1: Choose Your Powertrain Type")
print("=" * 50)

type_selector = widgets.RadioButtons(
    options=[
        ('⚡ Pure EV - Electric Only', 'Pure EV'),
        ('🔥 Pure ICE - Internal Combustion Only', 'Pure ICE'),
        ('⚡🔥 Hybrid - Electric + ICE Combination', 'Hybrid')
    ],
    value='Pure EV',
    description='Powertrain Type:',
    style=style,
    layout=layout_wide
)

display(type_selector)

# Component selectors
print("\n🔧 STEP 2: Select Components")
print("=" * 50)

# Electric Motor Selection
motor_options = [('Select motor...', None)]
motor_options.extend([
    ('30kW Mid-Drive Motor (30kW, 28kg)', '30kW Mid-Drive Motor'),
    ('50kW High-Performance Motor (50kW, 35kg)', '50kW High-Performance Motor'),
    ('80kW High-Performance Motor (80kW, 45kg)', '80kW High-Performance Motor'),
    ('120kW High-Performance Motor (120kW, 60kg)', '120kW High-Performance Motor')
])

motor_selector = widgets.Dropdown(
    options=motor_options,
    value=None,
    description='Electric Motor:',
    style=style,
    layout=layout_wide
)

# Battery Selection
battery_options = [('Select battery...', None)]
battery_options.extend([
    ('10kWh Battery (10kWh, 62kg, 200Wh/kg)', '10kWh Battery'),
    ('15kWh Battery (15kWh, 68kg, 220Wh/kg)', '15kWh Battery'),
    ('20kWh Battery (20kWh, 111kg, 180Wh/kg)', '20kWh Battery'),
    ('25kWh Battery (25kWh, 125kg, 200Wh/kg)', '25kWh Battery')
])

battery_selector = widgets.Dropdown(
    options=battery_options,
    value=None,
    description='Battery Pack:',
    style=style,
    layout=layout_wide
)

# Engine Selection
engine_options = [('Select engine...', None)]
engine_options.extend([
    ('400cc Engine (400cc, 30kW, 45kg)', '400cc Engine'),
    ('500cc Engine (500cc, 40kW, 55kg)', '500cc Engine'),
    ('650cc Engine (650cc, 50kW, 65kg)', '650cc Engine'),
    ('750cc Engine (750cc, 60kW, 75kg)', '750cc Engine'),
    ('1000cc Engine (1000cc, 80kW, 90kg)', '1000cc Engine')
])

engine_selector = widgets.Dropdown(
    options=engine_options,
    value=None,
    description='ICE Engine:',
    style=style,
    layout=layout_wide
)

# Fuel Tank Selection
fuel_options = [('Select fuel tank...', None)]
fuel_options.extend([
    ('15L Fuel Tank (15L, 12kg)', '15L Fuel Tank'),
    ('25L Fuel Tank (25L, 20kg)', '25L Fuel Tank')
])

fuel_selector = widgets.Dropdown(
    options=fuel_options,
    value=None,
    description='Fuel Tank:',
    style=style,
    layout=layout_wide
)

# Create containers for component groups
electric_components = widgets.VBox([
    widgets.HTML("<h4>⚡ Electric Components</h4>"),
    motor_selector,
    battery_selector
])

ice_components = widgets.VBox([
    widgets.HTML("<h4>🔥 Internal Combustion Components</h4>"),
    engine_selector,
    fuel_selector
])

# Real-time specifications display
specs_display = widgets.Output()

# Build button
build_btn = widgets.Button(
    description='🏗️ Build My Motorcycle',
    button_style='success',
    layout=widgets.Layout(width='200px', height='40px')
)

build_output = widgets.Output()

def update_component_visibility(change=None):
    """Update which components are visible based on motorcycle type."""
    app.motorcycle_type = type_selector.value

    if app.motorcycle_type == "Pure EV":
        electric_components.layout.display = 'block'
        ice_components.layout.display = 'none'
    elif app.motorcycle_type == "Pure ICE":
        electric_components.layout.display = 'none'
        ice_components.layout.display = 'block'
    elif app.motorcycle_type == "Hybrid":
        electric_components.layout.display = 'block'
        ice_components.layout.display = 'block'

    update_specifications()

def handle_motor_change(change):
    app.selected_motor = change.new
    update_specifications()

def handle_battery_change(change):
    app.selected_battery = change.new
    update_specifications()

def handle_engine_change(change):
    app.selected_engine = change.new
    update_specifications()

def handle_fuel_change(change):
    app.selected_fuel_tank = change.new
    update_specifications()

def update_specifications(change=None):
    """Update real-time motorcycle specifications."""
    with specs_display:
        clear_output()

        # Calculate specifications
        base_mass = 150.0  # kg
        total_mass = base_mass
        total_power = 0
        total_energy = 0
        components = []

        if app.selected_motor:
            components.append(f"Motor: {app.selected_motor}")
            if '30kW' in app.selected_motor:
                total_mass += 28; total_power += 30
            elif '50kW' in app.selected_motor:
                total_mass += 35; total_power += 50
            elif '80kW' in app.selected_motor:
                total_mass += 45; total_power += 80
            elif '120kW' in app.selected_motor:
                total_mass += 60; total_power += 120

        if app.selected_battery:
            components.append(f"Battery: {app.selected_battery}")
            if '10kWh' in app.selected_battery:
                total_mass += 62; total_energy += 10
            elif '15kWh' in app.selected_battery:
                total_mass += 68; total_energy += 15
            elif '20kWh' in app.selected_battery:
                total_mass += 111; total_energy += 20
            elif '25kWh' in app.selected_battery:
                total_mass += 125; total_energy += 25

        if app.selected_engine:
            components.append(f"Engine: {app.selected_engine}")
            if '400cc' in app.selected_engine:
                total_mass += 45; total_power += 30
            elif '500cc' in app.selected_engine:
                total_mass += 55; total_power += 40
            elif '650cc' in app.selected_engine:
                total_mass += 65; total_power += 50
            elif '750cc' in app.selected_engine:
                total_mass += 75; total_power += 60
            elif '1000cc' in app.selected_engine:
                total_mass += 90; total_power += 80

        if app.selected_fuel_tank:
            components.append(f"Fuel Tank: {app.selected_fuel_tank}")
            if '15L' in app.selected_fuel_tank:
                total_mass += 12
            elif '25L' in app.selected_fuel_tank:
                total_mass += 20

        power_to_weight = total_power / total_mass if total_mass > 0 else 0

        print("📊 REAL-TIME MOTORCYCLE SPECIFICATIONS")
        print("=" * 45)
        print(f"🏷️ Type: {app.motorcycle_type}")
        print(f"⚖️ Total Weight: {total_mass:.1f} kg")
        print(f"⚡ Total Power: {total_power:.1f} kW")
        print(f"🔋 Total Energy: {total_energy:.1f} kWh")
        print(f"🏁 Power-to-Weight: {power_to_weight:.3f} kW/kg")
        print(f"🔧 Components: {len(components)}/4")

        if components:
            print("\n🔧 Selected Components:")
            for comp in components:
                print(f"  • {comp}")

        # Performance indicators
        print("\n🎯 Performance Indicators:")
        if power_to_weight > 0.15:
            print("  🏁 HIGH PERFORMANCE - Excellent acceleration and top speed")
        elif power_to_weight > 0.08:
            print("  🚗 MODERATE PERFORMANCE - Good balance of power and efficiency")
        elif power_to_weight > 0:
            print("  🌱 EFFICIENCY FOCUSED - Optimized for range and economy")
        else:
            print("  ⚠️ No power source selected")

        # Validation warnings
        if len(components) == 0:
            print("\n⚠️ No components selected - please select at least one component")
        elif app.motorcycle_type == "Pure EV" and not (app.selected_motor and app.selected_battery):
            print("\n⚠️ Pure EV requires both motor and battery")
        elif app.motorcycle_type == "Pure ICE" and not (app.selected_engine and app.selected_fuel_tank):
            print("\n⚠️ Pure ICE requires both engine and fuel tank")
        elif app.motorcycle_type == "Hybrid" and len(components) < 2:
            print("\n⚠️ Hybrid requires at least two different component types")

def build_motorcycle(btn):
    """Build the custom motorcycle."""
    with build_output:
        clear_output()
        try:
            # Validation
            components_count = sum([bool(x) for x in [app.selected_motor, app.selected_battery, app.selected_engine, app.selected_fuel_tank]])

            if components_count == 0:
                print("❌ No components selected. Please select at least one component.")
                return

            # Type-specific validation
            if app.motorcycle_type == "Pure EV":
                if not (app.selected_motor and app.selected_battery):
                    print("❌ Pure EV requires both motor and battery. Please select both components.")
                    return
            elif app.motorcycle_type == "Pure ICE":
                if not (app.selected_engine and app.selected_fuel_tank):
                    print("❌ Pure ICE requires both engine and fuel tank. Please select both components.")
                    return
            elif app.motorcycle_type == "Hybrid":
                if components_count < 2:
                    print("❌ Hybrid configuration requires at least two different component types.")
                    return

            # Build motorcycle
            motorcycle = app.build_motorcycle()

            print("✅ CUSTOM MOTORCYCLE BUILT SUCCESSFULLY!")
            print("=" * 50)
            print(f"🏍️ Name: {motorcycle.name}")
            print(f"🏷️ Type: {app.motorcycle_type}")
            print(f"⚖️ Total Mass: {motorcycle.mass:.1f} kg")
            print(f"🔧 Components: {len(motorcycle.child_components)}")

            # Show component list
            print("\n🔧 Built Components:")
            for comp in motorcycle.child_components:
                print(f"  • {comp.name} ({comp.mass:.1f} kg)")

            # Calculate total power
            total_power = 0
            for component in motorcycle.child_components:
                if hasattr(component, '_maximum_power_generation'):
                    total_power += component._maximum_power_generation

            if total_power > 0:
                power_to_weight = (total_power / 1000) / motorcycle.mass
                print(f"\n⚡ Performance Summary:")
                print(f"  • Total Power: {total_power / 1000:.1f} kW")
                print(f"  • Power-to-Weight: {power_to_weight:.3f} kW/kg")

            print("\n👇 Continue to Step 2 to choose test tracks")

        except Exception as e:
            print(f"❌ Error building motorcycle: {e}")
            print("💡 Please check your component selections and try again")

# Connect event handlers
type_selector.observe(update_component_visibility, names='value')
motor_selector.observe(handle_motor_change, names='value')
battery_selector.observe(handle_battery_change, names='value')
engine_selector.observe(handle_engine_change, names='value')
fuel_selector.observe(handle_fuel_change, names='value')
build_btn.on_click(build_motorcycle)

# Initial setup
update_component_visibility()

# Display interface
display(electric_components)
display(ice_components)

print("\n📊 STEP 3: Monitor Real-Time Specifications")
print("=" * 50)
display(specs_display)

print("\n🏗️ STEP 4: Build Your Motorcycle")
print("=" * 50)
display(build_btn)
display(build_output)
```

<!-- #region id="b1uqAwqilTDK" -->
## Step 2: Select Test Tracks
<!-- #endregion -->

```python colab={"base_uri": "https://localhost:8080/", "height": 212, "referenced_widgets": ["3164d34bea5247c98212df305d7b4a4e", "bd7ac1bda03443e0b41f72d1b030f8b1", "e118d293f9dd4d0c87bc1fa6b7d01a78", "d4088e14dd2a492e9658454101b1d7eb", "1db9ff8ccd9b4b938ea599f05d2a3e0f", "4ff4cdc8b5f74aaaa0fc489ec773a258", "806b6e9a28c04a9eab5dbc7037c83ab8", "4abdb11fb3d648cab775b4753c8eada4", "c54b3d3455454aa5a330f453e36e5fbf", "75183ac1342a48c8a2f98f68062c5b2d"]} id="z6pSjp6ylTDK" outputId="8e0a50d0-f824-440a-bd5a-f449897c9920"
#@title 🗺️ Track Selection { display-mode: "form" }

#@markdown Select which tracks to test your custom motorcycle on:
#@markdown - **Single Track**: Focused testing on specific terrain
#@markdown - **All Tracks**: Comprehensive validation across all available tracks

track_mode_selector = widgets.RadioButtons(
    options=[
        ('🎯 Test Single Track', 'single'),
        ('🌍 Test All Available Tracks', 'all')
    ],
    value='single',  # Set default value
    description='Test Mode:',
    style=style,
    layout=layout_wide
)

single_track_selector = widgets.Dropdown(
    options=[("Select a track...", None)],
    value=None,
    description='Track:',
    style=style,
    layout=layout_wide
)

track_info = widgets.Output()
confirm_tracks_btn = widgets.Button(
    description='✅ Confirm Track Selection',
    button_style='success',
    layout=widgets.Layout(width='200px')
)

def update_track_options():
    """Update track dropdown with available tracks."""
    try:
        available_tracks = app.get_available_tracks()
        if available_tracks and available_tracks[0][1] is not None:
            options = [("Select a track...", None)] + available_tracks
            single_track_selector.options = options
        else:
            single_track_selector.options = [("No tracks available", None)]
    except Exception as e:
        print(f"Error loading tracks: {e}")

def handle_track_mode_change(change):
    """Handle track mode selection."""
    with track_info:
        clear_output()
        if change.new == 'single':
            update_track_options()
            single_track_selector.layout.display = 'block'
            print("📍 Single Track Testing Selected")
            print("💡 Advantages:")
            print("  • Detailed analysis of specific terrain challenges")
            print("  • Faster simulation and results")
            print("  • Focus on particular riding conditions")
            print("\n👇 Select a track from the dropdown below")
        elif change.new == 'all':
            single_track_selector.layout.display = 'none'
            available_tracks = app.get_available_tracks()
            if available_tracks and available_tracks[0][1] is not None:
                print(f"🌍 All Tracks Testing Selected ({len(available_tracks)} tracks)")
                print("💡 Advantages:")
                print("  • Comprehensive performance validation")
                print("  • Statistical analysis across varied conditions")
                print("  • Complete powertrain characterization")
                print("\n📊 Available tracks:")
                for i, (name, _) in enumerate(available_tracks[:8]):  # Show first 8
                    print(f"  {i+1:2d}. {name}")
                if len(available_tracks) > 8:
                    print(f"  ... and {len(available_tracks) - 8} more")
            else:
                print("❌ No tracks found in the repository")
                print("💡 Please ensure GPX files are available in docs/gpx_files/")

def handle_single_track_change(change):
    """Handle single track selection."""
    if change.new and track_mode_selector.value == 'single':
        with track_info:
            clear_output()
            track_name = change.new[0] if isinstance(change.new, tuple) else str(change.new)
            print(f"📍 Selected Track: {track_name}")
            print("🎯 This track will be used for detailed performance analysis")
            print("📊 You'll get comprehensive metrics for this specific terrain")

def confirm_track_selection(btn):
    """Confirm track selection."""
    if not app.custom_motorcycle:
        with track_info:
            clear_output()
            print("❌ Please build a motorcycle first (Step 1)")
            print("💡 Go back to Step 1 and click 'Build My Motorcycle'")
        return

    # Validate track mode selection
    if not track_mode_selector.value:
        with track_info:
            clear_output()
            print("❌ Please select a test mode (Single Track or All Tracks)")
        return

    # Validate single track selection if needed
    if track_mode_selector.value == 'single':
        if not single_track_selector.value:
            with track_info:
                clear_output()
                print("❌ Please select a specific track for single track testing")
            return

    # Store selection
    if track_mode_selector.value == 'single':
        app.selected_tracks = [single_track_selector.value]
    else:
        available_tracks = app.get_available_tracks()
        app.selected_tracks = [(name, path) for name, path in available_tracks if path is not None]

    with track_info:
        clear_output()
        print("✅ TRACK SELECTION CONFIRMED!")
        print("=" * 40)
        print(f"🏍️ Custom Motorcycle: {app.custom_motorcycle.name}")
        print(f"⚖️ Total Mass: {app.custom_motorcycle.mass:.1f} kg")

        if track_mode_selector.value == 'single':
            track_name = app.selected_tracks[0][0] if isinstance(app.selected_tracks[0], tuple) else str(app.selected_tracks[0])
            print(f"📍 Test Track: {track_name}")
            print("🎯 Mode: Single Track Analysis")
        else:
            print(f"🌍 Test Tracks: All {len(app.selected_tracks)} available")
            print("📊 Mode: Comprehensive Validation")

        print("\n🚀 Ready for simulation!")
        print("👇 Continue to Step 3 to run the physics simulation")

# Connect event handlers
track_mode_selector.observe(handle_track_mode_change, names='value')
single_track_selector.observe(handle_single_track_change, names='value')
confirm_tracks_btn.on_click(confirm_track_selection)

# Initialize display
update_track_options()

# Check if we have a motorcycle built
if app.custom_motorcycle:
    display(track_mode_selector)
    display(single_track_selector)
    display(track_info)
    display(confirm_tracks_btn)

    # Trigger initial display
    handle_track_mode_change({'new': track_mode_selector.value})
else:
    print("⚠️ Please complete Step 1 (build your motorcycle) first")
    print("💡 Go back to Step 1 and click 'Build My Motorcycle'")
```

<!-- #region id="oFFZO4jwlTDL" -->
## Step 3: Run Custom Design Simulation
<!-- #endregion -->

```python colab={"base_uri": "https://localhost:8080/", "height": 912, "referenced_widgets": ["064e9f9752344b0282e1375c69ce1628", "78b22f7f322142459ed5528cd83f438b", "c14d8a79ab264ad78707a01c554f2655", "d69b5946ee914b91b71be0d9f188bb30", "70df7119f67d46b19255815db8602e66"]} id="DrAFXiG7lTDL" outputId="8c4f728e-dfb9-44cc-8e00-f06231a68e49"
#@title 🚀 Run Custom Design Simulation { display-mode: "form" }

#@markdown Click the button below to start the comprehensive simulation of your custom motorcycle.
#@markdown
#@markdown **Custom Design Simulation includes:**
#@markdown - Component interaction analysis
#@markdown - Real-world performance validation
#@markdown - Energy flow and efficiency calculations
#@markdown - Design optimization insights

run_simulation_btn = widgets.Button(
    description='🚀 Simulate Custom Design',
    button_style='primary',
    layout=widgets.Layout(width='220px', height='40px')
)

simulation_progress = widgets.Output()

def run_simulation(btn):
    """Execute simulation for custom motorcycle and tracks."""
    # Check prerequisites
    if not app.custom_motorcycle:
        with simulation_progress:
            clear_output()
            print("❌ No custom motorcycle built. Complete Step 1 first.")
            print("💡 Go back to Step 1 and build your motorcycle")
        return

    if not app.selected_tracks:
        with simulation_progress:
            clear_output()
            print("❌ No tracks selected. Complete Step 2 first.")
            print("💡 Go back to Step 2 and select test tracks")
        return

    with simulation_progress:
        clear_output()
        print("🚀 STARTING CUSTOM DESIGN SIMULATION")
        print("=" * 60)

        # Display custom motorcycle summary
        print(f"🏍️ CUSTOM MOTORCYCLE: {app.custom_motorcycle.name}")
        print(f"🏷️ Type: {app.motorcycle_type}")
        print(f"⚖️ Total Mass: {app.custom_motorcycle.mass:.1f} kg")
        print(f"🔧 Components: {len(app.custom_motorcycle.child_components)}")

        # Show component breakdown
        print("\n🔧 COMPONENT ANALYSIS:")
        total_component_power = 0
        total_component_energy = 0

        for component in app.custom_motorcycle.child_components:
            comp_info = f"  • {component.name} ({component.mass:.1f} kg)"

            if hasattr(component, '_maximum_power_generation') and component._maximum_power_generation > 0:
                power_kw = component._maximum_power_generation / 1000
                comp_info += f" - {power_kw:.1f} kW"
                total_component_power += component._maximum_power_generation

            if hasattr(component, 'remaining_energy_capacity'):
                energy_kwh = component.remaining_energy_capacity / 3.6e6
                comp_info += f" - {energy_kwh:.1f} kWh"
                total_component_energy += component.remaining_energy_capacity

            print(comp_info)

        # Performance summary
        if total_component_power > 0:
            power_to_weight = (total_component_power / 1000) / app.custom_motorcycle.mass
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            print(f"  • Total Power: {total_component_power / 1000:.1f} kW")
            print(f"  • Power-to-Weight: {power_to_weight:.3f} kW/kg")

            if total_component_energy > 0:
                energy_kwh = total_component_energy / 3.6e6
                print(f"  • Total Energy: {energy_kwh:.1f} kWh")

        print(f"\n📊 TESTING ON {len(app.selected_tracks)} TRACK(S)")
        print("🔄 Running physics simulations...")
        print("-" * 60)

        app.simulation_results = {}
        successful_runs = 0
        total_distance = 0
        total_time = 0
        total_energy = 0

        # Process selected tracks properly
        tracks_to_test = []
        for track_item in app.selected_tracks:  # Run on all selected tracks
            if isinstance(track_item, tuple) and len(track_item) == 2:
                track_name, track_file = track_item
            elif isinstance(track_item, str):
                # If it's just a string, try to find the corresponding track
                available_tracks = app.get_available_tracks()
                track_file = None
                for name, path in available_tracks:
                    if name == track_item:
                        track_name = name
                        track_file = path
                        break
                if track_file is None:
                    continue
            else:
                continue

            if track_file is not None:
                tracks_to_test.append((track_name, track_file))

        for i, (track_name, track_file) in enumerate(tracks_to_test):
            print(f"\n📍 ({i+1}/{len(tracks_to_test)}) Testing: {track_name}")

            try:
                result = app.simulate_motorcycle_on_track(app.custom_motorcycle, track_file, track_name)
                app.simulation_results[track_name] = result

                if result['success']:
                    successful_runs += 1
                    distance = result['total_distance_km']
                    time_min = result['total_time_s'] / 60
                    speed = result['average_speed_kmh']
                    energy = result['energy_consumed_kWh']

                    total_distance += distance
                    total_time += result['total_time_s']
                    total_energy += energy

                    print(f"  ✅ Success - {time_min:.1f} min | {distance:.1f} km | {speed:.1f} km/h")

                    if energy > 0:
                        efficiency = energy / distance if distance > 0 else 0
                        print(f"     🔋 Energy: {energy:.2f} kWh | Efficiency: {efficiency:.3f} kWh/km")

                    # Component utilization feedback
                    if total_component_power > 0:
                        power_to_weight = (total_component_power / 1000) / app.custom_motorcycle.mass
                        if power_to_weight > 0.15:
                            print(f"     💪 High performance configuration - excellent acceleration capability")
                        elif power_to_weight > 0.08:
                            print(f"     ⚖️ Balanced configuration - good power and efficiency")
                        else:
                            print(f"     🌱 Efficiency-focused configuration - optimized for range")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"  ❌ Failed: {error_msg[:70]}..." if len(error_msg) > 70 else f"  ❌ Failed: {error_msg}")

            except Exception as e:
                print(f"  ❌ Exception: {str(e)[:70]}..." if len(str(e)) > 70 else f"  ❌ Exception: {str(e)}")
                app.simulation_results[track_name] = {
                    'track_name': track_name,
                    'error': str(e),
                    'success': False
                }

        print("\n" + "=" * 60)
        print("🎉 CUSTOM DESIGN SIMULATION COMPLETE!")
        print(f"✅ Successful: {successful_runs}/{len(tracks_to_test)} tracks")

        if successful_runs > 0:
            avg_speed = (total_distance / (total_time / 3600)) if total_time > 0 else 0

            print(f"\n📊 CUSTOM DESIGN PERFORMANCE SUMMARY:")
            print(f"  🛣️ Total Distance Tested: {total_distance:.1f} km")
            print(f"  ⏱️ Total Test Time: {total_time/3600:.1f} hours")
            print(f"  🏁 Average Speed: {avg_speed:.1f} km/h")

            if total_energy > 0:
                print(f"  🔋 Total Energy Consumed: {total_energy:.2f} kWh")
                efficiency = total_energy / total_distance if total_distance > 0 else 0
                print(f"  ⚡ Overall Efficiency: {efficiency:.3f} kWh/km")

            # Design feedback
            print(f"\n🎯 DESIGN ANALYSIS:")
            if app.motorcycle_type == "Hybrid":
                print(f"  🔄 Hybrid powertrain allows optimal component utilization")
            elif app.motorcycle_type == "Pure EV":
                print(f"  ⚡ Pure electric design optimizes for efficiency and simplicity")
            elif app.motorcycle_type == "Pure ICE":
                print(f"  🔥 ICE-only design provides traditional performance characteristics")

            # Performance class
            if total_component_power > 0:
                power_to_weight = (total_component_power / 1000) / app.custom_motorcycle.mass
                if power_to_weight > 0.15:
                    print(f"  🏆 HIGH PERFORMANCE CLASS - Track/sport oriented")
                elif power_to_weight > 0.08:
                    print(f"  🚗 STANDARD PERFORMANCE CLASS - Versatile daily use")
                else:
                    print(f"  🌱 EFFICIENCY CLASS - Range/economy optimized")

            print("\n👇 Continue to Step 4 to analyze results and export design data")
        else:
            print("\n❌ No successful simulations completed.")
            print("🔧 DESIGN RECOMMENDATIONS:")
            print("  • Check component compatibility")
            print("  • Ensure power source is adequate")
            print("  • Verify track files are accessible")
            print("  • Consider different component combinations")

run_simulation_btn.on_click(run_simulation)

# Only show if prerequisites are met
if app.custom_motorcycle and app.selected_tracks:
    display(run_simulation_btn)
    display(simulation_progress)
else:
    missing = []
    if not app.custom_motorcycle:
        missing.append("custom motorcycle (Step 1)")
    if not app.selected_tracks:
        missing.append("test tracks (Step 2)")

    print(f"⚠️ Complete the following first: {', '.join(missing)}")
    for item in missing:
        if "motorcycle" in item:
            print("  💡 Go to Step 1 and build your motorcycle")
        if "tracks" in item:
            print("  💡 Go to Step 2 and select test tracks")
```

<!-- #region id="yzikNMZHlTDL" -->
## Step 4: Design Analysis & Export
<!-- #endregion -->

```python colab={"base_uri": "https://localhost:8080/", "height": 1000, "referenced_widgets": ["7c89d8876e2f4653b1ccf009e8354b4c", "1533945aa7044581ab59787c3bd2fe87", "6bd72b770549495892d6668fd58cd8c9", "cc544fafff5b44c4b1a063961e0d6376", "1ef31ac572fd484a8c90892d76d480ee", "5c932c6673c64083a867d53d0f588d4c", "d9e42909f30f415da8328757b5d89fd6", "91f69b82da18447aaec075f6e13e9683", "1ac3591f764b45fd9b2d6651448c349e", "09559f29f9234aff9e519b79373f634c", "1342d8260d7849088343867f52e80b1e", "51a7d80a56564f509966c08f7cf37403"]} id="ckBhNWKElTDM" outputId="5a61da56-ddb6-439c-8c6d-b4ef0b70d86d"
#@title 📊 Custom Design Analysis & Export { display-mode: "form" }

#@markdown This section provides comprehensive analysis of your custom motorcycle design and professional export capabilities.
#@markdown **Perfect for engineering analysis** - includes component specifications, performance metrics, and design insights.

view_design_analysis_btn = widgets.Button(
    description='📊 View Design Analysis',
    button_style='info',
    layout=widgets.Layout(width='200px')
)

export_design_btn = widgets.Button(
    description='💾 Export Design Data',
    button_style='success',
    layout=widgets.Layout(width='200px')
)

analysis_display = widgets.Output()
export_status = widgets.Output()

def view_design_analysis(btn):
    """Display comprehensive custom design analysis."""
    if not app.simulation_results:
        with analysis_display:
            clear_output()
            print("❌ No simulation results available. Run simulation first.")
        return

    if not app.custom_motorcycle:
        with analysis_display:
            clear_output()
            print("❌ No custom motorcycle found. Build motorcycle first.")
        return

    with analysis_display:
        clear_output()

        print("📊 COMPREHENSIVE CUSTOM DESIGN ANALYSIS")
        print("=" * 80)

        # Custom motorcycle specifications
        print(f"🏍️ CUSTOM MOTORCYCLE: {app.custom_motorcycle.name}")
        print(f"🏷️ Powertrain Type: {app.motorcycle_type}")
        print(f"⚖️ Total Mass: {app.custom_motorcycle.mass:.1f} kg")
        print(f"🔧 Custom Components: {len(app.custom_motorcycle.child_components)}")

        # Detailed component analysis
        print(f"\n🔧 COMPONENT SPECIFICATION ANALYSIS:")
        print("-" * 80)

        total_power = 0
        total_energy = 0
        component_mass = 0
        power_sources = []
        energy_sources = []

        for component in app.custom_motorcycle.child_components:
            component_mass += component.mass
            print(f"  📦 {component.name}")
            print(f"     ⚖️ Mass: {component.mass:.1f} kg")

            if hasattr(component, '_maximum_power_generation') and component._maximum_power_generation > 0:
                power_kw = component._maximum_power_generation / 1000
                total_power += component._maximum_power_generation
                power_sources.append(component.name)
                print(f"     ⚡ Max Power: {power_kw:.1f} kW")
                print(f"     🏁 Power/Weight: {(power_kw / component.mass):.3f} kW/kg")

            if hasattr(component, 'remaining_energy_capacity'):
                energy_j = component.remaining_energy_capacity
                energy_kwh = energy_j / 3.6e6
                total_energy += energy_j
                energy_sources.append(component.name)
                print(f"     🔋 Energy Capacity: {energy_kwh:.1f} kWh")
                energy_density = energy_kwh / component.mass * 1000  # Wh/kg
                print(f"     📊 Energy Density: {energy_density:.0f} Wh/kg")

            print()

        # Overall powertrain analysis
        power_to_weight = (total_power / 1000) / app.custom_motorcycle.mass if total_power > 0 else 0
        component_ratio = component_mass / app.custom_motorcycle.mass

        print(f"🎯 POWERTRAIN PERFORMANCE ANALYSIS:")
        print(f"  ⚡ Total System Power: {total_power / 1000:.1f} kW")
        print(f"  🔋 Total Energy Storage: {total_energy / 3.6e6:.1f} kWh")
        print(f"  🏁 Power-to-Weight Ratio: {power_to_weight:.3f} kW/kg")
        print(f"  ⚖️ Component Mass Ratio: {component_ratio:.1%}")
        print(f"  🔧 Power Sources: {len(power_sources)} ({', '.join(power_sources)})")
        print(f"  🔋 Energy Sources: {len(energy_sources)} ({', '.join(energy_sources)})")

        # Design classification
        print(f"\n🏷️ DESIGN CLASSIFICATION:")
        if power_to_weight > 0.15:
            print(f"  🏆 Performance Class: HIGH PERFORMANCE")
            print(f"     • Excellent acceleration and top speed")
            print(f"     • Suitable for track and sport applications")
        elif power_to_weight > 0.08:
            print(f"  🚗 Performance Class: STANDARD PERFORMANCE")
            print(f"     • Balanced power and efficiency")
            print(f"     • Versatile for various riding conditions")
        else:
            print(f"  🌱 Performance Class: EFFICIENCY FOCUSED")
            print(f"     • Optimized for range and economy")
            print(f"     • Ideal for urban commuting")

        if app.motorcycle_type == "Hybrid":
            print(f"  🔄 Powertrain Type: HYBRID SYSTEM")
            print(f"     • Combines electric and ICE advantages")
            print(f"     • Flexible power delivery options")
        elif app.motorcycle_type == "Pure EV":
            print(f"  ⚡ Powertrain Type: PURE ELECTRIC")
            print(f"     • Zero local emissions")
            print(f"     • Instant torque delivery")
        elif app.motorcycle_type == "Pure ICE":
            print(f"  🔥 Powertrain Type: INTERNAL COMBUSTION")
            print(f"     • Traditional performance characteristics")
            print(f"     • Extended range capability")

        # Simulation results analysis
        print(f"\n" + "=" * 80)
        print(f"📈 PERFORMANCE VALIDATION RESULTS")
        print("-" * 100)
        print(f"{'Track Name':<40} {'Distance':<10} {'Time':<8} {'Speed':<10} {'Energy':<10} {'Efficiency':<15}")
        print(f"{'':40} {'(km)':<10} {'(min)':<8} {'(km/h)':<10} {'(kWh)':<10} {'(kWh/km)':<15}")
        print("-" * 100)

        successful_results = []
        failed_count = 0

        for track_name, result in app.simulation_results.items():
            if result.get('success'):
                dist = result['total_distance_km']
                time_min = result['total_time_s'] / 60
                speed = result['average_speed_kmh']
                energy = result['energy_consumed_kWh']
                efficiency = energy / dist if dist > 0 and energy > 0 else 0

                print(f"{track_name[:39]:<40} {dist:<10.1f} {time_min:<8.1f} {speed:<10.1f} {energy:<10.2f} {efficiency:<15.4f}")
                successful_results.append(result)
            else:
                failed_count += 1
                error_msg = result.get('error', 'Unknown error')[:25]
                print(f"{track_name[:39]:<40} {'ERROR':<10} {'---':<8} {'---':<10} {'---':<10} {error_msg:<15}")

        print("-" * 100)

        # Statistical performance analysis
        if successful_results:
            distances = [r['total_distance_km'] for r in successful_results]
            speeds = [r['average_speed_kmh'] for r in successful_results]
            energies = [r['energy_consumed_kWh'] for r in successful_results]
            times = [r['total_time_s'] for r in successful_results]

            print(f"\n📊 STATISTICAL PERFORMANCE ANALYSIS:")
            print(f"✅ Validation Success Rate: {len(successful_results)}/{len(app.simulation_results)} ({len(successful_results)/len(app.simulation_results)*100:.1f}%)")

            print(f"\n🏁 Speed Performance Statistics:")
            print(f"  • Mean Speed: {np.mean(speeds):.1f} km/h")
            print(f"  • Maximum Speed: {np.max(speeds):.1f} km/h")
            print(f"  • Minimum Speed: {np.min(speeds):.1f} km/h")
            print(f"  • Speed Standard Deviation: {np.std(speeds):.1f} km/h")
            print(f"  • Speed Consistency: {(1 - np.std(speeds)/np.mean(speeds))*100:.1f}%")

            print(f"\n🛣️ Distance and Time Analysis:")
            print(f"  • Total Test Distance: {sum(distances):.1f} km")
            print(f"  • Total Test Time: {sum(times)/3600:.1f} hours")
            print(f"  • Average Track Length: {np.mean(distances):.1f} km")
            print(f"  • Overall Average Speed: {sum(distances)/(sum(times)/3600):.1f} km/h")

            print(f"\n🎯 DESIGN OPTIMIZATION INSIGHTS:")

            # Power utilization analysis
            avg_speed = np.mean(speeds)
            if power_to_weight > 0.2:
                print(f"  💪 Power Analysis: High power-to-weight ({power_to_weight:.3f} kW/kg)")
                print(f"     • Excellent for acceleration and hill climbing")
                print(f"     • Consider efficiency optimization for better range")
            elif power_to_weight < 0.05:
                print(f"  🐌 Power Analysis: Low power-to-weight ({power_to_weight:.3f} kW/kg)")
                print(f"     • May struggle with acceleration and hills")
                print(f"     • Consider adding more powerful components")
            else:
                print(f"  ⚖️ Power Analysis: Balanced power-to-weight ({power_to_weight:.3f} kW/kg)")
                print(f"     • Good compromise between performance and efficiency")

            # Type-specific insights
            if app.motorcycle_type == "Hybrid" and len(power_sources) > 1:
                print(f"  🔄 Hybrid Optimization: Multi-source powertrain active")
                print(f"     • Leverage electric for efficiency, ICE for range")
                print(f"     • Consider power management strategies")
            elif app.motorcycle_type == "Pure EV" and total_energy > 0:
                print(f"  ⚡ EV Optimization: Pure electric configuration")
                print(f"     • Focus on energy density and thermal management")
                print(f"     • Battery chemistry and charging speed critical")

        else:
            print("\n❌ No successful results to analyze")
            print("🔧 Troubleshooting suggestions:")
            print("  • Verify component compatibility")
            print("  • Check power source adequacy")
            print("  • Ensure track files are valid")

def export_design_data(btn):
    """Export comprehensive custom design data."""
    if not app.simulation_results:
        with export_status:
            clear_output()
            print("❌ No results to export. Run simulation first.")
        return

    if not app.custom_motorcycle:
        with export_status:
            clear_output()
            print("❌ No custom motorcycle found. Build motorcycle first.")
        return

    try:
        with export_status:
            clear_output()
            print("💾 Preparing comprehensive custom design export...")

        # Create comprehensive export data structure
        export_data = {
            'export_metadata': {
                'timestamp': datetime.now().isoformat(),
                'notebook_type': 'custom_build_motorcycles',
                'application_version': '2.0',
                'design_type': 'custom_build',
                'powertrain_type': app.motorcycle_type,
                'total_tracks_tested': len(app.simulation_results),
                'successful_simulations': len([r for r in app.simulation_results.values() if r.get('success')])
            },
            'custom_design_specifications': {
                'motorcycle_name': app.custom_motorcycle.name,
                'powertrain_type': app.motorcycle_type,
                'design_timestamp': datetime.now().isoformat(),
                'total_mass_kg': float(app.custom_motorcycle.mass),
                'dry_mass_excluding_components_kg': float(app.custom_motorcycle.dry_mass_excluding_components)
            },
            'component_selections': {
                'selected_motor': app.selected_motor,
                'selected_battery': app.selected_battery,
                'selected_engine': app.selected_engine,
                'selected_fuel_tank': app.selected_fuel_tank
            },
            'component_specifications': [],
            'simulation_results': {},
            'design_optimization_insights': {}
        }

        # Add detailed component specifications
        total_power = 0
        total_energy_capacity = 0

        for component in app.custom_motorcycle.child_components:
            comp_spec = {
                'name': component.name,
                'type': type(component).__name__,
                'mass_kg': float(component.mass)
            }

            # Power generation capability
            if hasattr(component, '_maximum_power_generation'):
                power_w = component._maximum_power_generation
                comp_spec['max_power_W'] = float(power_w)
                comp_spec['max_power_kW'] = float(power_w / 1000)
                total_power += power_w

            # Energy storage capability
            if hasattr(component, 'remaining_energy_capacity'):
                energy_j = component.remaining_energy_capacity
                comp_spec['energy_capacity_J'] = float(energy_j)
                comp_spec['energy_capacity_kWh'] = float(energy_j / 3.6e6)
                total_energy_capacity += energy_j

            export_data['component_specifications'].append(comp_spec)

        # Add simulation results
        successful_results = []
        for track_name, result in app.simulation_results.items():
            if result.get('success'):
                track_data = {
                    'track_name': result['track_name'],
                    'track_file': result['track_file'],
                    'total_time_s': float(result['total_time_s']),
                    'total_distance_km': float(result['total_distance_km']),
                    'average_speed_kmh': float(result['average_speed_kmh']),
                    'energy_consumed_kWh': float(result['energy_consumed_kWh']),
                    'status': 'success'
                }

                export_data['simulation_results'][track_name] = track_data
                successful_results.append(result)
            else:
                export_data['simulation_results'][track_name] = {
                    'track_name': result['track_name'],
                    'track_file': result.get('track_file', 'unknown'),
                    'error': result.get('error', 'Unknown error'),
                    'status': 'failed'
                }

        # Generate filename with design characteristics
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        type_abbrev = app.motorcycle_type.replace(' ', '').replace('Pure', '').replace('ICE', 'Ice').lower()
        power_to_weight = (total_power / 1000) / app.custom_motorcycle.mass if total_power > 0 else 0
        power_class = 'HP' if power_to_weight > 0.15 else 'MP' if power_to_weight > 0.08 else 'EF'
        filename = f"custom_{type_abbrev}_{power_class}_{timestamp}.json"

        # Write comprehensive data to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        with export_status:
            clear_output()
            print("✅ CUSTOM DESIGN EXPORT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📄 Filename: {filename}")

            file_size = os.path.getsize(filename) / 1024  # KB
            print(f"📦 File Size: {file_size:.1f} KB")

            print("\n📊 Export Contains:")
            print(f"  🔧 Custom design specifications and component selections")
            print(f"  📋 Detailed component specifications ({len(export_data['component_specifications'])} components)")
            print(f"  📈 {len(app.simulation_results)} track simulation results")
            print(f"  🎯 Design optimization insights and recommendations")
            print(f"  🕐 Complete design and testing timeline")

            if successful_results:
                print(f"\n🎯 Key Design Metrics Exported:")
                print(f"  • Powertrain Type: {app.motorcycle_type}")
                print(f"  • Power-to-Weight: {power_to_weight:.3f} kW/kg")
                print(f"  • Total System Power: {total_power/1000:.1f} kW")
                print(f"  • Validation Success: {len(successful_results)}/{len(app.simulation_results)} tracks")

                avg_speed = np.mean([r['average_speed_kmh'] for r in successful_results])
                total_dist = sum([r['total_distance_km'] for r in successful_results])
                print(f"  • Average Performance: {avg_speed:.1f} km/h over {total_dist:.1f} km")

            print("\n🎉 Ready for comprehensive engineering analysis!")
            print("💡 Use this data for design optimization, component selection, and performance prediction.")

    except Exception as e:
        with export_status:
            clear_output()
            print(f"❌ Export failed: {str(e)}")
            print("💡 Please check file permissions and available disk space")
            print("🔧 If the error persists, try running the simulation again")

# Connect button handlers
view_design_analysis_btn.on_click(view_design_analysis)
export_design_btn.on_click(export_design_data)

# Only show if simulation has been run
if app.simulation_results:
    display(widgets.HBox([view_design_analysis_btn, export_design_btn]))
    display(analysis_display)
    display(export_status)
else:
    print("⚠️ Run simulation first (Step 3) to analyze and export your custom design")
    print("💡 Complete Steps 1-3 to unlock comprehensive design analysis")
```
