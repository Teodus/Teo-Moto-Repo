"""Track data processing with improved filtering and validation."""

import pandas as pd
import numpy as np
from typing import Optional, Tuple


class TrackProcessor:
    """Handles track data processing with consistent filtering and validation."""

    def __init__(
        self,
        min_speed_kmh: float = 10.0,
        max_speed_kmh: float = 300.0,
        min_time_delta_s: float = 0.1,
        max_time_delta_s: float = 60.0,
    ):
        """
        Initialize track processor with configurable parameters.

        Parameters
        ----------
        min_speed_kmh : float
            Minimum speed in km/h to consider as moving (default: 10.0)
        max_speed_kmh : float
            Maximum realistic speed in km/h (default: 300.0)
        min_time_delta_s : float
            Minimum time delta between points in seconds (default: 0.1)
        max_time_delta_s : float
            Maximum time delta between points in seconds (default: 60.0)
        """
        self.min_speed_ms = min_speed_kmh / 3.6
        self.max_speed_ms = max_speed_kmh / 3.6
        self.min_time_delta = min_time_delta_s
        self.max_time_delta = max_time_delta_s

    def process_track_data(
        self,
        trajectory_df: pd.DataFrame,
        filter_stops: bool = True,
        validate_speeds: bool = True,
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Process track data with consistent filtering and validation.

        Parameters
        ----------
        trajectory_df : pd.DataFrame
            Raw trajectory data with Distance, Elevation, Target Time, Target Speed
        filter_stops : bool
            Whether to filter out stopped sections
        validate_speeds : bool
            Whether to validate and correct unrealistic speeds

        Returns
        -------
        processed_df : pd.DataFrame
            Processed trajectory data
        stats : dict
            Processing statistics and warnings
        """
        stats = {
            "original_points": len(trajectory_df),
            "filtered_points": 0,
            "avg_speed_original_kmh": 0,
            "avg_speed_processed_kmh": 0,
            "warnings": [],
        }

        # Make a copy to avoid modifying original
        df = trajectory_df.copy()

        # Calculate original average speed
        if len(df) > 1:
            total_distance = df["Distance"].iloc[-1] - df["Distance"].iloc[0]
            total_time = df["Target Time"].iloc[-1] - df["Target Time"].iloc[0]
            if total_time > 0:
                stats["avg_speed_original_kmh"] = (total_distance / total_time) * 3.6

        # Validate time deltas
        if len(df) > 1:
            time_deltas = np.diff(df["Target Time"])

            # Check for invalid time deltas
            invalid_small = np.sum(time_deltas < self.min_time_delta)
            invalid_large = np.sum(time_deltas > self.max_time_delta)

            if invalid_small > 0:
                stats["warnings"].append(
                    f"Found {invalid_small} time intervals < {self.min_time_delta}s"
                )
            if invalid_large > 0:
                stats["warnings"].append(
                    f"Found {invalid_large} time intervals > {self.max_time_delta}s"
                )

        # Validate and correct speeds if requested
        if validate_speeds and "Target Speed" in df.columns:
            # Apply speed bounds
            original_speeds = df["Target Speed"].copy()
            df["Target Speed"] = np.clip(
                df["Target Speed"], 0.0, self.max_speed_ms  # Allow zero speed
            )

            # Check for speed corrections
            speed_corrections = np.sum(df["Target Speed"] != original_speeds)
            if speed_corrections > 0:
                stats["warnings"].append(
                    f"Corrected {speed_corrections} unrealistic speed values"
                )

        # Filter stops if requested
        if filter_stops and "Target Speed" in df.columns:
            # Mark moving sections
            is_moving = df["Target Speed"] >= self.min_speed_ms

            # Group consecutive moving/stopped sections
            groups = (is_moving != is_moving.shift()).cumsum()

            # Calculate group statistics
            group_stats = df.groupby(groups).agg(
                {"Target Speed": "mean", "Target Time": ["min", "max", "count"]}
            )

            # Flatten column names
            group_stats.columns = ["avg_speed", "start_time", "end_time", "count"]
            group_stats["duration"] = (
                group_stats["end_time"] - group_stats["start_time"]
            )
            group_stats["is_moving"] = group_stats["avg_speed"] >= self.min_speed_ms

            # Keep only moving sections with sufficient duration (at least 2 seconds)
            valid_groups = group_stats[
                (group_stats["is_moving"]) & (group_stats["duration"] >= 2.0)
            ].index

            # Filter dataframe
            df = df[groups.isin(valid_groups)].copy()

            if len(df) > 0:
                # Reset index and recalculate continuous time
                df = df.reset_index(drop=True)

                # Recalculate time to be continuous
                if len(df) > 1:
                    # Calculate actual time intervals between consecutive points
                    time_intervals = []
                    for i in range(1, len(df)):
                        # Use distance and speed to estimate time interval
                        dist_delta = df["Distance"].iloc[i] - df["Distance"].iloc[i - 1]
                        avg_speed = (
                            df["Target Speed"].iloc[i] + df["Target Speed"].iloc[i - 1]
                        ) / 2

                        if avg_speed > 0.1:  # Avoid division by very small numbers
                            time_interval = dist_delta / avg_speed
                            # Bound the time interval
                            time_interval = np.clip(
                                time_interval, self.min_time_delta, self.max_time_delta
                            )
                        else:
                            time_interval = self.min_time_delta

                        time_intervals.append(time_interval)

                    # Reconstruct time array
                    new_times = [0.0]
                    for interval in time_intervals:
                        new_times.append(new_times[-1] + interval)

                    df["Target Time"] = new_times

                stats["filtered_points"] = len(df)
                removed_pct = (1 - len(df) / len(trajectory_df)) * 100
                stats["warnings"].append(
                    f"Filtered {removed_pct:.1f}% of points (stops < {self.min_speed_ms * 3.6:.1f} km/h)"
                )
        else:
            stats["filtered_points"] = len(df)

        # Calculate processed average speed
        if len(df) > 1:
            total_distance = df["Distance"].iloc[-1] - df["Distance"].iloc[0]
            total_time = df["Target Time"].iloc[-1] - df["Target Time"].iloc[0]
            if total_time > 0:
                stats["avg_speed_processed_kmh"] = (total_distance / total_time) * 3.6

        return df, stats

    def validate_achieved_speeds(
        self, target_speeds: list, achieved_speeds: list, time_deltas: list
    ) -> Tuple[list, dict]:
        """
        Validate and correct achieved speeds from simulation.

        Parameters
        ----------
        target_speeds : list
            Target speeds in m/s
        achieved_speeds : list
            Achieved speeds from simulation in m/s
        time_deltas : list
            Time intervals in seconds

        Returns
        -------
        corrected_speeds : list
            Validated and corrected speeds
        validation_stats : dict
            Validation statistics
        """
        validation_stats = {"corrections": 0, "max_correction": 0, "warnings": []}

        corrected_speeds = []

        for i, (target, achieved, dt) in enumerate(
            zip(target_speeds, achieved_speeds, time_deltas)
        ):
            # Apply realistic bounds
            corrected = np.clip(achieved, 0.0, self.max_speed_ms)

            # Check for large deviations from target
            if abs(corrected - target) > 20.0:  # More than 20 m/s difference
                validation_stats["warnings"].append(
                    f"Large speed deviation at point {i}: "
                    f"target={target*3.6:.1f} km/h, achieved={achieved*3.6:.1f} km/h"
                )

            # Track corrections
            if corrected != achieved:
                validation_stats["corrections"] += 1
                validation_stats["max_correction"] = max(
                    validation_stats["max_correction"], abs(corrected - achieved)
                )

            corrected_speeds.append(corrected)

        return corrected_speeds, validation_stats
