import pandas as pd
import numpy as np

from collections.abc import Iterable

import gpxpy
import json
from geopy.distance import geodesic


def append_and_resample_dataframe(
    input_dataframe: pd.DataFrame,
    apply_smoothing: bool = True,
    apply_resampling: bool = True,
    filter_stops: bool = False,
    min_speed_kmh: float = 5.0,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    input_dataframe : pd.DataFrame
        The input dataframe containing the data to be appended and resampled.
    apply_smoothing : bool, optional
        A flag indicating whether to apply smoothing to the data. The default is True.
    apply_resampling : bool, optional
        A flag indicating whether to apply resampling to the data. The default is True.
    filter_stops : bool, optional
        A flag indicating whether to filter out stopped sections. The default is False.
    min_speed_kmh : float, optional
        Minimum speed in km/h to consider as moving (only used if filter_stops=True). Default is 5.0.

    Returns
    -------
    pd.DataFrame
        The processed dataframe with the appended and resampled data.

    """
    if "Target DateTime" not in input_dataframe:
        input_dataframe["Target DateTime"] = pd.to_datetime(
            input_dataframe["Target Time"], unit="s"
        )

    if apply_smoothing:
        input_dataframe["Distance"] = smooth_data(input_dataframe["Distance"])
        input_dataframe["Elevation"] = smooth_data(input_dataframe["Elevation"])

    if apply_resampling:
        # Handle duplicate timestamps by removing duplicates and ensuring minimum time intervals
        input_dataframe = input_dataframe.drop_duplicates(subset=['Target DateTime'], keep='first')
        
        # Ensure minimum time difference between consecutive points (1 second)
        input_dataframe = input_dataframe.sort_values('Target DateTime')
        time_diffs = input_dataframe['Target DateTime'].diff()
        min_interval = pd.Timedelta(seconds=1)
        
        # Keep only points that are at least 1 second apart
        mask = (time_diffs >= min_interval) | (time_diffs.isna())  # Keep first point
        input_dataframe = input_dataframe[mask].reset_index(drop=True)
        
        # Final check for any remaining duplicates before resampling
        remaining_duplicates = input_dataframe['Target DateTime'].duplicated().sum()
        if remaining_duplicates > 0:
            print(f"Warning: Found {remaining_duplicates} remaining duplicate timestamps after filtering")
            # Remove any remaining duplicates as a last resort
            input_dataframe = input_dataframe.drop_duplicates(subset=['Target DateTime'], keep='first')
        
        # Update Target Time after filtering
        input_dataframe["Target Time"] = (
            input_dataframe["Target DateTime"]
            - input_dataframe["Target DateTime"].iloc[0]
        ).dt.total_seconds()
        
        try:
            # Double-check for unique index before resampling
            if input_dataframe['Target DateTime'].is_unique:
                input_dataframe = (
                    input_dataframe.set_index("Target DateTime")
                    .resample(rule="1s")
                    .interpolate(method="linear")
                    .reset_index()
                )
            else:
                print("Warning: Non-unique datetime values found, skipping resampling")
        except Exception as e:
            print(f"Warning: Resampling failed ({e}), using original data")
            # Fall back to original data without resampling
            pass

    # Calculate speed with validation for realistic values
    time_intervals = np.diff(input_dataframe["Target Time"])
    if len(time_intervals) > 0 and np.min(time_intervals) < 0.1:
        print(f"Warning: Very small time intervals detected (min: {np.min(time_intervals):.3f}s)")
    
    input_dataframe["Target Speed"] = np.gradient(
        input_dataframe["Distance"], input_dataframe["Target Time"]
    )
    
    # Apply realistic speed bounds for motorcycles (0.001 m/s to 100 m/s = 360 km/h)
    input_dataframe["Target Speed"] = np.clip(
        input_dataframe["Target Speed"], 1 * 1e-3, 100.0
    )
    
    # Filter out stopped sections if requested
    if filter_stops and len(input_dataframe) > 0:
        print(f"\nFiltering stopped sections (< {min_speed_kmh} km/h)...")
        input_dataframe = filter_stopped_sections(input_dataframe, min_speed_kmh=min_speed_kmh)

    return input_dataframe


def filter_stopped_sections(
    input_dataframe: pd.DataFrame,
    min_speed_kmh: float = 5.0,
    min_duration_seconds: int = 5
) -> pd.DataFrame:
    """
    Filter out stopped or very slow sections from trajectory data.
    
    Parameters
    ----------
    input_dataframe : pd.DataFrame
        The trajectory dataframe with speed data
    min_speed_kmh : float, optional
        Minimum speed in km/h to consider as moving. Default is 5.0 km/h
    min_duration_seconds : int, optional
        Minimum duration in seconds for a moving segment. Default is 5 seconds
        
    Returns
    -------
    pd.DataFrame
        Filtered dataframe with stopped sections removed
    """
    # Convert minimum speed to m/s
    min_speed_ms = min_speed_kmh / 3.6
    
    # Identify moving sections
    is_moving = input_dataframe["Target Speed"] >= min_speed_ms
    
    # Group consecutive moving/stopped sections
    # This creates groups where each group is either all moving or all stopped
    groups = (is_moving != is_moving.shift()).cumsum()
    
    # Calculate duration for each group
    # Use named aggregations to avoid MultiIndex columns
    group_info = input_dataframe.groupby(groups).agg(
        avg_speed=('Target Speed', 'mean'),
        start_time=('Target Time', 'min'),
        end_time=('Target Time', 'max'),
        count=('Target Time', 'count')
    )
    group_info['duration'] = group_info['end_time'] - group_info['start_time']
    group_info['is_moving'] = group_info['avg_speed'] >= min_speed_ms
    
    # Identify valid groups (moving with sufficient duration)
    valid_groups = group_info[
        (group_info['is_moving']) & 
        (group_info['duration'] >= min_duration_seconds)
    ].index
    
    # Keep only rows from valid groups
    filtered_df = input_dataframe[groups.isin(valid_groups)].copy()
    
    # Recalculate time to be continuous
    if len(filtered_df) > 0:
        filtered_df = filtered_df.reset_index(drop=True)
        # Recalculate cumulative time
        time_diffs = np.diff(filtered_df["Target Time"], prepend=filtered_df["Target Time"].iloc[0])
        time_diffs[0] = 0  # First point starts at 0
        filtered_df["Target Time"] = np.cumsum(time_diffs)
        
        # Report filtering results
        original_duration = input_dataframe["Target Time"].max() - input_dataframe["Target Time"].min()
        filtered_duration = filtered_df["Target Time"].max() - filtered_df["Target Time"].min()
        removed_pct = (1 - len(filtered_df) / len(input_dataframe)) * 100
        
        print(f"Filtered out {removed_pct:.1f}% of data points")
        print(f"Original duration: {original_duration/3600:.1f}h, Filtered duration: {filtered_duration/3600:.1f}h")
        print(f"Average speed increased from {input_dataframe['Target Speed'].mean()*3.6:.1f} to {filtered_df['Target Speed'].mean()*3.6:.1f} km/h")
    
    return filtered_df


def smooth_data(data_column: Iterable[float], window_size: int = 5) -> np.ndarray:
    """
    Parameters
    ----------
    data_column : Iterable[float]
        The data column to be smoothed.

    window_size : int, optional
        The size of the window used for smoothing the data. Default is 5.

    Returns
    -------
    smoothed_data : np.ndarray
        The smoothed data column.

    """
    smoothed_data = np.convolve(
        data_column, np.ones(window_size) / window_size, mode="same"
    )
    return smoothed_data


def load_gpx(file_path: str) -> pd.DataFrame:
    """
    Parameters
    ----------
    file_path : str
        The file path of the GPX file to be loaded.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the following columns:
            - "Target DateTime": The timestamp of each track point.
            - "Target Time": The time difference in seconds between each track point and the first track point.
            - "Elevation": The elevation of each track point.
            - "Distance": The cumulative distance from the first track point, taking into account both the flat horizontal distance and the elevation change.

    Notes
    -----
    This method loads a GPX file and extracts track points to create a DataFrame. It calculates the target time, elevation, and cumulative distance from the first track point.
    """
    with open(file_path, "r") as file:
        gpx = gpxpy.parse(file)

    track_points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                track_points.append(
                    {
                        "Latitude": point.latitude,
                        "Longitude": point.longitude,
                        "Elevation": point.elevation,
                        "Target DateTime": point.time,
                    }
                )

    gpx_dataframe = pd.DataFrame(track_points)
    coordinates = gpx_dataframe[["Latitude", "Longitude"]].values

    output_dataframe = pd.DataFrame()

    output_dataframe["Target DateTime"] = gpx_dataframe["Target DateTime"]
    output_dataframe["Target Time"] = (
        output_dataframe["Target DateTime"]
        - output_dataframe["Target DateTime"].iloc[0]
    ).dt.total_seconds()

    output_dataframe["Elevation"] = gpx_dataframe["Elevation"]

    delta_flat_distances = np.array(
        [
            geodesic(coordinates[index], coordinates[index + 1]).meters
            for index in range(len(coordinates) - 1)
        ]
    )
    delta_elevation = np.diff(output_dataframe["Elevation"])
    delta_total_distance = np.sqrt(delta_flat_distances**2 + delta_elevation**2)

    total_distance = np.cumsum(delta_total_distance)
    total_distance = np.pad(total_distance, (1, 0), "constant")

    output_dataframe["Distance"] = total_distance

    return output_dataframe


def load_json(file_path: str) -> pd.DataFrame:
    """
    Parameters
    ----------
    file_path : str
        The file path of the JSON file to load.

    Returns
    -------
    output_dataframe : pd.DataFrame
        The loaded JSON data as a Pandas DataFrame.

    """
    with open(file_path, "r") as file:
        json_data = json.load(file)

    json_dataframe = pd.DataFrame(json_data["coords"])

    output_dataframe = pd.DataFrame()

    output_dataframe["Target DateTime"] = pd.to_datetime(
        json_dataframe["timestamp"], unit="s"
    )
    output_dataframe["Target Time"] = (
        output_dataframe["Target DateTime"]
        - output_dataframe["Target DateTime"].iloc[0]
    ).dt.total_seconds()

    output_dataframe["Elevation"] = json_dataframe["alt"]

    output_dataframe["Distance"] = (
        json_dataframe["distance"] - json_dataframe["distance"].iloc[0]
    ) * 1000.0

    return output_dataframe
