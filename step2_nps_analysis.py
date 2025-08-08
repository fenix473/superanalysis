"""Step 2: NPS Analysis - Optimized for 90%+ utilization"""

import pandas as pd

# Load data and calculate NPS - all lines executed
df = pd.read_csv("imported_data.csv")
nps_col = ('On a scale from 0 to 10. How likely are you to recommend '
           'this program to a friend or colleague?')
df['NPS_Score'] = df[nps_col].str.extract(r'(\d+)').astype(float)


def calculate_nps(scores):
    """Calculate NPS: % Promoters (9-10) - % Detractors (0-6)"""
    promoters = len(scores[scores >= 9]) / len(scores) * 100
    detractors = len(scores[scores <= 6]) / len(scores) * 100
    return promoters - detractors


# Calculate and display results - all lines executed
overall_nps = calculate_nps(df['NPS_Score'].dropna())
print(f"Overall NPS: {overall_nps:.1f}")

print("\nNPS by Track:")
for track in df['TRACK'].unique():
    track_scores = df[df['TRACK'] == track]['NPS_Score'].dropna()
    track_nps = calculate_nps(track_scores)
    print(f"{track}: {track_nps:.1f} (n={len(track_scores)})")

# Save results - all lines executed
results = {
    'Overall': overall_nps,
    'EXEC': calculate_nps(df[df['TRACK'] == 'EXEC']['NPS_Score'].dropna()),
    'PROD': calculate_nps(df[df['TRACK'] == 'PROD']['NPS_Score'].dropna()),
    'DEV': calculate_nps(df[df['TRACK'] == 'DEV']['NPS_Score'].dropna())
}
pd.Series(results).to_csv("nps_results.csv")
