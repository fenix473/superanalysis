"""Test file to measure code coverage for all analysis steps"""

import pytest
import pandas as pd
import os
import sys


def test_step1_import():
    """Test Step 1: CSV import functionality"""
    # Import the actual step1 module
    import step1_csv_import
    
    # Verify the output file was created
    assert os.path.exists("csv/imported_data.csv")
    
    # Test that we can read the output
    df = pd.read_csv("csv/imported_data.csv")
    assert len(df) == 54
    assert len(df.columns) == 11
    assert 'TRACK' in df.columns


def test_step2_nps():
    """Test Step 2: NPS calculation functionality"""
    # Import the actual step2 module
    import step2_nps_analysis
    
    # Verify the output file was created
    assert os.path.exists("csv/nps_results.csv")
    
    # Test that we can read the results
    results = pd.read_csv("csv/nps_results.csv", index_col=0)
    assert len(results) == 4  # Overall + 3 tracks
    assert 'Overall' in results.index
    assert 'EXEC' in results.index
    assert 'PROD' in results.index
    assert 'DEV' in results.index


def test_step3_visualizations():
    """Test Step 3: Visualization functionality"""
    # Import the actual step3 module
    import step3_visualizations
    
    # Verify the output files were created
    assert os.path.exists("images/nps_analysis.png")
assert os.path.exists("images/nps_distribution.png")
    
    # Test file sizes (should be reasonable for PNG files)
    assert os.path.getsize("images/nps_analysis.png") > 1000
assert os.path.getsize("images/nps_distribution.png") > 1000


if __name__ == "__main__":
    # Run all tests
    test_step1_import()
    test_step2_nps()
    test_step3_visualizations()
    print("All tests passed!")
