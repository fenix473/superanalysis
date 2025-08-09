"""Test coverage for step7_lowest_nps.py"""

import pytest
import pandas as pd
import sys
import os

# Add the python directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the functions we want to test
from step7_lowest_nps import analyze_lowest_nps, extract_nps_scores, format_feedback

class TestStep7Coverage:
    """Test class for step7_lowest_nps.py coverage"""
    
    def test_extract_nps_scores(self):
        """Test NPS score extraction"""
        # Test data
        test_data = {
            'On a scale from 0 to 10. How likely are you to recommend this program to a friend or colleague?': [
                'I would rate it 5 out of 10',
                'Score: 8',
                '10/10',
                '3',
                '9 out of 10'
            ],
            'TRACK': ['PROD', 'DEV', 'EXEC', 'PROD', 'DEV'],
            'What should we improve?': [
                'Better structure',
                'More hands-on',
                'Good program',
                'Need organization',
                'Excellent content'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result_df = extract_nps_scores(df)
        
        # Check that NPS_Score column was created
        assert 'NPS_Score' in result_df.columns
        
        # Check extracted scores
        expected_scores = [5.0, 8.0, 10.0, 3.0, 9.0]
        assert result_df['NPS_Score'].tolist() == expected_scores
        
        # Check data types
        assert result_df['NPS_Score'].dtype == 'float64'
    
    def test_analyze_lowest_nps(self):
        """Test lowest NPS analysis"""
        # Test data with known lowest scores
        test_data = {
            'NPS_Score': [10.0, 2.0, 8.0, 4.0, 6.0, 7.0],
            'TRACK': ['EXEC', 'PROD', 'DEV', 'PROD', 'DEV', 'EXEC'],
            'What should we improve?': [
                'Great program',
                'Too much unstructured time',
                'More hands-on needed',
                'Logistics issues',
                'Better organization',
                'Published schedule needed'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = analyze_lowest_nps(df, top_n=3)
        
        # Check that we get the 3 lowest scores
        assert len(result) == 3
        
        # Check that scores are in ascending order
        scores = [row['NPS_Score'] for row in result]
        assert scores == [2.0, 4.0, 6.0]
        
        # Check that feedback is preserved
        assert result[0]['feedback'] == 'Too much unstructured time'
        assert result[1]['feedback'] == 'Logistics issues'
        assert result[2]['feedback'] == 'Better organization'
    
    def test_format_feedback(self):
        """Test feedback formatting"""
        test_feedback = "This is a test feedback message"
        formatted = format_feedback(test_feedback)
        
        # Check that feedback is properly quoted
        assert formatted == f"'{test_feedback}'"
        
        # Test with empty feedback
        empty_formatted = format_feedback("")
        assert empty_formatted == "''"
        
        # Test with None feedback
        none_formatted = format_feedback(None)
        assert none_formatted == "'None'"
    
    def test_edge_cases(self):
        """Test edge cases for robustness"""
        # Test with empty dataframe
        empty_df = pd.DataFrame()
        result = analyze_lowest_nps(empty_df, top_n=5)
        assert result == []
        
        # Test with single row
        single_row_df = pd.DataFrame({
            'NPS_Score': [5.0],
            'TRACK': ['PROD'],
            'What should we improve?': ['Test feedback']
        })
        result = analyze_lowest_nps(single_row_df, top_n=3)
        assert len(result) == 1
        assert result[0]['NPS_Score'] == 5.0
        
        # Test with missing NPS scores
        missing_scores_df = pd.DataFrame({
            'NPS_Score': [None, 5.0, 8.0],
            'TRACK': ['PROD', 'DEV', 'EXEC'],
            'What should we improve?': ['Feedback 1', 'Feedback 2', 'Feedback 3']
        })
        result = analyze_lowest_nps(missing_scores_df, top_n=2)
        # Should handle None values gracefully
        assert len(result) == 2
    
    def test_nps_score_extraction_edge_cases(self):
        """Test NPS score extraction with edge cases"""
        # Test with various text formats
        test_cases = [
            ('I give it a 7', 7.0),
            ('Score: 10/10', 10.0),
            ('Rating: 3 out of 10', 3.0),
            ('5', 5.0),
            ('No score mentioned', None),
            ('', None),
            (None, None)
        ]
        
        for text, expected in test_cases:
            test_data = {
                'On a scale from 0 to 10. How likely are you to recommend this program to a friend or colleague?': [text],
                'TRACK': ['PROD'],
                'What should we improve?': ['Test']
            }
            df = pd.DataFrame(test_data)
            result_df = extract_nps_scores(df)
            
            if expected is None:
                assert pd.isna(result_df['NPS_Score'].iloc[0])
            else:
                assert result_df['NPS_Score'].iloc[0] == expected

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "--cov=step7_lowest_nps", "--cov-report=term-missing"])
