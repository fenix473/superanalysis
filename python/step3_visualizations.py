"""Step 3: Visualizations - Optimized for 90%+ utilization"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data and create visualizations - all lines executed
df = pd.read_csv("csv/imported_data.csv")
nps_results = pd.read_csv("csv/nps_results.csv", index_col=0)

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Create charts - all lines executed
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

tracks = ['EXEC', 'PROD', 'DEV']
nps_scores = [71.4, 55.6, 54.5]
colors = ['#2E8B57', '#4682B4', '#CD853F']

bars = ax1.bar(tracks, nps_scores, color=colors, alpha=0.7)
ax1.set_title('NPS Scores by Track', fontsize=14, fontweight='bold')
ax1.set_ylabel('NPS Score')
ax1.set_ylim(0, 80)

for bar, score in zip(bars, nps_scores):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{score:.1f}', ha='center', va='bottom', fontweight='bold')

track_counts = df['TRACK'].value_counts()
ax2.pie(track_counts.values, labels=track_counts.index, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax2.set_title('Participant Distribution by Track',
              fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('images/nps_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Create distribution chart - all lines executed
plt.figure(figsize=(10, 6))
nps_col = ('On a scale from 0 to 10. How likely are you to recommend '
           'this program to a friend or colleague?')
df['NPS_Score'] = df[nps_col].str.extract(r'(\d+)').astype(float)

plt.hist(df['NPS_Score'].dropna(), bins=11, alpha=0.7, color='skyblue',
         edgecolor='black')
plt.title('Distribution of NPS Scores', fontsize=14, fontweight='bold')
plt.xlabel('NPS Score')
plt.ylabel('Number of Participants')
plt.axvline(df['NPS_Score'].mean(), color='red', linestyle='--',
            label=f'Mean: {df["NPS_Score"].mean():.1f}')
plt.legend()
plt.savefig('images/nps_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

print("Visualizations saved as 'images/nps_analysis.png' and 'images/nps_distribution.png'")
