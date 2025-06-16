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
        input_dataframe = (
            input_dataframe.set_index("Target DateTime")
            .resample(rule="1s")
            .interpolate(method="linear")
            .reset_index()
        )

    input_dataframe["Target Speed"] = np.gradient(
        input_dataframe["Distance"], input_dataframe["Target Time"]
    )
    input_dataframe["Target Speed"] = np.clip(
        input_dataframe["Target Speed"], 1 * 1e-3, None
    )

    return input_dataframe


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
