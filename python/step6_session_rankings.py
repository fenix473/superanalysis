"""Step 6: Session Rankings Analysis - Optimized for 90%+ utilization"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("csv/imported_data.csv")

# Define session columns
session_cols = {
    'favorite': 'What session did you enjoy the most?',
    'second_favorite': 'What is the second session you enjoyed the most?'
}

# Analyze session preferences by track
def analyze_session_rankings(df, session_cols):
    track_rankings = {}
    
    for track in df['TRACK'].unique():
        track_data = df[df['TRACK'] == track]
        
        # Count favorite sessions
        favorite_sessions = track_data[session_cols['favorite']].value_counts()
        second_favorite_sessions = track_data[session_cols['second_favorite']].value_counts()
        
        # Combine rankings (1 point for each session regardless of rank)
        combined_rankings = {}
        
        # Add favorite sessions (1 point each)
        for session, count in favorite_sessions.items():
            if pd.notna(session) and session.strip():
                combined_rankings[session] = count
        
        # Add second favorite sessions (1 point each)
        for session, count in second_favorite_sessions.items():
            if pd.notna(session) and session.strip():
                if session in combined_rankings:
                    combined_rankings[session] += count
                else:
                    combined_rankings[session] = count
        
        # Sort by points (descending)
        sorted_rankings = dict(sorted(combined_rankings.items(), 
                                     key=lambda x: x[1], reverse=True))
        
        track_rankings[track] = sorted_rankings
    
    return track_rankings

# Analyze rankings
session_rankings = analyze_session_rankings(df, session_cols)

# Create visualizations
fig, axes = plt.subplots(1, 3, figsize=(24, 10))
fig.suptitle('Session Rankings by Track (1 point per session regardless of rank)', 
             fontsize=20, fontweight='bold')

colors = ['#2E8B57', '#4682B4', '#CD853F']

for i, (track, rankings) in enumerate(session_rankings.items()):
    if rankings:
        # Get top 8 sessions for better visualization
        top_sessions = dict(list(rankings.items())[:8])
        
        # Shorten session names for better display
        shortened_names = []
        for session in top_sessions.keys():
            if 'Day' in session and 'Session' in session:
                # Extract day and session info
                parts = session.split(':')
                if len(parts) > 1:
                    day_session = parts[0].strip()
                    title = parts[1].strip()
                    if len(title) > 30:
                        title = title[:30] + '...'
                    shortened_names.append(f"{day_session}\n{title}")
                else:
                    shortened_names.append(session[:40] + '...' if len(session) > 40 else session)
            else:
                shortened_names.append(session[:40] + '...' if len(session) > 40 else session)
        
        # Create horizontal bar chart
        bars = axes[i].barh(range(len(top_sessions)), list(top_sessions.values()), 
                           color=colors[i], alpha=0.7)
        axes[i].set_yticks(range(len(top_sessions)))
        axes[i].set_yticklabels(shortened_names, fontsize=10)
        axes[i].set_xlabel('Points', fontweight='bold')
        axes[i].set_title(f'{track} Track', fontsize=16, fontweight='bold')
        
        # Add value labels on bars
        for j, (bar, value) in enumerate(zip(bars, top_sessions.values())):
            axes[i].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                        f'{value}', ha='left', va='center', fontweight='bold')
        
        axes[i].invert_yaxis()  # Top session at the top
    else:
        axes[i].text(0.5, 0.5, f'{track}\nNo session\npreferences', 
                    ha='center', va='center', fontsize=14, fontweight='bold')
        axes[i].axis('off')

plt.tight_layout()
plt.savefig('images/session_rankings.png', dpi=300, bbox_inches='tight')
plt.show()

# Display detailed results
print("Session Rankings by Track:")
print("=" * 60)

for track, rankings in session_rankings.items():
    print(f"\n{track} Track:")
    print("-" * 40)
    if rankings:
        for i, (session, points) in enumerate(rankings.items(), 1):
            print(f"{i:2d}. {session}")
            print(f"    Points: {points}")
            print()
    else:
        print("  No session preferences recorded")

# Create summary statistics
print("\nSummary Statistics:")
print("=" * 60)

for track, rankings in session_rankings.items():
    if rankings:
        total_points = sum(rankings.values())
        unique_sessions = len(rankings)
        top_session = list(rankings.keys())[0]
        top_points = rankings[top_session]
        
        print(f"\n{track} Track:")
        print(f"  Total Points: {total_points}")
        print(f"  Unique Sessions: {unique_sessions}")
        print(f"  Top Session: {top_session}")
        print(f"  Top Points: {top_points}")

# Save detailed results
track_results = []
for track, rankings in session_rankings.items():
    if rankings:
        for session, points in rankings.items():
            track_results.append({
                'Track': track,
                'Session': session,
                'Points': points,
                'Rank': list(rankings.keys()).index(session) + 1
            })
    else:
        track_results.append({
            'Track': track,
            'Session': 'None',
            'Points': 0,
            'Rank': 0
        })

pd.DataFrame(track_results).to_csv('csv/session_rankings.csv', index=False)

print("\nSession rankings saved as 'images/session_rankings.png'")
print("Detailed results saved as 'csv/session_rankings.csv'")
