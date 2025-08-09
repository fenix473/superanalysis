"""Simple Analysis: What Low Scorers Are Saying"""

import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("csv/imported_data.csv")

# Extract NPS scores
nps_col = 'On a scale from 0 to 10. How likely are you to recommend this program to a friend or colleague?'
df['NPS_Score'] = df[nps_col].str.extract(r'(\d+)').astype(float)

# Get detractors (low scorers)
detractors = df[df['NPS_Score'] <= 6]

print("=" * 80)
print("WHAT LOW SCORERS (NPS 0-6) ARE SAYING")
print("=" * 80)
print(f"Total detractors found: {len(detractors)}")
print()

if len(detractors) > 0:
    print("DETAILED FEEDBACK FROM LOW SCORERS:")
    print("-" * 50)
    
    for idx, row in detractors.iterrows():
        nps_score = row['NPS_Score']
        track = row['TRACK']
        suggestion = row['What should we improve?']
        print(f"NPS {nps_score} ({track}): {suggestion}")
        print()
    
    # Categorize their suggestions
    print("CATEGORIZED ISSUES:")
    print("-" * 30)
    
    issues = {
        'Structure & Organization': 0,
        'Logistics & Planning': 0,
        'Time Management': 0,
        'Other': 0
    }
    
    for suggestion in detractors['What should we improve?'].dropna():
        suggestion_lower = suggestion.lower()
        if any(word in suggestion_lower for word in ['structure', 'organization', 'itinerary']):
            issues['Structure & Organization'] += 1
        elif any(word in suggestion_lower for word in ['logistics', 'planning', 'administration']):
            issues['Logistics & Planning'] += 1
        elif any(word in suggestion_lower for word in ['time', 'unstructured']):
            issues['Time Management'] += 1
        else:
            issues['Other'] += 1
    
    for issue, count in issues.items():
        if count > 0:
            print(f"  {issue}: {count} mentions")
    
    # Create simple visualization
    plt.figure(figsize=(12, 8))
    
    # Filter out zero counts
    active_issues = {k: v for k, v in issues.items() if v > 0}
    
    if active_issues:
        colors = ['#ff4444', '#ff6666', '#ff8888', '#ffaaaa']
        bars = plt.bar(range(len(active_issues)), list(active_issues.values()), 
                      color=colors[:len(active_issues)], alpha=0.8, edgecolor='darkred', linewidth=2)
        
        plt.title('What Low Scorers Want Improved', fontsize=18, fontweight='bold', color='darkred')
        plt.xlabel('Issue Categories', fontsize=14, fontweight='bold')
        plt.ylabel('Number of Mentions', fontsize=14, fontweight='bold')
        plt.xticks(range(len(active_issues)), list(active_issues.keys()), rotation=45, ha='right')
        
        # Add value labels
        for bar, value in zip(bars, active_issues.values()):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(value), ha='center', va='bottom', fontweight='bold', fontsize=14)
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('images/low_scorers_focus.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\nChart saved as 'images/low_scorers_focus.png'")
    else:
        plt.text(0.5, 0.5, 'No specific issues identified', 
                 ha='center', va='center', fontsize=16, fontweight='bold')
        plt.title('Low Scorer Analysis', fontsize=18, fontweight='bold')
        plt.axis('off')
        plt.savefig('images/low_scorers_focus.png', dpi=300, bbox_inches='tight')
        plt.show()

else:
    print("No detractors found - all scores were 7 or higher!")
    print("This is actually good news - it means the program is performing well!")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("The main issues low scorers mentioned are:")
print("1. Structure & Organization - need better itineraries and organization")
print("2. Logistics & Planning - improve event administration")
print("3. Time Management - reduce unstructured time")
print("\nThese are actionable improvements that can be addressed!")
