"""Step 4: Word Cloud Analysis - Optimized for 90%+ utilization"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from collections import Counter

# Load data and extract improvement suggestions
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

# Extract and categorize improvements
def categorize_improvements(text_series):
    categorized = {category: [] for category in improvement_categories.keys()}
    
    for text in text_series.dropna():
        text_lower = str(text).lower()
        
        for category, keywords in improvement_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    categorized[category].append(keyword)
    
    return categorized

# Categorize improvements
categorized = categorize_improvements(df[improvement_col])

# Count improvements by category
category_counts = {}
for category, keywords in categorized.items():
    if keywords:  # Only include categories with matches
        category_counts[category.replace('_', ' ').title()] = len(keywords)

# Generate word cloud
wordcloud = WordCloud(width=800, height=600, background_color='white',
                     max_words=10, colormap='viridis',
                     collocations=False).generate_from_frequencies(category_counts)

# Create visualization
plt.figure(figsize=(12, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Improvement Areas by Category', fontsize=18, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('images/improvement_wordcloud.png', dpi=300, bbox_inches='tight')
plt.show()

# Display categorized improvements
print("Improvement Areas by Category:")
for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{category}: {count} mentions")

# Save categorized improvements
pd.DataFrame(sorted(category_counts.items(), key=lambda x: x[1], reverse=True), 
             columns=['Category', 'Mentions']).to_csv('csv/improvement_categories.csv', index=False)

print("\nWord cloud saved as 'images/improvement_wordcloud.png'")
print("Improvement categories saved as 'csv/improvement_categories.csv'")
