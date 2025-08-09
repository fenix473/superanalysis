"""
Step 8 Visualizations: Enhanced Session Analysis Charts
Creates visualizations for the enhanced session analysis including:
- Session popularity by track
- Top sessions with motivation insights
- Track-specific session preferences
- Keyword analysis visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import os

# Set style
plt.style.use('default')
sns.set_palette("husl")

def create_session_popularity_chart():
    """Create a chart showing session popularity by track"""
    try:
        # Read session analysis data
        session_data = pd.read_csv("csv/session_analysis.csv")
        
                        # Extract track information from the breakdown
                track_data = []
                for _, row in session_data.iterrows():
                    session = row['Session']
                    mentions = row['Total_Mentions']
                    nps_score = row['NPS_Score']
                    
                    # Parse track breakdown (simplified approach)
                    if 'EXEC' in str(row['Track_Breakdown']):
                        track_data.append({'Session': session, 'Track': 'EXEC', 'Mentions': mentions, 'NPS_Score': nps_score})
                    if 'PROD' in str(row['Track_Breakdown']):
                        track_data.append({'Session': session, 'Track': 'PROD', 'Mentions': mentions, 'NPS_Score': nps_score})
                    if 'DEV' in str(row['Track_Breakdown']):
                        track_data.append({'Session': session, 'Track': 'DEV', 'Mentions': mentions, 'NPS_Score': nps_score})
        
        track_df = pd.DataFrame(track_data)
        
        # Get top 10 sessions by mentions
        top_sessions = track_df.groupby('Session')['Mentions'].sum().sort_values(ascending=False).head(10)
        
        # Create the visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Chart 1: Top sessions by mentions
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                 '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
        bars1 = ax1.barh(range(len(top_sessions)), top_sessions.values, color=colors)
        ax1.set_yticks(range(len(top_sessions)))
        ax1.set_yticklabels([session[:50] + '...' if len(session) > 50 else session 
                            for session in top_sessions.index], fontsize=10)
        ax1.set_xlabel('Number of Mentions', fontsize=12, fontweight='bold')
        ax1.set_title('Top 10 Most Popular Sessions by Total Mentions', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        # Chart 2: Track breakdown for top sessions
        track_colors = {'EXEC': '#FF6B6B', 'PROD': '#4ECDC4', 'DEV': '#45B7D1'}
        
        # Get track breakdown for top sessions
        top_session_names = top_sessions.index
        track_breakdown_data = []
        
        for session in top_session_names:
            session_tracks = track_df[track_df['Session'] == session]
            for _, row in session_tracks.iterrows():
                track_breakdown_data.append({
                    'Session': session[:30] + '...' if len(session) > 30 else session,
                    'Track': row['Track'],
                    'Mentions': row['Mentions']
                })
        
        track_breakdown_df = pd.DataFrame(track_breakdown_data)
        
        if not track_breakdown_df.empty:
            # Create stacked bar chart
            pivot_data = track_breakdown_df.pivot(index='Session', columns='Track', values='Mentions').fillna(0)
            
            pivot_data.plot(kind='barh', stacked=True, ax=ax2, color=[track_colors.get(col, '#999999') for col in pivot_data.columns])
            ax2.set_xlabel('Number of Mentions', fontsize=12, fontweight='bold')
            ax2.set_title('Track Breakdown for Top Sessions', fontsize=14, fontweight='bold')
            ax2.legend(title='Track', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('images/enhanced_session_popularity.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Session popularity chart created: images/enhanced_session_popularity.png")
        
    except Exception as e:
        print(f"❌ Error creating session popularity chart: {e}")


def create_motivation_analysis_chart():
    """Create a chart showing motivation analysis for top sessions"""
    try:
        # Read session reviews data
        reviews_data = pd.read_csv("csv/session_reviews.csv")
        
        # Get sessions with 3+ reviews (comprehensive analysis)
        session_counts = reviews_data['Session'].value_counts()
        comprehensive_sessions = session_counts[session_counts >= 3].index
        
        if len(comprehensive_sessions) == 0:
            print("⚠️ No sessions with 3+ reviews found for comprehensive analysis")
            return
        
        # Filter for comprehensive sessions
        comprehensive_reviews = reviews_data[reviews_data['Session'].isin(comprehensive_sessions)]
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Chart 1: Review length analysis
        session_avg_lengths = comprehensive_reviews.groupby('Session')['Length'].mean().sort_values(ascending=False)
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(session_avg_lengths)))
        bars1 = ax1.barh(range(len(session_avg_lengths)), session_avg_lengths.values, color=colors)
        
        ax1.set_yticks(range(len(session_avg_lengths)))
        ax1.set_yticklabels([session[:40] + '...' if len(session) > 40 else session 
                            for session in session_avg_lengths.index], fontsize=10)
        ax1.set_xlabel('Average Review Length (characters)', fontsize=12, fontweight='bold')
        ax1.set_title('Average Motivation Review Length by Session (3+ reviews)', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 2, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        # Chart 2: Top motivation keywords
        # Read keywords data
        keywords_data = pd.read_csv("csv/session_keywords_enhanced.csv")
        
        if not keywords_data.empty:
            # Get top keywords across all sessions
            top_keywords = keywords_data.groupby('Keyword')['Mentions'].sum().sort_values(ascending=False).head(10)
            
            colors2 = plt.cm.Set3(np.linspace(0, 1, len(top_keywords)))
            bars2 = ax2.barh(range(len(top_keywords)), top_keywords.values, color=colors2)
            
            ax2.set_yticks(range(len(top_keywords)))
            ax2.set_yticklabels(top_keywords.index, fontsize=11)
            ax2.set_xlabel('Total Mentions', fontsize=12, fontweight='bold')
            ax2.set_title('Top Keywords from Session Motivations', fontsize=14, fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for i, bar in enumerate(bars2):
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                        f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('images/enhanced_motivation_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Motivation analysis chart created: images/enhanced_motivation_analysis.png")
        
    except Exception as e:
        print(f"❌ Error creating motivation analysis chart: {e}")


def create_track_comparison_chart():
    """Create a chart comparing tracks with session preferences"""
    try:
        # Read track analysis data
        track_data = pd.read_csv("csv/track_analysis_enhanced.csv")
        
        # Read track keywords
        track_keywords = pd.read_csv("csv/track_keywords.csv")
        
        # Create visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
                        # Chart 1: Track NPS comparison
                tracks = track_data['Track']
                nps_scores = track_data['NPS_Score']
                participants = track_data['Total_Participants']
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        bars1 = ax1.bar(tracks, nps_scores, color=colors, alpha=0.8)
        ax1.set_ylabel('Average NPS Score', fontsize=12, fontweight='bold')
        ax1.set_title('Track Performance Comparison', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, score in zip(bars1, nps_scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: Participant distribution
        ax2.pie(participants, labels=tracks, autopct='%1.1f%%', startangle=90, colors=colors)
        ax2.set_title('Participant Distribution by Track', fontsize=14, fontweight='bold')
        
        # Chart 3: Top keywords by track
        if not track_keywords.empty:
            # Get top 5 keywords for each track
            top_keywords_by_track = {}
            for track in tracks:
                track_kw = track_keywords[track_keywords['Track'] == track].nlargest(5, 'Mentions')
                top_keywords_by_track[track] = track_kw
            
            # Create horizontal bar chart for keywords
            y_pos = 0
            for track in tracks:
                if track in top_keywords_by_track and not top_keywords_by_track[track].empty:
                    keywords = top_keywords_by_track[track]['Keyword'].tolist()
                    mentions = top_keywords_by_track[track]['Mentions'].tolist()
                    
                    x_pos = np.arange(len(keywords))
                    bars = ax3.barh(y_pos + x_pos, mentions, color=colors[tracks.tolist().index(track)], alpha=0.7)
                    ax3.set_yticks(y_pos + x_pos)
                    ax3.set_yticklabels([f"{track}: {kw}" for kw in keywords], fontsize=9)
                    
                    # Add value labels
                    for bar, mention in zip(bars, mentions):
                        width = bar.get_width()
                        ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                                f'{mention}', ha='left', va='center', fontsize=8)
                    
                    y_pos += len(keywords) + 1
            
            ax3.set_xlabel('Mentions', fontsize=12, fontweight='bold')
            ax3.set_title('Top Keywords by Track', fontsize=14, fontweight='bold')
            ax3.grid(axis='x', alpha=0.3)
        
        # Chart 4: Session preferences heatmap
        # Create a simple heatmap showing session popularity by track
        session_data = pd.read_csv("csv/session_analysis.csv")
        
        # Extract track information for heatmap
        heatmap_data = []
        for _, row in session_data.iterrows():
            session = row['Session']
            mentions = row['Total_Mentions']
            
            # Parse track from breakdown (simplified)
            if 'EXEC' in str(row['Track_Breakdown']):
                heatmap_data.append({'Session': session[:30], 'Track': 'EXEC', 'Mentions': mentions})
            if 'PROD' in str(row['Track_Breakdown']):
                heatmap_data.append({'Session': session[:30], 'Track': 'PROD', 'Mentions': mentions})
            if 'DEV' in str(row['Track_Breakdown']):
                heatmap_data.append({'Session': session[:30], 'Track': 'DEV', 'Mentions': mentions})
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            heatmap_pivot = heatmap_df.pivot(index='Session', columns='Track', values='Mentions').fillna(0)
            
            # Get top 8 sessions for heatmap
            top_sessions_heatmap = heatmap_pivot.sum(axis=1).sort_values(ascending=False).head(8).index
            heatmap_pivot_top = heatmap_pivot.loc[top_sessions_heatmap]
            
            sns.heatmap(heatmap_pivot_top, annot=True, fmt='g', cmap='YlOrRd', ax=ax4, cbar_kws={'label': 'Mentions'})
            ax4.set_title('Session Popularity by Track (Top 8 Sessions)', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Track', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Session', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('images/enhanced_track_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Track comparison chart created: images/enhanced_track_comparison.png")
        
    except Exception as e:
        print(f"❌ Error creating track comparison chart: {e}")


def main():
    """Main function to create all visualizations"""
    print("🎨 Creating Enhanced Step 8 Visualizations...")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("images", exist_ok=True)
    
    # Create all charts
    create_session_popularity_chart()
    create_motivation_analysis_chart()
    create_track_comparison_chart()
    
    print("\n✅ All enhanced step 8 visualizations completed!")
    print("📊 Generated charts:")
    print("  • images/enhanced_session_popularity.png")
    print("  • images/enhanced_motivation_analysis.png")
    print("  • images/enhanced_track_comparison.png")


if __name__ == "__main__":
    main()
