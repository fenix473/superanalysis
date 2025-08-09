"""
Step 8: Track-Specific Feedback Analysis
Analyzes feedback by track (EXEC, PROD, DEV) focusing on:
- Keywords from top scorers (promoters)
- Most comprehensive reviews from low scorers (detractors)
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
import os


def extract_nps_scores(df):
    """Extract NPS scores from the NPS column"""
    nps_col = 'On a scale from 0 to 10. How likely are you to recommend this program to a friend or colleague?'
    df['NPS_Score'] = df[nps_col].str.extract(r'(\d+)').astype(float)
    return df


def categorize_nps(score):
    """Categorize NPS scores into promoters, passives, detractors"""
    if pd.isna(score):
        return 'Unknown'
    elif score >= 9:
        return 'Promoter'
    elif score >= 7:
        return 'Passive'
    else:
        return 'Detractor'


def extract_keywords(text, min_length=4):
    """Extract meaningful keywords and phrases from text"""
    if pd.isna(text) or text == '' or str(text) == 'nan':
        return []
    
    # Clean text
    text = str(text).lower()
    
    # Look for meaningful phrases first (2-3 words)
    phrases = re.findall(r'\b(?:ai|data|learning|hands.?on|practical|networking|conversations|speakers|framework|sessions?|insights?|experience|knowledge|tools?|technology|implementation|strategy|strategic|leadership|transformation|collaboration|workshop|discussions?)\b', text)
    
    # Also extract important single words
    stop_words = {'the', 'and', 'was', 'were', 'are', 'is', 'it', 'of', 'to', 'in', 'for', 'with', 'on', 'at', 'by', 'from', 'this', 'that', 'they', 'them', 'their', 'would', 'could', 'should', 'very', 'really', 'great', 'good', 'nice', 'well', 'also', 'more', 'most', 'all', 'some', 'any', 'had', 'have', 'has', 'been', 'being', 'will', 'can', 'may', 'might', 'much', 'many', 'but', 'not', 'only', 'just', 'about', 'than', 'into', 'over', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'again', 'further', 'then', 'once', 'program', 'course'}
    
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text)
    meaningful_words = [word for word in words if word not in stop_words]
    
    # Combine phrases and words
    all_keywords = phrases + meaningful_words
    return all_keywords


def analyze_track_feedback(df):
    """Analyze feedback by track, separating top and low scorers"""
    results = {}
    
    for track in ['EXEC', 'PROD', 'DEV']:
        track_data = df[df['TRACK'] == track].copy()
        track_data['NPS_Category'] = track_data['NPS_Score'].apply(categorize_nps)
        
        # Get promoters (top scorers)
        promoters = track_data[track_data['NPS_Category'] == 'Promoter']
        
        # Get detractors (low scorers)
        detractors = track_data[track_data['NPS_Category'] == 'Detractor']
        
        # Extract positive feedback keywords from promoters
        positive_keywords = []
        for _, row in promoters.iterrows():
            valuable_text = str(row.get('What was the most valuable part of the program?', ''))
            motivation_text = str(row.get('What motivated your choice?', ''))
            motivation_text2 = str(row.get('What motivated your choice?.1', ''))
            session_enjoyed = str(row.get('What session did you enjoy the most?', ''))
            session2_enjoyed = str(row.get('What is the second session you enjoyed the most?', ''))
            anything_else = str(row.get('Anything else you want to share with us?', ''))
            
            all_text = f"{valuable_text} {motivation_text} {motivation_text2} {session_enjoyed} {session2_enjoyed} {anything_else}"
            keywords = extract_keywords(all_text)
            positive_keywords.extend(keywords)
        
        # Get most comprehensive negative reviews from detractors
        comprehensive_reviews = []
        for _, row in detractors.iterrows():
            improve_text = str(row.get('What should we improve?', ''))
            if len(improve_text) > 50 and improve_text != 'nan':  # Filter for substantial feedback
                comprehensive_reviews.append({
                    'nps_score': row['NPS_Score'],
                    'feedback': improve_text,
                    'length': len(improve_text)
                })
        
        # Sort by length to get most comprehensive
        comprehensive_reviews.sort(key=lambda x: x['length'], reverse=True)
        
        results[track] = {
            'total_participants': len(track_data),
            'promoters_count': len(promoters),
            'detractors_count': len(detractors),
            'top_keywords': Counter(positive_keywords).most_common(10),
            'comprehensive_reviews': comprehensive_reviews[:3],  # Top 3 most comprehensive
            'avg_nps': track_data['NPS_Score'].mean()
        }
    
    return results


def print_track_analysis(results):
    """Print comprehensive track analysis"""
    print("=" * 80)
    print("TRACK-SPECIFIC FEEDBACK ANALYSIS")
    print("=" * 80)
    
    for track, data in results.items():
        print(f"\n{'='*20} {track} TRACK {'='*20}")
        print(f"Total Participants: {data['total_participants']}")
        print(f"Average NPS: {data['avg_nps']:.1f}")
        print(f"Promoters: {data['promoters_count']} | Detractors: {data['detractors_count']}")
        
        print(f"\n🔑 TOP KEYWORDS FROM PROMOTERS:")
        if data['top_keywords']:
            for keyword, count in data['top_keywords']:
                print(f"  • {keyword} ({count} mentions)")
        else:
            print("  No significant keywords found")
        
        print(f"\n📝 MOST COMPREHENSIVE NEGATIVE REVIEWS:")
        if data['comprehensive_reviews']:
            for i, review in enumerate(data['comprehensive_reviews'], 1):
                print(f"\n  {i}. NPS {review['nps_score']} ({review['length']} chars):")
                print(f"     \"{review['feedback']}\"")
        else:
            print("  No comprehensive negative reviews found")
        
        print("-" * 60)


def save_track_analysis(results):
    """Save analysis results to CSV"""
    os.makedirs("csv", exist_ok=True)
    
    # Create summary data
    summary_data = []
    keyword_data = []
    review_data = []
    
    for track, data in results.items():
        summary_data.append({
            'Track': track,
            'Total_Participants': data['total_participants'],
            'Promoters_Count': data['promoters_count'],
            'Detractors_Count': data['detractors_count'],
            'Average_NPS': round(data['avg_nps'], 1)
        })
        
        # Keywords data
        for keyword, count in data['top_keywords']:
            keyword_data.append({
                'Track': track,
                'Keyword': keyword,
                'Mentions': count
            })
        
        # Reviews data
        for i, review in enumerate(data['comprehensive_reviews'], 1):
            review_data.append({
                'Track': track,
                'Rank': i,
                'NPS_Score': review['nps_score'],
                'Feedback_Length': review['length'],
                'Feedback': review['feedback']
            })
    
    # Save to CSV files
    pd.DataFrame(summary_data).to_csv("csv/track_summary.csv", index=False)
    pd.DataFrame(keyword_data).to_csv("csv/track_keywords.csv", index=False)
    pd.DataFrame(review_data).to_csv("csv/track_reviews.csv", index=False)
    
    print(f"\nAnalysis saved to:")
    print(f"  • csv/track_summary.csv")
    print(f"  • csv/track_keywords.csv") 
    print(f"  • csv/track_reviews.csv")


def main():
    """Main function to run track analysis"""
    try:
        df = pd.read_csv("csv/imported_data.csv")
        df = extract_nps_scores(df)
        
        results = analyze_track_feedback(df)
        print_track_analysis(results)
        save_track_analysis(results)
        
        return results
        
    except FileNotFoundError:
        print("Error: csv/imported_data.csv not found. Please run step1 first.")
        return None
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None


if __name__ == "__main__":
    main()
