"""
Range tracking module for monitoring energy consumption and remaining range.

This module provides comprehensive range tracking for all motorcycle types,
handling both electric (battery) and ICE (fuel) energy sources uniformly.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EnergyState:
    """Represents the energy state at a point in time."""
    timestamp: float  # Simulation time in seconds
    distance_km: float  # Distance traveled
    energy_remaining_J: float  # Remaining energy in Joules
    energy_consumed_J: float  # Energy consumed since last state
    speed_kmh: float  # Current speed
    efficiency_instant: float  # Instantaneous efficiency (J/m)
    
    @property
    def energy_remaining_kWh(self) -> float:
        """Convert remaining energy to kWh."""
        return self.energy_remaining_J / 3.6e6
    
    @property
    def energy_consumed_kWh(self) -> float:
        """Convert consumed energy to kWh."""
        return self.energy_consumed_J / 3.6e6


@dataclass
class RangeMetrics:
    """Comprehensive range metrics for a motorcycle."""
    total_capacity_J: float  # Total energy capacity in Joules
    current_energy_J: float  # Current energy level
    energy_consumed_J: float  # Total energy consumed
    distance_traveled_km: float  # Total distance traveled
    
    # Efficiency metrics
    average_efficiency_J_per_m: float  # Average efficiency
    recent_efficiency_J_per_m: float  # Recent efficiency (last 10km)
    
    # Range estimates
    range_remaining_average_km: float  # Based on average efficiency
    range_remaining_recent_km: float  # Based on recent efficiency
    range_remaining_worst_km: float  # Based on worst efficiency
    total_range_km: float  # Total theoretical range
    
    # Additional metrics
    energy_sources: Dict[str, float]  # Energy by source type
    last_topup_distance_km: float  # Distance at last top-up
    
    @property
    def energy_percent_remaining(self) -> float:
        """Calculate percentage of energy remaining."""
        if self.total_capacity_J > 0:
            return (self.current_energy_J / self.total_capacity_J) * 100
        return 0.0
    
    @property
    def distance_since_topup_km(self) -> float:
        """Calculate distance since last top-up."""
        return self.distance_traveled_km - self.last_topup_distance_km


class RangeTracker:
    """
    Tracks range and energy consumption for motorcycles.
    
    This class monitors energy usage, calculates remaining range,
    and handles top-ups (recharge/refuel) for all motorcycle types.
    """
    
    def __init__(self, motorcycle, window_size_km: float = 10.0):
        """
        Initialize range tracker for a motorcycle.
        
        Args:
            motorcycle: The Motorbike instance to track
            window_size_km: Window size for recent efficiency calculation
        """
        self.motorcycle = motorcycle
        self.window_size_km = window_size_km
        
        # State tracking
        self.energy_states: List[EnergyState] = []
        self.topup_events: List[Tuple[float, float, str]] = []  # (distance, amount, type)
        
        # Initialize with current state
        self._initialize_energy_sources()
        
        # Efficiency tracking
        self.worst_efficiency_J_per_m = 0.0
        self.best_efficiency_J_per_m = float('inf')
        
    def _initialize_energy_sources(self):
        """Initialize energy source tracking."""
        self.energy_sources = {}
        self.total_capacity_J = 0.0
        
        # Find all energy sources in the motorcycle
        for component in self._get_all_components(self.motorcycle):
            if hasattr(component, 'remaining_energy_capacity'):
                source_type = type(component).__name__
                capacity = getattr(component, 'initial_energy_capacity', 
                                 component.remaining_energy_capacity)
                
                self.energy_sources[source_type] = {
                    'component': component,
                    'initial_capacity_J': capacity,
                    'current_capacity_J': component.remaining_energy_capacity,
                    'type': 'electric' if 'Battery' in source_type else 'fuel'
                }
                self.total_capacity_J += capacity
    
    def _get_all_components(self, component) -> List:
        """Recursively get all components."""
        components = [component]
        if hasattr(component, 'child_components'):
            for child in component.child_components:
                components.extend(self._get_all_components(child))
        return components
    
    def update(self, time_s: float, distance_km: float, speed_kmh: float, 
               energy_consumed_J: float):
        """
        Update range tracking with new state.
        
        Args:
            time_s: Current simulation time
            distance_km: Current distance traveled
            speed_kmh: Current speed
            energy_consumed_J: Energy consumed in this time step
        """
        # Calculate current total energy
        current_energy_J = 0.0
        for source_info in self.energy_sources.values():
            component = source_info['component']
            if hasattr(component, 'remaining_energy_capacity'):
                current_energy_J += component.remaining_energy_capacity
        
        # Calculate instantaneous efficiency
        if distance_km > 0 and len(self.energy_states) > 0:
            last_state = self.energy_states[-1]
            distance_delta_m = (distance_km - last_state.distance_km) * 1000
            if distance_delta_m > 0:
                efficiency = energy_consumed_J / distance_delta_m
            else:
                efficiency = 0.0
        else:
            efficiency = 0.0
        
        # Update worst/best efficiency
        if efficiency > 0:
            self.worst_efficiency_J_per_m = max(self.worst_efficiency_J_per_m, efficiency)
            self.best_efficiency_J_per_m = min(self.best_efficiency_J_per_m, efficiency)
        
        # Record state
        state = EnergyState(
            timestamp=time_s,
            distance_km=distance_km,
            energy_remaining_J=current_energy_J,
            energy_consumed_J=energy_consumed_J,
            speed_kmh=speed_kmh,
            efficiency_instant=efficiency
        )
        self.energy_states.append(state)
    
    def get_range_metrics(self) -> RangeMetrics:
        """
        Calculate comprehensive range metrics.
        
        Returns:
            RangeMetrics object with all range calculations
        """
        if not self.energy_states:
            return self._get_empty_metrics()
        
        current_state = self.energy_states[-1]
        
        # Calculate average efficiency
        total_energy_consumed = sum(s.energy_consumed_J for s in self.energy_states)
        total_distance_m = current_state.distance_km * 1000
        
        if total_distance_m > 0:
            avg_efficiency = total_energy_consumed / total_distance_m
        else:
            avg_efficiency = 0.0
        
        # Calculate recent efficiency (last window_size_km)
        recent_efficiency = self._calculate_recent_efficiency()
        
        # Get current energy levels
        current_energy_J = 0.0
        energy_by_source = {}
        for source_name, source_info in self.energy_sources.items():
            component = source_info['component']
            if hasattr(component, 'remaining_energy_capacity'):
                energy = component.remaining_energy_capacity
                current_energy_J += energy
                energy_by_source[source_name] = energy / 3.6e6  # Convert to kWh
        
        # Calculate range estimates
        if avg_efficiency > 0:
            range_avg = (current_energy_J / avg_efficiency) / 1000  # km
        else:
            range_avg = 0.0
        
        if recent_efficiency > 0:
            range_recent = (current_energy_J / recent_efficiency) / 1000  # km
        else:
            range_recent = range_avg
        
        if self.worst_efficiency_J_per_m > 0:
            range_worst = (current_energy_J / self.worst_efficiency_J_per_m) / 1000  # km
        else:
            range_worst = 0.0
        
        # Calculate total theoretical range
        if avg_efficiency > 0:
            total_range = (self.total_capacity_J / avg_efficiency) / 1000  # km
        else:
            total_range = 0.0
        
        # Find last top-up distance
        last_topup_distance = 0.0
        if self.topup_events:
            last_topup_distance = self.topup_events[-1][0]
        
        return RangeMetrics(
            total_capacity_J=self.total_capacity_J,
            current_energy_J=current_energy_J,
            energy_consumed_J=total_energy_consumed,
            distance_traveled_km=current_state.distance_km,
            average_efficiency_J_per_m=avg_efficiency,
            recent_efficiency_J_per_m=recent_efficiency,
            range_remaining_average_km=range_avg,
            range_remaining_recent_km=range_recent,
            range_remaining_worst_km=range_worst,
            total_range_km=total_range,
            energy_sources=energy_by_source,
            last_topup_distance_km=last_topup_distance
        )
    
    def _calculate_recent_efficiency(self) -> float:
        """Calculate efficiency over recent window."""
        if len(self.energy_states) < 2:
            return 0.0
        
        current_distance = self.energy_states[-1].distance_km
        window_start_distance = current_distance - self.window_size_km
        
        # Find states within window
        window_states = []
        for state in reversed(self.energy_states):
            if state.distance_km >= window_start_distance:
                window_states.append(state)
            else:
                break
        
        if len(window_states) < 2:
            return self.energy_states[-1].efficiency_instant
        
        # Calculate efficiency over window
        window_states.reverse()
        total_energy = sum(s.energy_consumed_J for s in window_states[1:])
        distance_m = (window_states[-1].distance_km - window_states[0].distance_km) * 1000
        
        if distance_m > 0:
            return total_energy / distance_m
        return 0.0
    
    def perform_topup(self, amount_percent: float = 100.0, 
                      source_type: Optional[str] = None) -> Dict[str, float]:
        """
        Perform a top-up (recharge/refuel) operation.
        
        Args:
            amount_percent: Percentage to top up (0-100)
            source_type: Specific source to top up (None = all sources)
            
        Returns:
            Dict of energy added by source type
        """
        if not self.energy_states:
            return {}
        
        current_distance = self.energy_states[-1].distance_km
        energy_added = {}
        
        for source_name, source_info in self.energy_sources.items():
            if source_type is None or source_type in source_name:
                component = source_info['component']
                if hasattr(component, 'remaining_energy_capacity'):
                    # Calculate top-up amount
                    max_capacity = source_info['initial_capacity_J']
                    current = component.remaining_energy_capacity
                    deficit = max_capacity - current
                    
                    # Apply percentage
                    topup_amount = deficit * (amount_percent / 100.0)
                    
                    # Update component (this is a simplified version - 
                    # actual implementation would depend on component API)
                    new_capacity = current + topup_amount
                    if hasattr(component, 'set_remaining_energy'):
                        component.set_remaining_energy(new_capacity)
                    else:
                        # Fallback - directly set if possible
                        component.remaining_energy_capacity = new_capacity
                    
                    energy_added[source_name] = topup_amount / 3.6e6  # kWh
        
        # Record top-up event
        total_added = sum(v * 3.6e6 for v in energy_added.values())  # Convert back to J
        self.topup_events.append((current_distance, total_added, 'partial' if amount_percent < 100 else 'full'))
        
        return energy_added
    
    def get_efficiency_profile(self) -> Dict[str, Any]:
        """
        Get detailed efficiency profile.
        
        Returns:
            Dictionary with efficiency statistics and profile
        """
        if not self.energy_states:
            return {}
        
        # Extract efficiency data
        distances = [s.distance_km for s in self.energy_states]
        efficiencies = [s.efficiency_instant for s in self.energy_states if s.efficiency_instant > 0]
        speeds = [s.speed_kmh for s in self.energy_states]
        
        if not efficiencies:
            return {}
        
        # Convert to Wh/km for easier interpretation
        efficiencies_wh_per_km = [e * 1000 / 3.6 for e in efficiencies]  # J/m to Wh/km
        
        return {
            'average_efficiency_Wh_per_km': np.mean(efficiencies_wh_per_km),
            'best_efficiency_Wh_per_km': np.min(efficiencies_wh_per_km),
            'worst_efficiency_Wh_per_km': np.max(efficiencies_wh_per_km),
            'std_efficiency_Wh_per_km': np.std(efficiencies_wh_per_km),
            'efficiency_at_speeds': self._calculate_efficiency_by_speed_bins(),
            'topup_locations_km': [t[0] for t in self.topup_events]
        }
    
    def _calculate_efficiency_by_speed_bins(self) -> Dict[str, float]:
        """Calculate average efficiency in different speed ranges."""
        speed_bins = [(0, 30), (30, 50), (50, 70), (70, 90), (90, 110), (110, 130), (130, float('inf'))]
        efficiency_by_speed = {}
        
        for low, high in speed_bins:
            bin_efficiencies = []
            for state in self.energy_states:
                if low <= state.speed_kmh < high and state.efficiency_instant > 0:
                    bin_efficiencies.append(state.efficiency_instant * 1000 / 3.6)  # Wh/km
            
            if bin_efficiencies:
                label = f"{low}-{high} km/h" if high != float('inf') else f"{low}+ km/h"
                efficiency_by_speed[label] = np.mean(bin_efficiencies)
        
        return efficiency_by_speed
    
    def _get_empty_metrics(self) -> RangeMetrics:
        """Return empty metrics when no data available."""
        return RangeMetrics(
            total_capacity_J=self.total_capacity_J,
            current_energy_J=self.total_capacity_J,
            energy_consumed_J=0.0,
            distance_traveled_km=0.0,
            average_efficiency_J_per_m=0.0,
            recent_efficiency_J_per_m=0.0,
            range_remaining_average_km=0.0,
            range_remaining_recent_km=0.0,
            range_remaining_worst_km=0.0,
            total_range_km=0.0,
            energy_sources={},
            last_topup_distance_km=0.0
        )