#!/usr/bin/env python3
"""Test the full simulation workflow to reproduce the reindex error."""

import pandas as pd
import numpy as np
import traceback
from ithaka_powertrain_sim.trajectory import load_gpx, append_and_resample_dataframe
from ithaka_powertrain_sim.motorbike import Motorbike
from ithaka_powertrain_sim.component_library import create_motorcycle

def simulate_track(track_name, track_file):
    """Simulate the exact workflow from the notebook."""
    print(f"\n{'='*60}")
    print(f"Simulating full workflow for {track_name}")
    print('='*60)
    
    try:
        # Create a motorcycle
        print("\n1. Creating motorcycle...")
        motorcycle = create_motorcycle("Sport EV")
        print(f"   ✓ Created: {motorcycle.name}")
        
        # Load and process trajectory
        print("\n2. Loading trajectory...")
        trajectory_df = load_gpx(track_file)
        print(f"   ✓ Loaded: {len(trajectory_df)} points")
        
        print("\n3. Processing trajectory with append_and_resample_dataframe...")
        trajectory_df = append_and_resample_dataframe(trajectory_df)
        print(f"   ✓ Processed: {len(trajectory_df)} points")
        
        # Extract parameters (like in notebook)
        print("\n4. Extracting parameters...")
        target_speed = trajectory_df["Target Speed"].to_list()
        delta_distance = np.diff(trajectory_df["Distance"], prepend=0).tolist()
        delta_elevation = np.diff(trajectory_df["Elevation"], prepend=0).tolist()
        approximate_time = trajectory_df["Target Time"].to_list()
        print(f"   ✓ Extracted {len(target_speed)} speed points")
        
        # Run simulation
        print("\n5. Running simulation...")
        achieved_speeds = [trajectory_df["Target Speed"].iloc[0]]
        reporting_dataframe_rows = []
        
        # Just simulate first 100 points for testing
        max_points = min(100, len(trajectory_df))
        
        for index in range(1, max_points):
            delta_time = approximate_time[index] - approximate_time[index - 1]
            
            achieved_speed, reporting_dataframe_row = motorcycle.calculate_achieved_speed(
                achieved_speeds[index - 1], target_speed[index], delta_time,
                delta_distance[index], delta_elevation[index]
            )
            
            achieved_speeds.append(achieved_speed)
            reporting_dataframe_rows.append(reporting_dataframe_row)
        
        print(f"   ✓ Simulated {len(achieved_speeds)} points")
        
        # Combine results (this is where the error might occur)
        print("\n6. Combining results...")
        motorbike_dataframe = trajectory_df.iloc[:max_points].copy()
        motorbike_dataframe["Approximate Time"] = approximate_time[:max_points]
        motorbike_dataframe["Achieved Speed"] = achieved_speeds
        
        if reporting_dataframe_rows:
            print("   a) Concatenating reporting dataframes...")
            reporting_dataframe = pd.concat(reporting_dataframe_rows, ignore_index=True)
            print(f"      ✓ Created reporting dataframe: {reporting_dataframe.shape}")
            
            # This is the critical part - try different join methods
            print("\n   b) Testing join operations...")
            
            # Method 1: Original join (might fail)
            print("      - Testing original join method...")
            try:
                test_df = motorbike_dataframe.copy()
                final_results = test_df.join(reporting_dataframe)
                print("        ✓ Original join succeeded")
            except Exception as e:
                print(f"        ✗ Original join failed: {type(e).__name__}: {e}")
            
            # Method 2: Reset index then join
            print("      - Testing reset_index + join...")
            try:
                test_df = motorbike_dataframe.copy().reset_index(drop=True)
                test_reporting = reporting_dataframe.reset_index(drop=True)
                final_results = test_df.join(test_reporting)
                print("        ✓ Reset index + join succeeded")
            except Exception as e:
                print(f"        ✗ Reset index + join failed: {type(e).__name__}: {e}")
            
            # Method 3: pd.concat
            print("      - Testing pd.concat...")
            try:
                test_df = motorbike_dataframe.copy().reset_index(drop=True)
                test_reporting = reporting_dataframe.reset_index(drop=True)
                final_results = pd.concat([test_df, test_reporting], axis=1)
                print("        ✓ pd.concat succeeded")
            except Exception as e:
                print(f"        ✗ pd.concat failed: {type(e).__name__}: {e}")
        
        print("\n✅ Workflow completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

# Test both problematic tracks
simulate_track("D126", "/home/teocasares/Teo-Moto-Repo/docs/gpx_files/d126-mancos-kanab.gpx")
simulate_track("D75", "/home/teocasares/Teo-Moto-Repo/docs/gpx_files/d75-cuzco-pillcopata.gpx")