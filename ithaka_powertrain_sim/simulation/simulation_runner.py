"""Improved simulation runner with better error handling and validation."""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any, List
from ..trajectory import load_gpx, append_and_resample_dataframe
from .track_processor import TrackProcessor
from .speed_calculator import SpeedCalculator
from .range_tracker import RangeTracker


class SimulationRunner:
    """Runs motorcycle simulations with improved data processing and validation."""

    def __init__(
        self,
        min_speed_kmh: float = 10.0,
        max_speed_kmh: float = 300.0,
        use_filter: bool = True,
        speed_calculation_method: str = "distance_time",
        track_range: bool = True,
    ):
        """
        Initialize simulation runner.

        Parameters
        ----------
        min_speed_kmh : float
            Minimum speed to consider as moving (default: 10.0 km/h)
        max_speed_kmh : float
            Maximum realistic speed (default: 300.0 km/h)
        use_filter : bool
            Whether to filter stopped sections (default: True)
        speed_calculation_method : str
            Method for average speed: 'distance_time', 'mean_speeds', 'weighted'
        track_range : bool
            Whether to track range and energy consumption (default: True)
        """
        self.track_processor = TrackProcessor(
            min_speed_kmh=min_speed_kmh, max_speed_kmh=max_speed_kmh
        )
        self.speed_calculator = SpeedCalculator()
        self.use_filter = use_filter
        self.speed_method = speed_calculation_method
        self.track_range = track_range

    def simulate_motorcycle_on_track(
        self, motorcycle: Any, track_file: str, track_name: str, verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run simulation for motorcycle on a single track.

        Parameters
        ----------
        motorcycle : Motorbike
            The motorcycle object to simulate
        track_file : str
            Path to the GPX track file
        track_name : str
            Name of the track for reporting
        verbose : bool
            Whether to print detailed progress

        Returns
        -------
        result : dict
            Simulation results including metrics and any warnings
        """
        result = {
            "track_name": track_name,
            "track_file": track_file,
            "success": False,
            "warnings": [],
            "processing_stats": {},
        }

        try:
            # Step 1: Load trajectory
            if verbose:
                print(f"Loading track: {track_name}")

            trajectory_df = load_gpx(track_file)

            # Step 2: Append and resample with filtering
            trajectory_df = append_and_resample_dataframe(
                trajectory_df,
                filter_stops=self.use_filter,
                min_speed_kmh=self.track_processor.min_speed_ms * 3.6,
            )

            # Step 3: Additional processing and validation
            processed_df, processing_stats = self.track_processor.process_track_data(
                trajectory_df,
                filter_stops=False,  # Already filtered in step 2
                validate_speeds=True,
            )

            result["processing_stats"] = processing_stats
            result["warnings"].extend(processing_stats.get("warnings", []))

            if len(processed_df) < 10:
                raise ValueError("Insufficient data points after processing")

            # Step 4: Extract simulation parameters
            target_speeds = processed_df["Target Speed"].to_list()
            delta_distances = np.diff(processed_df["Distance"], prepend=0).tolist()
            delta_elevations = np.diff(processed_df["Elevation"], prepend=0).tolist()
            times = processed_df["Target Time"].to_list()

            # Step 5: Initialize range tracker if enabled
            range_tracker = None
            if self.track_range:
                range_tracker = RangeTracker(motorcycle)
                if verbose:
                    print("Range tracking enabled")

            # Step 6: Run motorcycle simulation
            achieved_speeds = [target_speeds[0]]
            reporting_rows = []
            energy_consumed = []
            current_distance = 0.0

            for i in range(1, len(processed_df)):
                delta_time = times[i] - times[i - 1]

                # Skip invalid time deltas
                if delta_time <= 0 or delta_time > 300:  # Skip if > 5 minutes
                    if verbose:
                        print(
                            f"Warning: Skipping point {i} with invalid delta_time: {delta_time}"
                        )
                    achieved_speeds.append(achieved_speeds[-1])
                    continue

                try:
                    # Run physics simulation
                    achieved_speed, reporting_row = motorcycle.calculate_achieved_speed(
                        achieved_speeds[-1],
                        target_speeds[i],
                        delta_time,
                        delta_distances[i],
                        delta_elevations[i],
                    )

                    # Validate achieved speed
                    if not np.isfinite(achieved_speed) or achieved_speed < 0:
                        achieved_speed = min(target_speeds[i], achieved_speeds[-1])
                        result["warnings"].append(f"Invalid speed at point {i}")

                    achieved_speeds.append(achieved_speed)
                    reporting_rows.append(reporting_row)

                    # Track energy if available
                    energy_j = 0
                    if (
                        hasattr(reporting_row, "get")
                        and "Energy Consumed (J)" in reporting_row
                    ):
                        energy_j = reporting_row.get("Energy Consumed (J)", 0)
                        energy_consumed.append(energy_j)
                    
                    # Update range tracker
                    if range_tracker and energy_j > 0:
                        current_distance = processed_df.iloc[i]["Distance"] / 1000  # Convert to km
                        current_speed = achieved_speed * 3.6  # Convert to km/h
                        range_tracker.update(
                            time_s=times[i],
                            distance_km=current_distance,
                            speed_kmh=current_speed,
                            energy_consumed_J=energy_j
                        )

                except Exception as e:
                    # Handle simulation errors gracefully
                    achieved_speeds.append(achieved_speeds[-1])
                    result["warnings"].append(
                        f"Simulation error at point {i}: {str(e)[:50]}"
                    )
                    if verbose:
                        print(f"Warning: Simulation error at point {i}: {e}")

            # Step 6: Validate achieved speeds
            validated_speeds, validation_stats = (
                self.track_processor.validate_achieved_speeds(
                    target_speeds, achieved_speeds, np.diff(times, prepend=0).tolist()
                )
            )

            result["warnings"].extend(validation_stats.get("warnings", []))

            # Step 7: Calculate metrics
            distances = processed_df["Distance"].values
            times_array = processed_df["Target Time"].values

            # Average speed calculation
            avg_speed_ms, speed_stats = self.speed_calculator.calculate_average_speed(
                distances, times_array, method=self.speed_method
            )

            result["total_time_s"] = float(times_array[-1] - times_array[0])
            result["total_distance_km"] = float((distances[-1] - distances[0]) / 1000)
            result["average_speed_kmh"] = float(avg_speed_ms * 3.6)
            result["speed_calculation_method"] = self.speed_method

            # Energy metrics
            if energy_consumed:
                total_energy_j = sum(energy_consumed)
                result["energy_consumed_kWh"] = float(total_energy_j / 3.6e6)

                # Calculate efficiency
                if result["total_distance_km"] > 0:
                    result["efficiency_kWh_per_km"] = (
                        result["energy_consumed_kWh"] / result["total_distance_km"]
                    )
                    result["efficiency_Wh_per_km"] = (
                        result["efficiency_kWh_per_km"] * 1000
                    )
            else:
                result["energy_consumed_kWh"] = 0.0

            # Performance metrics
            result["max_speed_kmh"] = float(max(validated_speeds) * 3.6)
            result["min_speed_kmh"] = float(min(validated_speeds) * 3.6)
            result["speed_std_kmh"] = float(np.std(validated_speeds) * 3.6)

            # Add range metrics if tracking is enabled
            if range_tracker:
                range_metrics = range_tracker.get_range_metrics()
                efficiency_profile = range_tracker.get_efficiency_profile()
                
                result["range_metrics"] = {
                    "total_capacity_kWh": range_metrics.total_capacity_J / 3.6e6,
                    "energy_remaining_kWh": range_metrics.current_energy_J / 3.6e6,
                    "energy_remaining_percent": range_metrics.energy_percent_remaining,
                    "range_remaining_avg_km": range_metrics.range_remaining_average_km,
                    "range_remaining_recent_km": range_metrics.range_remaining_recent_km,
                    "range_remaining_worst_km": range_metrics.range_remaining_worst_km,
                    "total_theoretical_range_km": range_metrics.total_range_km,
                    "energy_sources": range_metrics.energy_sources,
                }
                
                result["efficiency_profile"] = efficiency_profile

            # Track data quality metrics
            result["data_points"] = len(processed_df)
            result["filtered_percentage"] = (
                (1 - len(processed_df) / len(trajectory_df)) * 100
                if len(trajectory_df) > 0
                else 0
            )

            result["success"] = True

            if verbose:
                print(
                    f"Simulation complete: {result['average_speed_kmh']:.1f} km/h average"
                )

        except Exception as e:
            result["error"] = str(e)
            result["warnings"].append(f"Simulation failed: {str(e)}")
            if verbose:
                print(f"Error: {e}")

        return result

    def run_batch_simulations(
        self, motorcycle: Any, tracks: list, verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run simulations on multiple tracks.

        Parameters
        ----------
        motorcycle : Motorbike
            The motorcycle object to simulate
        tracks : list
            List of (track_name, track_file) tuples
        verbose : bool
            Whether to print detailed progress

        Returns
        -------
        results : dict
            Dictionary of track_name -> simulation results
        """
        results = {}
        successful = 0

        for i, (track_name, track_file) in enumerate(tracks):
            if verbose:
                print(f"\nSimulating track {i+1}/{len(tracks)}: {track_name}")

            result = self.simulate_motorcycle_on_track(
                motorcycle, track_file, track_name, verbose=verbose
            )

            results[track_name] = result
            if result["success"]:
                successful += 1

        # Calculate aggregate statistics
        if successful > 0:
            avg_speeds = [
                r["average_speed_kmh"] for r in results.values() if r["success"]
            ]
            total_distance = sum(
                r["total_distance_km"] for r in results.values() if r["success"]
            )
            total_time = sum(
                r["total_time_s"] for r in results.values() if r["success"]
            )
            total_energy = sum(
                r.get("energy_consumed_kWh", 0)
                for r in results.values()
                if r["success"]
            )

            aggregate_stats = {
                "total_tracks": len(tracks),
                "successful_simulations": successful,
                "success_rate": successful / len(tracks),
                "total_distance_km": total_distance,
                "total_time_hours": total_time / 3600,
                "overall_avg_speed_kmh": (
                    (total_distance / (total_time / 3600)) if total_time > 0 else 0
                ),
                "mean_track_speed_kmh": np.mean(avg_speeds),
                "speed_std_kmh": np.std(avg_speeds),
                "total_energy_kWh": total_energy,
                "overall_efficiency_kWh_per_km": (
                    total_energy / total_distance if total_distance > 0 else 0
                ),
            }

            results["_aggregate_stats"] = aggregate_stats

        return results
