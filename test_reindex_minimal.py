#!/usr/bin/env python3
"""Minimal test to reproduce the reindex error."""

import pandas as pd
import numpy as np

def test_reindex_scenarios():
    """Test different scenarios that could cause reindex errors."""
    
    print("Testing pandas reindex scenarios that could cause the error...\n")
    
    # Scenario 1: DataFrame with duplicate index
    print("1. Testing DataFrame.join with duplicate index:")
    df1 = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': [5, 6, 7, 8]
    }, index=[0, 1, 1, 2])  # Duplicate index at position 1
    
    df2 = pd.DataFrame({
        'C': [9, 10, 11, 12],
        'D': [13, 14, 15, 16]
    }, index=[0, 1, 2, 3])
    
    try:
        result = df1.join(df2)
        print("   ✓ Join succeeded (unexpected)")
    except Exception as e:
        print(f"   ✗ Join failed: {type(e).__name__}: {e}")
    
    # Scenario 2: Resample with duplicate DatetimeIndex
    print("\n2. Testing resample with duplicate DatetimeIndex:")
    dates = pd.date_range('2023-01-01', periods=4, freq='H')
    dates_with_dup = pd.DatetimeIndex([dates[0], dates[1], dates[1], dates[3]])  # Duplicate
    
    df3 = pd.DataFrame({
        'value': [1, 2, 3, 4]
    }, index=dates_with_dup)
    
    try:
        result = df3.resample('30T').mean()
        print("   ✓ Resample succeeded (unexpected)")
    except Exception as e:
        print(f"   ✗ Resample failed: {type(e).__name__}: {e}")
    
    # Scenario 3: GroupBy with MultiIndex aggregation
    print("\n3. Testing groupby with MultiIndex column result:")
    df4 = pd.DataFrame({
        'group': [1, 1, 2, 2],
        'value': [10, 20, 30, 40],
        'time': [1, 2, 1, 2]
    })
    
    # This creates MultiIndex columns
    grouped = df4.groupby('group').agg({
        'value': 'mean',
        'time': ['min', 'max']
    })
    
    print(f"   - Grouped columns: {grouped.columns}")
    print(f"   - Is MultiIndex: {isinstance(grouped.columns, pd.MultiIndex)}")
    
    # Try to flatten and use
    try:
        grouped.columns = ['avg_value', 'min_time', 'max_time']
        print("   ✓ Column flattening succeeded")
    except Exception as e:
        print(f"   ✗ Column flattening failed: {type(e).__name__}: {e}")
    
    # Scenario 4: Concat with duplicate indices
    print("\n4. Testing pd.concat with potential index issues:")
    df5 = pd.DataFrame({'A': [1, 2, 3]}, index=[0, 1, 2])
    df6 = pd.DataFrame({'B': [4, 5, 6]}, index=[0, 1, 2])
    
    try:
        # This should work
        result = pd.concat([df5, df6], axis=1)
        print("   ✓ Concat succeeded")
        
        # But what if indices don't match perfectly?
        df7 = pd.DataFrame({'C': [7, 8, 9, 10]}, index=[0, 1, 2, 3])
        result2 = pd.concat([df5, df7], axis=1)
        print("   ✓ Concat with mismatched indices succeeded")
    except Exception as e:
        print(f"   ✗ Concat failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_reindex_scenarios()