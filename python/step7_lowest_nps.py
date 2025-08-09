"""Step 7: Lowest NPS Scores and Their Exact Feedback"""

import pandas as pd

def extract_nps_scores(df):
    """Extract NPS scores from the NPS column"""
    nps_col = 'On a scale from 0 to 10. How likely are you to recommend this program to a friend or colleague?'
    df['NPS_Score'] = df[nps_col].str.extract(r'(\d+)').astype(float)
    return df

def analyze_lowest_nps(df, top_n=5):
    """Analyze the lowest NPS scores and return their details"""
    if df.empty:
        return []
    
    # Find lowest NPS scores
    lowest_nps = df.nsmallest(top_n, 'NPS_Score')
    
    results = []
    for idx, row in lowest_nps.iterrows():
        results.append({
            'NPS_Score': row['NPS_Score'],
            'track': row['TRACK'],
            'feedback': row['What should we improve?']
        })
    
    return results

def format_feedback(feedback):
    """Format feedback text with quotes"""
    return f"'{feedback}'"

def print_lowest_nps_analysis(df):
    """Print the lowest NPS analysis"""
    print("=" * 80)
    print("LOWEST NPS SCORES AND THEIR EXACT FEEDBACK")
    print("=" * 80)
    
    results = analyze_lowest_nps(df)
    
    for result in results:
        nps_score = result['NPS_Score']
        track = result['track']
        feedback = result['feedback']
        
        print(f"\nNPS {nps_score} ({track}):")
        print(format_feedback(feedback))
        print("-" * 60)
    
    print(f"\nTotal participants analyzed: {len(df)}")
    print(f"Lowest NPS score found: {df['NPS_Score'].min()}")
    print(f"Highest NPS score found: {df['NPS_Score'].max()}")

def main():
    """Main function to run the analysis"""
    # Load data
    df = pd.read_csv("csv/imported_data.csv")
    
    # Extract NPS scores
    df = extract_nps_scores(df)
    
    # Print analysis
    print_lowest_nps_analysis(df)

if __name__ == "__main__":
    main()
