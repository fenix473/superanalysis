"""Step 5: Track-Specific Improvement Analysis - Optimized for 90%+ utilization"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from collections import Counter

# Load data
df = pd.read_csv("csv/imported_data.csv")
improvement_col = 'What should we improve?'

# Define improvement categories based on actual feedback
improvement_categories = {
    'hands_on': ['hands on', 'hands-on', 'practical', 'demos', 'tutorials', 'exercises', 'projects', 'coding'],
    'structure': ['schedule', 'agenda', 'structure', 'organization', 'planning', 'logistics'],
    'content': ['content', 'basics', 'fundamentals', 'technical', 'insights', 'learning'],
    'communication': ['communication', 'emails', 'reminders', 'guidelines', 'instructions'],
    'logistics': ['room', 'food', 'wifi', 'outlets', 'setup', 'prep work', 'materials'],
    'interactive': ['interactive', 'discussions', 'team projects', 'workflows'],
    'time': ['time management', 'longer sessions', 'more time', 'unstructured time'],
    'track_specific': ['tracks', 'career path', 'developer', 'productivity', 'executive']
}

# Extract and categorize improvements by track
def categorize_improvements_by_track(df, improvement_col):
    track_improvements = {}
    
    for track in df['TRACK'].unique():
        track_data = df[df['TRACK'] == track]
        categorized = {category: [] for category in improvement_categories.keys()}
        
        for text in track_data[improvement_col].dropna():
            text_lower = str(text).lower()
            
            for category, keywords in improvement_categories.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        categorized[category].append(keyword)
        
        # Count improvements by category for this track
        category_counts = {}
        for category, keywords in categorized.items():
            if keywords:  # Only include categories with matches
                category_counts[category.replace('_', ' ').title()] = len(keywords)
        
        track_improvements[track] = category_counts
    
    return track_improvements

# Analyze improvements by track
track_improvements = categorize_improvements_by_track(df, improvement_col)

# Create visualizations for each track
fig, axes = plt.subplots(1, 3, figsize=(20, 8))
fig.suptitle('Improvement Areas by Track', fontsize=20, fontweight='bold')

for i, (track, improvements) in enumerate(track_improvements.items()):
    if improvements:  # Only create word cloud if there are improvements
        wordcloud = WordCloud(width=400, height=300, background_color='white',
                             max_words=8, colormap='viridis',
                             collocations=False).generate_from_frequencies(improvements)
        
        axes[i].imshow(wordcloud, interpolation='bilinear')
        axes[i].set_title(f'{track} Track', fontsize=16, fontweight='bold')
        axes[i].axis('off')
    else:
        axes[i].text(0.5, 0.5, f'{track}\nNo specific\nimprovements', 
                    ha='center', va='center', fontsize=14, fontweight='bold')
        axes[i].axis('off')

plt.tight_layout()
plt.savefig('images/track_improvements.png', dpi=300, bbox_inches='tight')
plt.show()

# Display results by track
print("Improvement Areas by Track:")
print("=" * 50)

for track, improvements in track_improvements.items():
    print(f"\n{track} Track:")
    if improvements:
        for category, count in sorted(improvements.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} mentions")
    else:
        print("  No specific improvement suggestions")

# Save detailed results
track_results = []
for track, improvements in track_improvements.items():
    if improvements:
        for category, count in improvements.items():
            track_results.append({'Track': track, 'Category': category, 'Mentions': count})
    else:
        track_results.append({'Track': track, 'Category': 'None', 'Mentions': 0})

pd.DataFrame(track_results).to_csv('csv/track_improvements.csv', index=False)

print("\nTrack improvements saved as 'images/track_improvements.png'")
print("Detailed results saved as 'csv/track_improvements.csv'")
