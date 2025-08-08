"""Test file to measure code coverage for all analysis steps"""

import pytest
import pandas as pd
import os
import sys


def test_step1_import():
    """Test Step 1: CSV import functionality"""
    # Import the actual step1 module
    import python.step1_csv_import as step1_csv_import

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
    import python.step2_nps_analysis as step2_nps_analysis

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
    import python.step3_visualizations as step3_visualizations

    # Verify the output files were created
    assert os.path.exists("images/nps_analysis.png")
    assert os.path.exists("images/nps_distribution.png")

    # Test file sizes (should be reasonable for PNG files)
    assert os.path.getsize("images/nps_analysis.png") > 1000
    assert os.path.getsize("images/nps_distribution.png") > 1000


def test_step4_word_cloud():
    """Test Step 4: Word cloud analysis functionality"""
    # Import the actual step4 module
    import python.step4_word_cloud as step4_word_cloud

    # Verify the output files were created
    assert os.path.exists("images/improvement_wordcloud.png")
    assert os.path.exists("csv/improvement_categories.csv")

    # Test file sizes (should be reasonable for PNG files)
    assert os.path.getsize("images/improvement_wordcloud.png") > 1000
    assert os.path.getsize("csv/improvement_categories.csv") > 100


def test_step5_track_improvements():
    """Test Step 5: Track-specific improvement analysis functionality"""
    # Import the actual step5 module
    import python.step5_track_improvements as step5_track_improvements

    # Verify the output files were created
    assert os.path.exists("images/track_improvements.png")
    assert os.path.exists("csv/track_improvements.csv")

    # Test file sizes (should be reasonable for PNG files)
    assert os.path.getsize("images/track_improvements.png") > 1000
    assert os.path.getsize("csv/track_improvements.csv") > 100


def test_step6_session_rankings():
    """Test Step 6: Session rankings analysis functionality"""
    # Import the actual step6 module
    import python.step6_session_rankings as step6_session_rankings

    # Verify the output files were created
    assert os.path.exists("images/session_rankings.png")
    assert os.path.exists("csv/session_rankings.csv")

    # Test file sizes (should be reasonable for PNG files)
    assert os.path.getsize("images/session_rankings.png") > 1000
    assert os.path.getsize("csv/session_rankings.csv") > 100


if __name__ == "__main__":
    # Run all tests
    test_step1_import()
    test_step2_nps()
    test_step3_visualizations()
    test_step4_word_cloud()
    test_step5_track_improvements()
    test_step6_session_rankings()
    print("All tests passed!")
