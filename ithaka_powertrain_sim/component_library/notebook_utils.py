"""
Notebook utility functions for component picking and simulation management.

This module provides common utilities for Jupyter notebooks to reduce code duplication
and improve maintainability.
"""

import sys
import os
import subprocess
import warnings
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import json

import numpy as np
import pandas as pd
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets


class NotebookEnvironment:
    """Manages notebook environment setup and dependency checking."""
    
    @staticmethod
    def setup_colab_environment() -> bool:
        """
        Set up Google Colab environment with repository and dependencies.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        warnings.filterwarnings('ignore')
        
        # Detect environment
        try:
            import google.colab
            IN_COLAB = True
            print("Google Colab environment detected")
        except ImportError:
            IN_COLAB = False
            print("Local environment detected")
        
        if IN_COLAB:
            # Check for existing repository
            print("Checking for repository...")
            
            current_dir = os.getcwd()
            possible_paths = ['/content/Teo-Moto-Repo', '/content/ithaka-powertrain-sim', current_dir]
            
            repo_found = False
            for path in possible_paths:
                if os.path.exists(path) and os.path.exists(os.path.join(path, 'setup.py')):
                    print(f"Found repository at: {path}")
                    os.chdir(path)
                    repo_found = True
                    break
            
            if not repo_found:
                print("Cloning repository...")
                try:
                    result = subprocess.run(['git', 'clone', 'https://github.com/Teodus/Teo-Moto-Repo.git'],
                                          capture_output=True, text=True, cwd='/content')
                    if result.returncode == 0:
                        os.chdir('/content/Teo-Moto-Repo')
                        print("Repository cloned successfully")
                    else:
                        print("Clone failed. Please check your internet connection.")
                        return False
                except Exception as e:
                    print(f"Error: {e}")
                    return False
            
            # Install dependencies
            print("Installing dependencies...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
                          capture_output=True)
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-e', '.'],
                          capture_output=True)
            print("Dependencies installed")
        
        # Verify installation
        return NotebookEnvironment.verify_installation()
    
    @staticmethod
    def verify_installation() -> bool:
        """
        Verify that all required packages are installed correctly.
        
        Returns:
            bool: True if all imports successful, False otherwise
        """
        print("Verifying installation...")
        
        required_packages = {
            'pandas': 'pandas as pd',
            'numpy': 'numpy as np',
            'matplotlib': 'matplotlib.pyplot as plt',
            'ipywidgets': 'ipywidgets as widgets',
            'ithaka_powertrain_sim': 'ithaka_powertrain_sim'
        }
        
        missing_packages = []
        
        for package_name, import_stmt in required_packages.items():
            try:
                exec(f"import {import_stmt}")
                # Silent success - only report failures
            except ImportError as e:
                print(f"Missing {package_name}: {e}")
                missing_packages.append(package_name)
        
        # Check component imports
        try:
            from ithaka_powertrain_sim.component_library import (
                Battery_10kWh_200WhKg, Motor_30kW_MidDrive, Engine_650cc_50kW
            )
            from ithaka_powertrain_sim.simulation import SimulationRunner
            print("Component library modules loaded successfully")
        except ImportError as e:
            print(f"Component imports failed: {e}")
            missing_packages.append('component_library')
        
        if missing_packages:
            print(f"Missing packages: {', '.join(missing_packages)}")
            return False
        
        print("All modules imported successfully!")
        return True


class TrackManager:
    """Manages track file discovery and loading."""
    
    @staticmethod
    def get_available_tracks(base_path: str = 'docs/gpx_files') -> List[Tuple[str, str]]:
        """
        Get list of available GPX track files.
        
        Args:
            base_path: Path to GPX files directory
            
        Returns:
            List of tuples (display_name, file_path)
        """
        gpx_pattern = os.path.join(base_path, '*.gpx')
        gpx_files = glob.glob(gpx_pattern)
        
        if not gpx_files:
            # Try alternative paths
            alt_paths = [
                'docs/gpx_files/*.gpx',
                '../docs/gpx_files/*.gpx',
                '../../docs/gpx_files/*.gpx',
                '/content/Teo-Moto-Repo/docs/gpx_files/*.gpx'
            ]
            
            for alt_pattern in alt_paths:
                gpx_files = glob.glob(alt_pattern)
                if gpx_files:
                    break
        
        if not gpx_files:
            return [("No tracks found", None)]
        
        track_names = []
        for gpx_file in gpx_files:
            # Create human-readable name
            name = os.path.basename(gpx_file).replace('.gpx', '')
            name = name.replace('-', ' ').replace('_', ' ')
            name = ' '.join(word.capitalize() for word in name.split())
            track_names.append((name, gpx_file))
        
        return sorted(track_names)
    
    @staticmethod
    def format_track_name(file_path: str) -> str:
        """Format track file path into readable name."""
        if not file_path:
            return "Unknown Track"
        
        name = os.path.basename(file_path).replace('.gpx', '').replace('.json', '')
        name = name.replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in name.split())


class SimulationExporter:
    """Handles export of simulation results and configurations."""
    
    @staticmethod
    def export_custom_design(
        motorcycle,
        motorcycle_type: str,
        simulation_results: Dict[str, Any],
        component_selections: Dict[str, Optional[str]],
        output_dir: str = "."
    ) -> str:
        """
        Export comprehensive custom design data.
        
        Args:
            motorcycle: The Motorbike instance
            motorcycle_type: Type of motorcycle (Pure EV, Hybrid, Pure ICE)
            simulation_results: Dictionary of simulation results by track
            component_selections: Dictionary of selected component names
            output_dir: Directory to save export file
            
        Returns:
            str: Path to exported file
        """
        # Calculate metrics
        total_power = SimulationExporter._calculate_total_power(component_selections)
        successful_results = [r for r in simulation_results.values() if r.get('success')]
        
        # Create export data structure
        export_data = {
            'export_metadata': {
                'timestamp': datetime.now().isoformat(),
                'notebook_type': 'custom_build_motorcycles',
                'application_version': '2.1',
                'design_type': 'custom_build',
                'powertrain_type': motorcycle_type,
                'total_tracks_tested': len(simulation_results),
                'successful_simulations': len(successful_results)
            },
            'custom_design_specifications': {
                'motorcycle_name': motorcycle.name,
                'powertrain_type': motorcycle_type,
                'design_timestamp': datetime.now().isoformat(),
                'total_mass_kg': float(motorcycle.mass),
                'dry_mass_excluding_components_kg': float(motorcycle.dry_mass_excluding_components),
                'aerodynamic_properties': {
                    'frontal_area_m2': float(motorcycle.frontal_area),
                    'drag_coefficient': float(motorcycle.coefficient_of_aerodynamic_drag)
                },
                'wheel_properties': {
                    'front_radius_m': float(motorcycle.front_wheel_radius),
                    'rear_radius_m': float(motorcycle.rear_wheel_radius),
                    'rolling_resistance_front': float(motorcycle.front_wheel_coefficient_of_rolling_resistance),
                    'rolling_resistance_rear': float(motorcycle.rear_wheel_coefficient_of_rolling_resistance)
                }
            },
            'component_selections': component_selections,
            'component_specifications': SimulationExporter._extract_component_specs(motorcycle),
            'simulation_results': SimulationExporter._format_simulation_results(simulation_results),
            'performance_summary': SimulationExporter._generate_performance_summary(
                motorcycle, total_power, successful_results
            )
        }
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        type_abbrev = motorcycle_type.replace(' ', '').replace('Pure', '').replace('ICE', 'Ice').lower()
        power_to_weight = (total_power / 1000) / motorcycle.mass if total_power > 0 else 0
        power_class = 'HP' if power_to_weight > 0.15 else 'MP' if power_to_weight > 0.08 else 'EF'
        
        filename = os.path.join(output_dir, f"custom_{type_abbrev}_{power_class}_{timestamp}.json")
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename
    
    @staticmethod
    def _calculate_total_power(component_selections: Dict[str, Optional[str]]) -> float:
        """Calculate total power from component selections."""
        total_power = 0
        
        # Motor power
        motor = component_selections.get('selected_motor')
        if motor:
            power_map = {
                '30kW': 30000, '50kW': 50000, '80kW': 80000, '120kW': 120000,
                '5kW': 5000, '10kW': 10000, '15kW': 15000
            }
            for key, value in power_map.items():
                if key in motor:
                    total_power += value
                    break
        
        # Engine power
        engine = component_selections.get('selected_engine')
        if engine:
            power_map = {
                '250cc': 20000, '400cc': 30000, '500cc': 40000,
                '650cc': 50000, '750cc': 60000, '1000cc': 80000
            }
            for key, value in power_map.items():
                if key in engine:
                    total_power += value
                    break
        
        return total_power
    
    @staticmethod
    def _extract_component_specs(motorcycle) -> List[Dict[str, Any]]:
        """Extract detailed component specifications."""
        specs = []
        
        for component in motorcycle.child_components:
            comp_spec = {
                'name': component.name,
                'type': type(component).__name__,
                'mass_kg': float(component.mass)
            }
            
            # Extract power if available
            if 'kW' in component.name:
                try:
                    power_str = component.name.split('kW')[0].split()[-1]
                    power_kw = float(power_str)
                    comp_spec['max_power_W'] = float(power_kw * 1000)
                    comp_spec['max_power_kW'] = float(power_kw)
                    comp_spec['specific_power_kW_kg'] = float(power_kw / component.mass)
                except:
                    pass
            
            # Extract energy capacity if available
            if hasattr(component, 'remaining_energy_capacity'):
                energy_j = component.remaining_energy_capacity
                comp_spec['energy_capacity_J'] = float(energy_j)
                comp_spec['energy_capacity_kWh'] = float(energy_j / 3.6e6)
                comp_spec['energy_density_Wh_kg'] = float(energy_j / 3600 / component.mass)
            
            specs.append(comp_spec)
        
        return specs
    
    @staticmethod
    def _format_simulation_results(simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format simulation results for export."""
        formatted = {}
        
        for track_name, result in simulation_results.items():
            if result.get('success'):
                formatted[track_name] = {
                    'track_name': result['track_name'],
                    'track_file': result['track_file'],
                    'total_time_s': float(result['total_time_s']),
                    'total_distance_km': float(result['total_distance_km']),
                    'average_speed_kmh': float(result['average_speed_kmh']),
                    'energy_consumed_kWh': float(result['energy_consumed_kWh']),
                    'efficiency_kWh_per_km': float(
                        result['energy_consumed_kWh'] / result['total_distance_km']
                    ) if result['total_distance_km'] > 0 else 0,
                    'status': 'success'
                }
            else:
                formatted[track_name] = {
                    'track_name': result['track_name'],
                    'track_file': result.get('track_file', 'unknown'),
                    'error': result.get('error', 'Unknown error'),
                    'status': 'failed'
                }
        
        return formatted
    
    @staticmethod
    def _generate_performance_summary(
        motorcycle,
        total_power: float,
        successful_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate performance summary statistics."""
        summary = {
            'power_metrics': {
                'total_system_power_W': float(total_power),
                'total_system_power_kW': float(total_power / 1000),
                'power_to_weight_kW_kg': float((total_power / 1000) / motorcycle.mass) if motorcycle.mass > 0 else 0
            }
        }
        
        if successful_results:
            speeds = [r['average_speed_kmh'] for r in successful_results]
            distances = [r['total_distance_km'] for r in successful_results]
            energies = [r['energy_consumed_kWh'] for r in successful_results]
            
            summary['performance_statistics'] = {
                'average_speed_kmh': float(np.mean(speeds)),
                'max_speed_kmh': float(np.max(speeds)),
                'min_speed_kmh': float(np.min(speeds)),
                'speed_std_dev_kmh': float(np.std(speeds)),
                'total_distance_tested_km': float(sum(distances)),
                'total_energy_consumed_kWh': float(sum(energies)),
                'average_efficiency_kWh_per_km': float(sum(energies) / sum(distances)) if sum(distances) > 0 else 0
            }
        
        # Performance classification
        power_to_weight = summary['power_metrics']['power_to_weight_kW_kg']
        if power_to_weight > 0.15:
            performance_class = "HIGH_PERFORMANCE"
            description = "Track/sport oriented configuration"
        elif power_to_weight > 0.08:
            performance_class = "STANDARD_PERFORMANCE"
            description = "Balanced daily use configuration"
        else:
            performance_class = "EFFICIENCY_FOCUSED"
            description = "Range/economy optimized configuration"
        
        summary['performance_classification'] = {
            'class': performance_class,
            'description': description,
            'power_to_weight_ratio': power_to_weight
        }
        
        return summary


class UIComponents:
    """Reusable UI components for notebooks."""
    
    @staticmethod
    def create_styled_button(
        description: str,
        button_style: str = 'primary',
        icon: str = None,
        width: str = '200px',
        height: str = '40px'
    ) -> widgets.Button:
        """Create a styled button with consistent appearance."""
        button = widgets.Button(
            description=description,
            button_style=button_style,
            layout=widgets.Layout(width=width, height=height)
        )
        if icon:
            button.icon = icon
        return button
    
    @staticmethod
    def create_progress_display(title: str = "Progress") -> Tuple[widgets.Output, callable]:
        """
        Create a progress display widget with update function.
        
        Returns:
            Tuple of (output_widget, update_function)
        """
        output = widgets.Output()
        
        def update_progress(message: str, progress: float = None, status: str = 'info'):
            """Update progress display."""
            with output:
                clear_output(wait=True)
                
                # Status colors
                colors = {
                    'info': '#0066cc',
                    'success': '#009900',
                    'warning': '#ff9900',
                    'error': '#cc0000'
                }
                
                color = colors.get(status, '#0066cc')
                
                html_content = f"""
                <div style="padding: 10px; border-left: 4px solid {color};">
                    <h4>{title}</h4>
                    <p style="color: {color};">{message}</p>
                """
                
                if progress is not None:
                    progress_pct = min(100, max(0, progress * 100))
                    html_content += f"""
                    <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px;">
                        <div style="width: {progress_pct}%; background-color: {color}; 
                                    padding: 5px 0; border-radius: 4px; text-align: center; color: white;">
                            {progress_pct:.0f}%
                        </div>
                    </div>
                    """
                
                html_content += "</div>"
                display(HTML(html_content))
        
        return output, update_progress
    
    @staticmethod
    def create_component_summary_card(component_name: str, specs: Dict[str, Any]) -> str:
        """Create HTML card for component summary."""
        html = f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0;">
            <h4 style="margin-top: 0;">{component_name}</h4>
            <table style="width: 100%;">
        """
        
        for key, value in specs.items():
            # Format key nicely
            display_key = key.replace('_', ' ').title()
            
            # Format value based on type
            if isinstance(value, float):
                if 'efficiency' in key.lower() or 'ratio' in key.lower():
                    display_value = f"{value:.1%}"
                elif 'power' in key.lower() and 'kw' in key.lower():
                    display_value = f"{value:.1f} kW"
                elif 'mass' in key.lower() or 'weight' in key.lower():
                    display_value = f"{value:.1f} kg"
                elif 'energy' in key.lower() and 'kwh' in key.lower():
                    display_value = f"{value:.1f} kWh"
                else:
                    display_value = f"{value:.2f}"
            else:
                display_value = str(value)
            
            html += f"""
                <tr>
                    <td style="padding: 5px; font-weight: bold;">{display_key}:</td>
                    <td style="padding: 5px;">{display_value}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html