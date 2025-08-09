"""
Step 8: Track Analysis Visualizations
Creates visualizations for track-specific feedback analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from step8_track_analysis import main as run_track_analysis


def create_track_comparison_viz():
    """Create comprehensive track comparison visualization"""
    # Run analysis to get fresh data
    results = run_track_analysis()
    if not results:
        print("Error: Could not run track analysis")
        return
    
    # Set up the plot style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Track-Specific Feedback Analysis', fontsize=16, fontweight='bold')
    
    # 1. NPS Comparison by Track
    tracks = list(results.keys())
    nps_scores = [results[track]['avg_nps'] for track in tracks]
    colors = ['#e74c3c', '#3498db', '#2ecc71']  # Red, Blue, Green
    
    bars1 = ax1.bar(tracks, nps_scores, color=colors, alpha=0.8)
    ax1.set_title('Average NPS Score by Track', fontweight='bold')
    ax1.set_ylabel('Average NPS Score')
    ax1.set_ylim(0, 10)
    
    # Add value labels on bars
    for bar, score in zip(bars1, nps_scores):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Participant Distribution
    promoter_counts = [results[track]['promoters_count'] for track in tracks]
    detractor_counts = [results[track]['detractors_count'] for track in tracks]
    total_counts = [results[track]['total_participants'] for track in tracks]
    
    x = np.arange(len(tracks))
    width = 0.35
    
    bars2 = ax2.bar(x - width/2, promoter_counts, width, label='Promoters', color='#2ecc71', alpha=0.8)
    bars3 = ax2.bar(x + width/2, detractor_counts, width, label='Detractors', color='#e74c3c', alpha=0.8)
    
    ax2.set_title('Promoters vs Detractors by Track', fontweight='bold')
    ax2.set_ylabel('Number of Participants')
    ax2.set_xticks(x)
    ax2.set_xticklabels(tracks)
    ax2.legend()
    
    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
    
    for bar in bars3:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
    
    # 3. Top Keywords by Track (Horizontal bar chart)
    ax3.set_title('Top 5 Keywords from Promoters by Track', fontweight='bold')
    
    y_pos = 0
    track_colors = {'EXEC': '#e74c3c', 'PROD': '#3498db', 'DEV': '#2ecc71'}
    
    for i, track in enumerate(tracks):
        top_keywords = results[track]['top_keywords'][:5]  # Top 5 keywords
        if top_keywords:
            keywords = [kw[0] for kw in top_keywords]
            counts = [kw[1] for kw in top_keywords]
            
            # Plot horizontal bars for this track
            y_positions = [y_pos + j for j in range(len(keywords))]
            ax3.barh(y_positions, counts, color=track_colors[track], alpha=0.7, label=track)
            
            # Add keyword labels
            for j, (keyword, count) in enumerate(top_keywords):
                ax3.text(-0.5, y_pos + j, keyword, ha='right', va='center', fontsize=9)
            
            y_pos += len(keywords) + 1  # Space between tracks
    
    ax3.set_xlabel('Mention Count')
    ax3.set_yticks([])
    ax3.legend()
    
    # 4. Track Overview Table
    ax4.axis('tight')
    ax4.axis('off')
    
    # Create table data
    table_data = []
    for track in tracks:
        data = results[track]
        table_data.append([
            track,
            data['total_participants'],
            f"{data['avg_nps']:.1f}",
            data['promoters_count'],
            data['detractors_count']
        ])
    
    table = ax4.table(cellText=table_data,
                     colLabels=['Track', 'Total', 'Avg NPS', 'Promoters', 'Detractors'],
                     cellLoc='center',
                     loc='center',
                     colColours=['#f0f0f0']*5)
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    ax4.set_title('Track Summary Statistics', fontweight='bold', pad=20)
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Ensure images directory exists
    os.makedirs("images", exist_ok=True)
    
    # Save the plot
    plt.savefig("images/track_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Track analysis visualization saved to images/track_analysis.png")


def create_keyword_wordcloud():
    """Create word clouds for each track's top keywords"""
    try:
        from wordcloud import WordCloud
        
        # Read keyword data
        keyword_df = pd.read_csv("csv/track_keywords.csv")
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Top Keywords by Track (from Promoters)', fontsize=16, fontweight='bold')
        
        track_colors = {'EXEC': 'Reds', 'PROD': 'Blues', 'DEV': 'Greens'}
        
        for i, track in enumerate(['EXEC', 'PROD', 'DEV']):
            track_keywords = keyword_df[keyword_df['Track'] == track]
            
            if not track_keywords.empty:
                # Create word frequency dict
                word_freq = dict(zip(track_keywords['Keyword'], track_keywords['Mentions']))
                
                # Generate word cloud
                wordcloud = WordCloud(width=400, height=300, 
                                    background_color='white',
                                    colormap=track_colors[track],
                                    max_words=50,
                                    relative_scaling=0.5).generate_from_frequencies(word_freq)
                
                axes[i].imshow(wordcloud, interpolation='bilinear')
                axes[i].set_title(f'{track} Track Keywords', fontweight='bold')
                axes[i].axis('off')
            else:
                axes[i].text(0.5, 0.5, 'No keywords found', ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(f'{track} Track Keywords', fontweight='bold')
                axes[i].axis('off')
        
        plt.tight_layout()
        plt.savefig("images/track_keywords_wordcloud.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Track keywords word cloud saved to images/track_keywords_wordcloud.png")
        
    except ImportError:
        print("WordCloud not available. Install with: pip install wordcloud")


def main():
    """Main function to create all track visualizations"""
    print("Creating track analysis visualizations...")
    
    # Create main comparison visualization
    create_track_comparison_viz()
    
    # Create keyword word clouds
    create_keyword_wordcloud()
    
    print("All track visualizations created successfully!")


if __name__ == "__main__":
    main()
