"""
Interactive component picker utilities for Google Colab interface.

This module provides widget creation functions and real-time calculation
engines for the interactive component selection interface.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from typing import Dict, Any, Callable, Optional, List
import warnings

# Ensure Colab compatibility
try:
    from google.colab import output
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

from .component_specs import ENGINE_SPECS, MOTOR_SPECS, BATTERY_SPECS, FUEL_TANK_SPECS
from .custom_builder import (
    create_custom_engine,
    create_custom_motor,
    create_custom_battery,
    create_custom_fuel_tank,
    validate_engine_parameters,
    validate_motor_parameters,
    validate_battery_parameters,
    estimate_component_cost,
)
from .engines import (
    Engine_250cc_20kW,
    Engine_400cc_30kW,
    Engine_500cc_40kW,
    Engine_650cc_50kW,
    Engine_750cc_60kW,
    Engine_1000cc_80kW,
)
from .motors import (
    Motor_5kW_Hub,
    Motor_10kW_Hub,
    Motor_15kW_MidDrive,
    Motor_30kW_MidDrive,
    Motor_50kW_HighPerf,
    Motor_80kW_HighPerf,
    Motor_120kW_HighPerf,
)
from .batteries import (
    Battery_5kWh_180WhKg,
    Battery_10kWh_200WhKg,
    Battery_15kWh_220WhKg,
    Battery_20kWh_180WhKg,
    Battery_25kWh_200WhKg,
)
from .fuel_systems import (
    FuelTank_8L,
    FuelTank_15L,
    FuelTank_25L,
)


def ensure_widget_display():
    """Ensure widgets display properly in Colab environment."""
    if IN_COLAB:
        try:
            from google.colab import output as colab_output
            # Enable custom widgets in Colab
            colab_output.enable_custom_widget_manager()
        except Exception:
            # Fallback for older Colab versions
            try:
                from google.colab import widgets as colab_widgets
                colab_widgets.enable()
            except:
                pass


class ComponentPickerState:
    """Manages the state of the interactive component picker."""
    
    def __init__(self):
        self.motorcycle_type = "Pure EV"
        self.selected_components = {}
        self.custom_components = {}
        self.total_cost = 0.0
        self.total_weight = 0.0
        self.power_to_weight = 0.0
        
    def update_metrics(self):
        """Update calculated metrics based on current component selection."""
        total_mass = 150.0  # Base motorcycle mass
        total_cost = 2000.0  # Base motorcycle cost
        max_power = 0.0
        
        for comp_type, component in self.selected_components.items():
            if component:
                total_mass += component.mass
                max_power = max(max_power, getattr(component, '_maximum_power_generation', 0) / 1000)
                
                # Estimate cost based on component type
                if hasattr(component, '_maximum_power_generation'):
                    if 'Engine' in component.name:
                        total_cost += 3000 + (max_power * 50)
                    elif 'Motor' in component.name:
                        total_cost += 1500 + (max_power * 80)
                    elif 'Battery' in component.name:
                        capacity = getattr(component, 'remaining_energy_capacity', 0) / 3.6e6
                        total_cost += capacity * 300
                    elif 'Fuel' in component.name:
                        total_cost += 200
        
        self.total_weight = total_mass
        self.total_cost = total_cost
        self.power_to_weight = max_power / total_mass if total_mass > 0 else 0


def create_motorcycle_type_selector(state: ComponentPickerState, update_callback: Callable) -> widgets.Widget:
    """Create motorcycle type selection widget."""
    type_selector = widgets.RadioButtons(
        options=['Pure EV', 'Hybrid', 'Pure ICE'],
        value=state.motorcycle_type,
        description='Motorcycle Type:',
        style={'description_width': '150px'}
    )
    
    def on_type_change(change):
        state.motorcycle_type = change['new']
        update_callback()
    
    type_selector.observe(on_type_change, names='value')
    return type_selector


def create_engine_selector(state: ComponentPickerState, update_callback: Callable) -> widgets.Widget:
    """Create engine selection widget."""
    # Preset options
    preset_options = [
        ('None', None),
        ('250cc 20kW Engine', 'Engine_250cc_20kW'),
        ('400cc 30kW Engine', 'Engine_400cc_30kW'),
        ('500cc 40kW Engine', 'Engine_500cc_40kW'),
        ('650cc 50kW Engine', 'Engine_650cc_50kW'),
        ('750cc 60kW Engine', 'Engine_750cc_60kW'),
        ('1000cc 80kW Engine', 'Engine_1000cc_80kW'),
        ('Custom Engine', 'custom')
    ]
    
    dropdown = widgets.Dropdown(
        options=preset_options,
        value=None,
        description='Engine:',
        style={'description_width': '100px'}
    )
    
    # Custom engine parameters
    custom_displacement = widgets.IntSlider(value=500, min=100, max=1500, description='Displacement (cc):')
    custom_power = widgets.FloatSlider(value=40, min=10, max=150, description='Power (kW):')
    custom_mass = widgets.FloatSlider(value=55, min=20, max=120, description='Mass (kg):')
    custom_efficiency = widgets.FloatSlider(value=0.32, min=0.15, max=0.45, step=0.01, description='Peak Efficiency:')
    
    custom_widgets = widgets.VBox([
        custom_displacement,
        custom_power,
        custom_mass,
        custom_efficiency
    ])
    custom_widgets.layout.display = 'none'
    
    specs_display = widgets.HTML(value="<b>Select an engine to see specifications</b>")
    validation_display = widgets.HTML(value="")
    
    def update_engine_display():
        if dropdown.value == 'custom':
            custom_widgets.layout.display = 'block'
            # Validate custom parameters
            is_valid, message = validate_engine_parameters(
                custom_displacement.value,
                custom_power.value,
                custom_mass.value,
                custom_efficiency.value
            )
            
            color = "green" if is_valid else "orange"
            validation_display.value = f'<span style="color: {color};">{message}</span>'
            
            # Create custom engine
            try:
                engine = create_custom_engine(
                    "Custom Engine",
                    custom_displacement.value,
                    custom_power.value,
                    custom_mass.value,
                    custom_efficiency.value
                )
                state.selected_components['engine'] = engine
                
                specs_display.value = f"""
                <b>Custom Engine Specifications:</b><br>
                • Displacement: {custom_displacement.value} cc<br>
                • Power: {custom_power.value} kW<br>
                • Mass: {engine.mass:.1f} kg (including fuel)<br>
                • Peak Efficiency: {custom_efficiency.value*100:.1f}%<br>
                • Estimated Cost: ${estimate_component_cost('engine', max_power_kW=custom_power.value, displacement_cc=custom_displacement.value):,.0f}
                """
            except Exception as e:
                specs_display.value = f'<span style="color: red;">Error creating engine: {str(e)}</span>'
                state.selected_components['engine'] = None
                
        elif dropdown.value:
            custom_widgets.layout.display = 'none'
            validation_display.value = ""
            
            # Create preset engine
            engine_functions = {
                'Engine_250cc_20kW': Engine_250cc_20kW,
                'Engine_400cc_30kW': Engine_400cc_30kW,
                'Engine_500cc_40kW': Engine_500cc_40kW,
                'Engine_650cc_50kW': Engine_650cc_50kW,
                'Engine_750cc_60kW': Engine_750cc_60kW,
                'Engine_1000cc_80kW': Engine_1000cc_80kW,
            }
            
            if dropdown.value in engine_functions:
                engine = engine_functions[dropdown.value]()
                state.selected_components['engine'] = engine
                
                # Get specs from ENGINE_SPECS
                spec_key = dropdown.value.replace('Engine_', '')
                specs = ENGINE_SPECS.get(spec_key, {})
                
                specs_display.value = f"""
                <b>Engine Specifications:</b><br>
                • Displacement: {specs.get('displacement_cc', 'N/A')} cc<br>
                • Power: {specs.get('max_power_kW', 'N/A')} kW<br>
                • Mass: {engine.mass:.1f} kg (including fuel)<br>
                • Peak Efficiency: {specs.get('efficiency_peak', 0)*100:.1f}%<br>
                • {specs.get('description', '')}
                """
        else:
            custom_widgets.layout.display = 'none'
            validation_display.value = ""
            specs_display.value = "<b>Select an engine to see specifications</b>"
            state.selected_components['engine'] = None
        
        state.update_metrics()
        update_callback()
    
    def on_dropdown_change(change):
        update_engine_display()
    
    def on_custom_change(change):
        if dropdown.value == 'custom':
            update_engine_display()
    
    dropdown.observe(on_dropdown_change, names='value')
    custom_displacement.observe(on_custom_change, names='value')
    custom_power.observe(on_custom_change, names='value')
    custom_mass.observe(on_custom_change, names='value')
    custom_efficiency.observe(on_custom_change, names='value')
    
    return widgets.VBox([
        dropdown,
        custom_widgets,
        specs_display,
        validation_display
    ])


def create_motor_selector(state: ComponentPickerState, update_callback: Callable) -> widgets.Widget:
    """Create motor selection widget."""
    preset_options = [
        ('None', None),
        ('5kW Hub Motor', 'Motor_5kW_Hub'),
        ('10kW Hub Motor', 'Motor_10kW_Hub'),
        ('15kW Mid-Drive Motor', 'Motor_15kW_MidDrive'),
        ('30kW Mid-Drive Motor', 'Motor_30kW_MidDrive'),
        ('50kW High-Performance Motor', 'Motor_50kW_HighPerf'),
        ('80kW High-Performance Motor', 'Motor_80kW_HighPerf'),
        ('120kW High-Performance Motor', 'Motor_120kW_HighPerf'),
        ('Custom Motor', 'custom')
    ]
    
    dropdown = widgets.Dropdown(
        options=preset_options,
        value=None,
        description='Motor:',
        style={'description_width': '100px'}
    )
    
    # Custom motor parameters
    custom_max_power = widgets.FloatSlider(value=30, min=5, max=150, description='Max Power (kW):')
    custom_cont_power = widgets.FloatSlider(value=24, min=3, max=120, description='Continuous (kW):')
    custom_mass = widgets.FloatSlider(value=25, min=8, max=60, description='Mass (kg):')
    custom_efficiency = widgets.FloatSlider(value=0.92, min=0.75, max=0.98, step=0.01, description='Efficiency:')
    
    custom_widgets = widgets.VBox([
        custom_max_power,
        custom_cont_power,
        custom_mass,
        custom_efficiency
    ])
    custom_widgets.layout.display = 'none'
    
    specs_display = widgets.HTML(value="<b>Select a motor to see specifications</b>")
    validation_display = widgets.HTML(value="")
    
    def update_motor_display():
        if dropdown.value == 'custom':
            custom_widgets.layout.display = 'block'
            
            # Auto-adjust continuous power if needed
            if custom_cont_power.value > custom_max_power.value:
                custom_cont_power.value = custom_max_power.value * 0.8
            
            # Validate custom parameters
            is_valid, message = validate_motor_parameters(
                custom_max_power.value,
                custom_cont_power.value,
                custom_mass.value,
                custom_efficiency.value
            )
            
            color = "green" if is_valid else "orange"
            validation_display.value = f'<span style="color: {color};">{message}</span>'
            
            # Create custom motor
            try:
                motor = create_custom_motor(
                    "Custom Motor",
                    custom_max_power.value,
                    custom_cont_power.value,
                    custom_mass.value,
                    custom_efficiency.value
                )
                state.selected_components['motor'] = motor
                
                specs_display.value = f"""
                <b>Custom Motor Specifications:</b><br>
                • Max Power: {custom_max_power.value} kW<br>
                • Continuous Power: {custom_cont_power.value} kW<br>
                • Mass: {custom_mass.value} kg<br>
                • Efficiency: {custom_efficiency.value*100:.1f}%<br>
                • Specific Power: {custom_max_power.value/custom_mass.value:.1f} kW/kg<br>
                • Estimated Cost: ${estimate_component_cost('motor', max_power_kW=custom_max_power.value):,.0f}
                """
            except Exception as e:
                specs_display.value = f'<span style="color: red;">Error creating motor: {str(e)}</span>'
                state.selected_components['motor'] = None
                
        elif dropdown.value:
            custom_widgets.layout.display = 'none'
            validation_display.value = ""
            
            # Create preset motor
            motor_functions = {
                'Motor_5kW_Hub': Motor_5kW_Hub,
                'Motor_10kW_Hub': Motor_10kW_Hub,
                'Motor_15kW_MidDrive': Motor_15kW_MidDrive,
                'Motor_30kW_MidDrive': Motor_30kW_MidDrive,
                'Motor_50kW_HighPerf': Motor_50kW_HighPerf,
                'Motor_80kW_HighPerf': Motor_80kW_HighPerf,
                'Motor_120kW_HighPerf': Motor_120kW_HighPerf,
            }
            
            if dropdown.value in motor_functions:
                motor = motor_functions[dropdown.value]()
                state.selected_components['motor'] = motor
                
                # Get specs from MOTOR_SPECS
                spec_key = dropdown.value.replace('Motor_', '')
                specs = MOTOR_SPECS.get(spec_key, {})
                
                specs_display.value = f"""
                <b>Motor Specifications:</b><br>
                • Max Power: {specs.get('max_power_kW', 'N/A')} kW<br>
                • Continuous Power: {specs.get('continuous_power_kW', 'N/A')} kW<br>
                • Mass: {specs.get('dry_mass_kg', 'N/A')} kg<br>
                • Efficiency: {specs.get('efficiency_peak', 0)*100:.1f}%<br>
                • Type: {specs.get('type', 'N/A').replace('_', ' ').title()}<br>
                • {specs.get('description', '')}
                """
        else:
            custom_widgets.layout.display = 'none'
            validation_display.value = ""
            specs_display.value = "<b>Select a motor to see specifications</b>"
            state.selected_components['motor'] = None
        
        state.update_metrics()
        update_callback()
    
    def on_dropdown_change(change):
        update_motor_display()
    
    def on_custom_change(change):
        if dropdown.value == 'custom':
            update_motor_display()
    
    dropdown.observe(on_dropdown_change, names='value')
    custom_max_power.observe(on_custom_change, names='value')
    custom_cont_power.observe(on_custom_change, names='value')
    custom_mass.observe(on_custom_change, names='value')
    custom_efficiency.observe(on_custom_change, names='value')
    
    return widgets.VBox([
        dropdown,
        custom_widgets,
        specs_display,
        validation_display
    ])


def create_battery_selector(state: ComponentPickerState, update_callback: Callable) -> widgets.Widget:
    """Create battery selection widget."""
    preset_options = [
        ('None', None),
        ('5kWh 180Wh/kg Battery', 'Battery_5kWh_180WhKg'),
        ('10kWh 200Wh/kg Battery', 'Battery_10kWh_200WhKg'),
        ('15kWh 220Wh/kg Battery', 'Battery_15kWh_220WhKg'),
        ('20kWh 180Wh/kg Battery', 'Battery_20kWh_180WhKg'),
        ('25kWh 200Wh/kg Battery', 'Battery_25kWh_200WhKg'),
        ('Custom Battery', 'custom')
    ]
    
    dropdown = widgets.Dropdown(
        options=preset_options,
        value=None,
        description='Battery:',
        style={'description_width': '100px'}
    )
    
    # Custom battery parameters
    custom_capacity = widgets.FloatSlider(value=15, min=5, max=50, description='Capacity (kWh):')
    custom_energy_density = widgets.IntSlider(value=200, min=100, max=300, description='Energy Density (Wh/kg):')
    custom_discharge_rate = widgets.FloatSlider(value=3.5, min=1, max=8, step=0.5, description='Max C-Rate:')
    custom_efficiency = widgets.FloatSlider(value=0.93, min=0.80, max=0.99, step=0.01, description='Efficiency:')
    
    custom_widgets = widgets.VBox([
        custom_capacity,
        custom_energy_density,
        custom_discharge_rate,
        custom_efficiency
    ])
    custom_widgets.layout.display = 'none'
    
    specs_display = widgets.HTML(value="<b>Select a battery to see specifications</b>")
    validation_display = widgets.HTML(value="")
    
    def update_battery_display():
        if dropdown.value == 'custom':
            custom_widgets.layout.display = 'block'
            
            # Validate custom parameters
            is_valid, message = validate_battery_parameters(
                custom_capacity.value,
                custom_energy_density.value,
                custom_discharge_rate.value,
                custom_efficiency.value
            )
            
            color = "green" if is_valid else "orange"
            validation_display.value = f'<span style="color: {color};">{message}</span>'
            
            # Create custom battery
            try:
                battery = create_custom_battery(
                    "Custom Battery",
                    custom_capacity.value,
                    custom_energy_density.value,
                    custom_discharge_rate.value,
                    custom_efficiency.value
                )
                state.selected_components['battery'] = battery
                
                max_power = custom_capacity.value * custom_discharge_rate.value
                
                specs_display.value = f"""
                <b>Custom Battery Specifications:</b><br>
                • Capacity: {custom_capacity.value} kWh<br>
                • Energy Density: {custom_energy_density.value} Wh/kg<br>
                • Total Mass: {battery.mass:.1f} kg<br>
                • Max Power: {max_power:.0f} kW<br>
                • Efficiency: {custom_efficiency.value*100:.1f}%<br>
                • Estimated Cost: ${estimate_component_cost('battery', capacity_kWh=custom_capacity.value, energy_density_WhKg=custom_energy_density.value):,.0f}
                """
            except Exception as e:
                specs_display.value = f'<span style="color: red;">Error creating battery: {str(e)}</span>'
                state.selected_components['battery'] = None
                
        elif dropdown.value:
            custom_widgets.layout.display = 'none'
            validation_display.value = ""
            
            # Create preset battery
            battery_functions = {
                'Battery_5kWh_180WhKg': Battery_5kWh_180WhKg,
                'Battery_10kWh_200WhKg': Battery_10kWh_200WhKg,
                'Battery_15kWh_220WhKg': Battery_15kWh_220WhKg,
                'Battery_20kWh_180WhKg': Battery_20kWh_180WhKg,
                'Battery_25kWh_200WhKg': Battery_25kWh_200WhKg,
            }
            
            if dropdown.value in battery_functions:
                battery = battery_functions[dropdown.value]()
                state.selected_components['battery'] = battery
                
                # Get specs from BATTERY_SPECS
                spec_key = dropdown.value.replace('Battery_', '')
                specs = BATTERY_SPECS.get(spec_key, {})
                
                max_power = specs.get('capacity_kWh', 0) * specs.get('max_discharge_rate_C', 0)
                
                specs_display.value = f"""
                <b>Battery Specifications:</b><br>
                • Capacity: {specs.get('capacity_kWh', 'N/A')} kWh<br>
                • Energy Density: {specs.get('energy_density_WhKg', 'N/A')} Wh/kg<br>
                • Total Mass: {battery.mass:.1f} kg<br>
                • Max Power: {max_power:.0f} kW<br>
                • Efficiency: {specs.get('efficiency', 0)*100:.1f}%<br>
                • {specs.get('description', '')}
                """
        else:
            custom_widgets.layout.display = 'none'
            validation_display.value = ""
            specs_display.value = "<b>Select a battery to see specifications</b>"
            state.selected_components['battery'] = None
        
        state.update_metrics()
        update_callback()
    
    def on_dropdown_change(change):
        update_battery_display()
    
    def on_custom_change(change):
        if dropdown.value == 'custom':
            update_battery_display()
    
    dropdown.observe(on_dropdown_change, names='value')
    custom_capacity.observe(on_custom_change, names='value')
    custom_energy_density.observe(on_custom_change, names='value')
    custom_discharge_rate.observe(on_custom_change, names='value')
    custom_efficiency.observe(on_custom_change, names='value')
    
    return widgets.VBox([
        dropdown,
        custom_widgets,
        specs_display,
        validation_display
    ])


def create_metrics_display(state: ComponentPickerState) -> widgets.Widget:
    """Create real-time metrics display widget."""
    metrics_html = widgets.HTML(value="<b>Configuration Metrics</b>")
    
    def update_display():
        metrics_html.value = f"""
        <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3>🏍️ Motorcycle Configuration Summary</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;"><b>Type:</b></td>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;">{state.motorcycle_type}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;"><b>Total Weight:</b></td>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;">{state.total_weight:.1f} kg</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;"><b>Estimated Cost:</b></td>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;">${state.total_cost:,.0f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;"><b>Power-to-Weight:</b></td>
                    <td style="padding: 5px; border-bottom: 1px solid #ddd;">{state.power_to_weight:.3f} kW/kg</td>
                </tr>
            </table>
        </div>
        """
    
    # Store update function for external access
    metrics_html.update_display = update_display
    update_display()
    
    return metrics_html


def create_configuration_export(state: ComponentPickerState) -> widgets.Widget:
    """Create configuration export widget."""
    export_button = widgets.Button(
        description="Export Configuration Code",
        button_style='success',
        icon='download'
    )
    
    # Use Output widget for better Colab compatibility
    code_output = widgets.Output()
    
    # Alternative text area for code display
    code_textarea = widgets.Textarea(
        value="# Click 'Export Configuration Code' to generate component code",
        rows=15,
        disabled=True,
        layout=widgets.Layout(width='100%', font_family='monospace')
    )
    
    def on_export_click(b):
        # Generate component creation code
        code_lines = [
            "# Generated Motorcycle Configuration",
            "# Copy this code to your simulation notebook",
            "",
            "from ithaka_powertrain_sim.motorbike import Motorbike",
            "from ithaka_powertrain_sim.components import MechanicalBrake, MechanicalComponent, ElectricalComponent",
            "from ithaka_powertrain_sim.efficiency_definitions import ConstantEfficiency",
            ""
        ]
        
        # Add imports based on selected components
        imports = []
        if state.selected_components.get('engine'):
            imports.append("from ithaka_powertrain_sim.component_library import Engine_*")
        if state.selected_components.get('motor'):
            imports.append("from ithaka_powertrain_sim.component_library import Motor_*")
        if state.selected_components.get('battery'):
            imports.append("from ithaka_powertrain_sim.component_library import Battery_*")
        
        code_lines.extend(imports)
        code_lines.append("")
        
        # Generate component creation code
        component_names = []
        
        if state.selected_components.get('engine'):
            engine = state.selected_components['engine']
            if 'Custom' in engine.name:
                code_lines.append("# Custom Engine (recreate with your parameters)")
                code_lines.append("engine = create_custom_engine(...)")
            else:
                func_name = engine.name.replace(' ', '_').replace('cc_', 'cc_').replace('kW_', 'kW')
                code_lines.append(f"engine = {func_name}()")
            component_names.append('engine')
        
        if state.selected_components.get('motor'):
            motor = state.selected_components['motor']
            if 'Custom' in motor.name:
                code_lines.append("# Custom Motor (recreate with your parameters)")
                code_lines.append("motor = create_custom_motor(...)")
            else:
                func_name = motor.name.replace(' ', '_')
                code_lines.append(f"motor = {func_name}()")
            component_names.append('motor')
        
        if state.selected_components.get('battery'):
            battery = state.selected_components['battery']
            if 'Custom' in battery.name:
                code_lines.append("# Custom Battery (recreate with your parameters)")
                code_lines.append("battery = create_custom_battery(...)")
            else:
                func_name = battery.name.replace(' ', '_').replace('/', '')
                code_lines.append(f"battery = {func_name}()")
            component_names.append('battery')
        
        # Generate motorcycle assembly code
        code_lines.extend([
            "",
            "# Assemble components",
            "brake = MechanicalBrake('Brake')",
            ""
        ])
        
        if state.motorcycle_type == "Pure EV":
            code_lines.extend([
                "# Connect battery to motor",
                "motor._child_components = (battery,)",
                "",
                "# Create motorcycle",
                "motorbike = Motorbike(",
                "    name='Pure EV Motorbike',",
                "    dry_mass_excluding_components=200.0,",
                "    front_mass_ratio=0.45,",
                "    front_wheel_inertia=5.0 * (0.45**2) / 2.0,",
                "    front_wheel_radius=0.45,",
                "    front_wheel_coefficient_of_rolling_resistance=0.01,",
                "    rear_wheel_inertia=12.0 * (0.45**2) / 2.0,",
                "    rear_wheel_radius=0.45,",
                "    rear_wheel_coefficient_of_rolling_resistance=0.01,",
                "    frontal_area=0.75,",
                "    coefficient_of_aerodynamic_drag=0.7,",
                "    child_components=(motor, brake),",
                ")"
            ])
        elif state.motorcycle_type == "Hybrid":
            code_lines.extend([
                "# Create hybrid configuration",
                "# (Additional setup required for generator and electrical connections)",
                "# See hybrid_motorbike example in component_library_demo.ipynb"
            ])
        else:  # Pure ICE
            code_lines.extend([
                "# Create gearbox",
                "gearbox = MechanicalComponent(",
                "    name='Gearbox',",
                "    dry_mass=15.0,",
                "    efficiency_definition=ConstantEfficiency(0.92),",
                "    child_components=(engine,)",
                ")",
                "",
                "# Create motorcycle",
                "motorbike = Motorbike(",
                "    name='Pure ICE Motorbike',",
                "    dry_mass_excluding_components=180.0,",
                "    front_mass_ratio=0.52,",
                "    front_wheel_inertia=5.0 * (0.45**2) / 2.0,",
                "    front_wheel_radius=0.45,",
                "    front_wheel_coefficient_of_rolling_resistance=0.01,",
                "    rear_wheel_inertia=12.0 * (0.45**2) / 2.0,",
                "    rear_wheel_radius=0.45,",
                "    rear_wheel_coefficient_of_rolling_resistance=0.01,",
                "    frontal_area=0.85,",
                "    coefficient_of_aerodynamic_drag=0.8,",
                "    child_components=(gearbox, brake),",
                ")"
            ])
        
        # Display code in both output and textarea for compatibility
        generated_code = "\n".join(code_lines)
        code_textarea.value = generated_code
        
        with code_output:
            clear_output()
            if IN_COLAB:
                # In Colab, also display as formatted code block
                display(HTML(f'<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;"><code>{generated_code}</code></pre>'))
    
    export_button.on_click(on_export_click)
    
    return widgets.VBox([
        export_button,
        code_textarea,
        code_output
    ])