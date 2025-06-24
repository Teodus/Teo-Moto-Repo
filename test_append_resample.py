#!/usr/bin/env python3
"""Test the actual append_and_resample_dataframe function."""

import pandas as pd
import numpy as np
import traceback
from ithaka_powertrain_sim.trajectory import load_gpx, append_and_resample_dataframe

def test_append_and_resample(track_name, file_path):
    """Test the append_and_resample_dataframe function directly."""
    print(f"\n{'='*60}")
    print(f"Testing append_and_resample_dataframe for {track_name}")
    print('='*60)
    
    try:
        # Load GPX
        print("\n1. Loading GPX...")
        df = load_gpx(file_path)
        print(f"   ✓ Loaded {len(df)} points")
        
        # Test append_and_resample_dataframe with different settings
        print("\n2. Testing append_and_resample_dataframe...")
        
        # Test 1: Default settings
        print("\n   a) Default settings (smoothing=True, resampling=True)...")
        try:
            result1 = append_and_resample_dataframe(df.copy())
            print(f"      ✓ Success: {len(result1)} points")
        except Exception as e:
            print(f"      ✗ Failed: {type(e).__name__}: {e}")
            traceback.print_exc()
        
        # Test 2: No resampling
        print("\n   b) Without resampling (smoothing=True, resampling=False)...")
        try:
            result2 = append_and_resample_dataframe(df.copy(), apply_resampling=False)
            print(f"      ✓ Success: {len(result2)} points")
        except Exception as e:
            print(f"      ✗ Failed: {type(e).__name__}: {e}")
            traceback.print_exc()
        
        # Test 3: No smoothing
        print("\n   c) Without smoothing (smoothing=False, resampling=True)...")
        try:
            result3 = append_and_resample_dataframe(df.copy(), apply_smoothing=False)
            print(f"      ✓ Success: {len(result3)} points")
        except Exception as e:
            print(f"      ✗ Failed: {type(e).__name__}: {e}")
            traceback.print_exc()
        
        # Test 4: With filtering
        print("\n   d) With stop filtering (filter_stops=True)...")
        try:
            result4 = append_and_resample_dataframe(df.copy(), filter_stops=True)
            print(f"      ✓ Success: {len(result4)} points")
        except Exception as e:
            print(f"      ✗ Failed: {type(e).__name__}: {e}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()

# Test both tracks
test_append_and_resample("D126", "/home/teocasares/Teo-Moto-Repo/docs/gpx_files/d126-mancos-kanab.gpx")
test_append_and_resample("D75", "/home/teocasares/Teo-Moto-Repo/docs/gpx_files/d75-cuzco-pillcopata.gpx")