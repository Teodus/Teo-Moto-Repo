#!/usr/bin/env python3
"""Trace the exact location of the reindex error."""

import pandas as pd
import numpy as np
import traceback
from ithaka_powertrain_sim.trajectory import load_gpx

def test_resampling_step_by_step(track_name, file_path):
    """Test each step of the trajectory processing to find where error occurs."""
    print(f"\n{'='*60}")
    print(f"Testing {track_name} step by step")
    print('='*60)
    
    try:
        # Step 1: Load GPX
        print("\n1. Loading GPX file...")
        df = load_gpx(file_path)
        print(f"   ✓ Loaded {len(df)} points")
        print(f"   - Columns: {list(df.columns)}")
        
        # Step 2: Check initial data
        print("\n2. Checking initial data...")
        print(f"   - Target DateTime unique: {df['Target DateTime'].is_unique}")
        print(f"   - Duplicates: {df['Target DateTime'].duplicated().sum()}")
        
        # Step 3: Manual resampling process (mimicking append_and_resample_dataframe)
        print("\n3. Testing resampling process...")
        
        # Add Target DateTime if missing
        if "Target DateTime" not in df:
            df["Target DateTime"] = pd.to_datetime(df["Target Time"], unit="s")
        
        # Remove duplicates
        print("   a) Removing duplicates...")
        df_clean = df.drop_duplicates(subset=['Target DateTime'], keep='first')
        print(f"      - After drop_duplicates: {len(df_clean)} points")
        
        # Sort by datetime
        print("   b) Sorting by datetime...")
        df_clean = df_clean.sort_values('Target DateTime')
        
        # Filter minimum intervals
        print("   c) Filtering minimum intervals...")
        time_diffs = df_clean['Target DateTime'].diff()
        min_interval = pd.Timedelta(seconds=1)
        mask = (time_diffs >= min_interval) | (time_diffs.isna())
        df_filtered = df_clean[mask].reset_index(drop=True)
        print(f"      - After interval filter: {len(df_filtered)} points")
        
        # Check uniqueness before set_index
        print("   d) Checking uniqueness before set_index...")
        is_unique = df_filtered['Target DateTime'].is_unique
        print(f"      - Is unique: {is_unique}")
        
        if not is_unique:
            # Find the duplicates
            dup_mask = df_filtered['Target DateTime'].duplicated(keep=False)
            duplicates = df_filtered[dup_mask]['Target DateTime']
            print(f"      - Found {len(duplicates)} duplicate values:")
            print(duplicates.head(10))
        
        # Try set_index
        print("   e) Attempting set_index...")
        try:
            df_indexed = df_filtered.set_index("Target DateTime")
            print("      ✓ set_index successful")
        except Exception as e:
            print(f"      ✗ set_index failed: {type(e).__name__}: {e}")
            raise
        
        # Try resample
        print("   f) Attempting resample...")
        try:
            df_resampled = df_indexed.resample(rule="1s").interpolate(method="linear")
            print(f"      ✓ resample successful: {len(df_resampled)} points")
        except Exception as e:
            print(f"      ✗ resample failed: {type(e).__name__}: {e}")
            
            # Try to understand why
            print("\n   Investigating resample failure...")
            print(f"   - Index type: {type(df_indexed.index)}")
            print(f"   - Index is unique: {df_indexed.index.is_unique}")
            print(f"   - Index has NaT: {df_indexed.index.isna().any()}")
            
            # Check for microsecond precision issues
            print("\n   Checking for microsecond precision duplicates...")
            # Round to seconds to see if there are duplicates at second precision
            rounded_index = df_indexed.index.round('S')
            rounded_dups = rounded_index.duplicated().sum()
            print(f"   - Duplicates when rounded to seconds: {rounded_dups}")
            
            if rounded_dups > 0:
                print("   - This is likely the issue! Multiple points within same second.")
                dup_seconds = rounded_index[rounded_index.duplicated(keep=False)]
                print(f"   - First few duplicate seconds: {dup_seconds.unique()[:5]}")
            
            raise
        
        print("\n✅ All steps completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {type(e).__name__}: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

# Test both problematic tracks
test_resampling_step_by_step("D126", "/home/teocasares/Teo-Moto-Repo/docs/gpx_files/d126-mancos-kanab.gpx")
test_resampling_step_by_step("D75", "/home/teocasares/Teo-Moto-Repo/docs/gpx_files/d75-cuzco-pillcopata.gpx")