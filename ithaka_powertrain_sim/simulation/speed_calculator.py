"""Improved speed calculation utilities."""

import numpy as np
from typing import Tuple, Optional


class SpeedCalculator:
    """Handles various speed calculation methods with proper validation."""

    @staticmethod
    def calculate_average_speed(
        distances: np.ndarray, times: np.ndarray, method: str = "distance_time"
    ) -> Tuple[float, dict]:
        """
        Calculate average speed using specified method.

        Parameters
        ----------
        distances : np.ndarray
            Distance values in meters
        times : np.ndarray
            Time values in seconds
        method : str
            Method to use: 'distance_time', 'mean_speeds', or 'weighted'

        Returns
        -------
        avg_speed : float
            Average speed in m/s
        stats : dict
            Calculation statistics
        """
        stats = {
            "method": method,
            "total_distance_m": 0,
            "total_time_s": 0,
            "warnings": [],
        }

        if len(distances) < 2 or len(times) < 2:
            stats["warnings"].append("Insufficient data points")
            return 0.0, stats

        # Calculate basic statistics
        total_distance = distances[-1] - distances[0]
        total_time = times[-1] - times[0]

        stats["total_distance_m"] = total_distance
        stats["total_time_s"] = total_time

        if total_time <= 0:
            stats["warnings"].append("Invalid time range")
            return 0.0, stats

        if method == "distance_time":
            # Traditional average: total distance / total time
            avg_speed = total_distance / total_time

        elif method == "mean_speeds":
            # Mean of instantaneous speeds
            speeds = np.gradient(distances, times)
            # Filter out unrealistic values
            valid_speeds = speeds[(speeds >= 0) & (speeds < 100)]  # 0-360 km/h
            if len(valid_speeds) > 0:
                avg_speed = np.mean(valid_speeds)
            else:
                avg_speed = 0.0
                stats["warnings"].append("No valid speed measurements")

        elif method == "weighted":
            # Weighted average by time intervals
            if len(distances) > 2:
                speeds = np.gradient(distances, times)
                time_intervals = np.diff(times)

                # Filter valid segments
                valid_mask = (
                    (speeds[:-1] >= 0) & (speeds[:-1] < 100) & (time_intervals > 0)
                )

                if np.any(valid_mask):
                    valid_speeds = speeds[:-1][valid_mask]
                    valid_intervals = time_intervals[valid_mask]

                    # Weighted average
                    avg_speed = np.sum(valid_speeds * valid_intervals) / np.sum(
                        valid_intervals
                    )
                else:
                    avg_speed = total_distance / total_time
                    stats["warnings"].append("Falling back to distance/time method")
            else:
                avg_speed = total_distance / total_time

        else:
            raise ValueError(f"Unknown method: {method}")

        return avg_speed, stats

    @staticmethod
    def calculate_instantaneous_speeds(
        distances: np.ndarray, times: np.ndarray, smoothing_window: Optional[int] = None
    ) -> Tuple[np.ndarray, dict]:
        """
        Calculate instantaneous speeds with optional smoothing.

        Parameters
        ----------
        distances : np.ndarray
            Distance values in meters
        times : np.ndarray
            Time values in seconds
        smoothing_window : int, optional
            Window size for smoothing (None = no smoothing)

        Returns
        -------
        speeds : np.ndarray
            Instantaneous speeds in m/s
        stats : dict
            Calculation statistics
        """
        stats = {"smoothing_applied": smoothing_window is not None, "warnings": []}

        if len(distances) != len(times):
            raise ValueError("Distance and time arrays must have same length")

        if len(distances) < 2:
            stats["warnings"].append("Insufficient data points")
            return np.array([0.0]), stats

        # Check for very small time intervals
        time_diffs = np.diff(times)
        min_dt = np.min(time_diffs) if len(time_diffs) > 0 else 0

        if min_dt < 0.01:  # Less than 10ms
            stats["warnings"].append(
                f"Very small time intervals detected (min: {min_dt*1000:.1f}ms)"
            )

        # Apply smoothing to distances if requested
        if smoothing_window and smoothing_window > 1:
            # Ensure window size is odd
            window = (
                smoothing_window if smoothing_window % 2 == 1 else smoothing_window + 1
            )

            # Apply moving average
            kernel = np.ones(window) / window
            smoothed_distances = np.convolve(distances, kernel, mode="same")

            # Use smoothed distances for gradient
            speeds = np.gradient(smoothed_distances, times)
            stats["smoothing_window"] = window
        else:
            # Direct gradient calculation
            speeds = np.gradient(distances, times)

        # Validate speeds
        invalid_count = np.sum((speeds < 0) | (speeds > 100))  # 360 km/h max
        if invalid_count > 0:
            stats["warnings"].append(f"Found {invalid_count} invalid speed values")

        return speeds, stats

    @staticmethod
    def calculate_energy_efficiency(
        distances: np.ndarray, energies: np.ndarray, speeds: Optional[np.ndarray] = None
    ) -> Tuple[float, float, dict]:
        """
        Calculate energy efficiency metrics.

        Parameters
        ----------
        distances : np.ndarray
            Distance values in meters
        energies : np.ndarray
            Energy consumption values in Joules
        speeds : np.ndarray, optional
            Speed values in m/s for speed-dependent analysis

        Returns
        -------
        efficiency_kwh_per_km : float
            Overall efficiency in kWh/km
        efficiency_wh_per_km : float
            Overall efficiency in Wh/km
        stats : dict
            Efficiency statistics
        """
        stats = {"total_energy_kwh": 0, "total_distance_km": 0, "warnings": []}

        if len(distances) < 2 or len(energies) < 2:
            stats["warnings"].append("Insufficient data points")
            return 0.0, 0.0, stats

        # Calculate totals
        total_distance_m = distances[-1] - distances[0]
        total_energy_j = np.sum(np.diff(energies, prepend=0))

        if total_distance_m <= 0:
            stats["warnings"].append("Invalid distance range")
            return 0.0, 0.0, stats

        # Convert units
        total_distance_km = total_distance_m / 1000
        total_energy_kwh = total_energy_j / 3.6e6
        total_energy_wh = total_energy_j / 3600

        stats["total_energy_kwh"] = total_energy_kwh
        stats["total_distance_km"] = total_distance_km

        # Calculate efficiency
        efficiency_kwh_per_km = total_energy_kwh / total_distance_km
        efficiency_wh_per_km = total_energy_wh / total_distance_km

        # Speed-dependent analysis if speeds provided
        if speeds is not None and len(speeds) == len(distances):
            # Group by speed ranges
            speed_kmh = speeds * 3.6
            speed_bins = [0, 30, 60, 90, 120, 200]  # km/h ranges

            efficiency_by_speed = {}
            for i in range(len(speed_bins) - 1):
                mask = (speed_kmh >= speed_bins[i]) & (speed_kmh < speed_bins[i + 1])
                if np.any(mask):
                    # Calculate efficiency for this speed range
                    indices = np.where(mask)[0]
                    if len(indices) > 1:
                        range_distance = np.sum(np.diff(distances[indices]))
                        range_energy = np.sum(np.diff(energies[indices]))

                        if range_distance > 0:
                            range_efficiency = (range_energy / 3.6e6) / (
                                range_distance / 1000
                            )
                            efficiency_by_speed[
                                f"{speed_bins[i]}-{speed_bins[i+1]}kmh"
                            ] = {
                                "efficiency_kwh_per_km": range_efficiency,
                                "distance_km": range_distance / 1000,
                                "proportion": range_distance / total_distance_m,
                            }

            stats["efficiency_by_speed"] = efficiency_by_speed

        return efficiency_kwh_per_km, efficiency_wh_per_km, stats
