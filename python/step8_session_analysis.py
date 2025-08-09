"""
Step 8: Session-Specific Feedback Analysis
Analyzes feedback by individual sessions focusing on:
- Keywords from top scorers who enjoyed specific sessions
- Most comprehensive reviews from low scorers about sessions they didn't like
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
    
    # Look for meaningful phrases and words
    phrases = re.findall(r'\b(?:hands.?on|end.?to.?end|real.?world|practical|interactive|engaging|informative|valuable|insightful|comprehensive|detailed|clear|useful|relevant|applicable|actionable|concrete|specific|technical|business|strategic|creative|collaborative|networking|learning|experience|knowledge|insights|framework|tools?|technology|ai|data|llm|development|coding|application|discussion|workshop|presentation|project|showcase|creativity|marketing|privacy|security|governance|strategy|implementation|transformation)\b', text)
    
    # Also extract important single words
    stop_words = {'the', 'and', 'was', 'were', 'are', 'is', 'it', 'of', 'to', 'in', 'for', 'with', 'on', 'at', 'by', 'from', 'this', 'that', 'they', 'them', 'their', 'would', 'could', 'should', 'very', 'really', 'great', 'good', 'nice', 'well', 'also', 'more', 'most', 'all', 'some', 'any', 'had', 'have', 'has', 'been', 'being', 'will', 'can', 'may', 'might', 'much', 'many', 'but', 'not', 'only', 'just', 'about', 'than', 'into', 'over', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'again', 'further', 'then', 'once', 'program', 'course', 'session', 'sessions', 'day'}
    
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text)
    meaningful_words = [word for word in words if word not in stop_words]
    
    # Combine phrases and words
    all_keywords = phrases + meaningful_words
    return all_keywords


def clean_session_name(session_name):
    """Clean and standardize session names"""
    if pd.isna(session_name):
        return "Unknown Session"
    
    session = str(session_name).strip()
    # Remove extra whitespace
    session = re.sub(r'\s+', ' ', session)
    return session


def analyze_session_feedback(df):
    """Analyze feedback by individual sessions"""
    df['NPS_Category'] = df['NPS_Score'].apply(categorize_nps)
    
    # Get all sessions mentioned
    session_columns = ['What session did you enjoy the most?', 'What is the second session you enjoyed the most?']
    
    session_feedback = {}
    
    # Analyze top-rated sessions
    for col in session_columns:
        session_data = df[df[col].notna()][['TRACK', 'NPS_Score', 'NPS_Category', col, 'What motivated your choice?', 'What motivated your choice?.1']].copy()
        
        for _, row in session_data.iterrows():
            session_name = clean_session_name(row[col])
            
            if session_name not in session_feedback:
                session_feedback[session_name] = {
                    'total_mentions': 0,
                    'promoter_mentions': 0,
                    'detractor_mentions': 0,
                    'promoter_keywords': [],
                    'avg_nps_of_fans': [],
                    'tracks_represented': [],
                    'motivations': []
                }
            
            session_feedback[session_name]['total_mentions'] += 1
            session_feedback[session_name]['avg_nps_of_fans'].append(row['NPS_Score'])
            session_feedback[session_name]['tracks_represented'].append(row['TRACK'])
            
            if row['NPS_Category'] == 'Promoter':
                session_feedback[session_name]['promoter_mentions'] += 1
                
                # Extract keywords from motivation
                motivation_col = 'What motivated your choice?' if col == session_columns[0] else 'What motivated your choice?.1'
                motivation = str(row[motivation_col])
                keywords = extract_keywords(motivation)
                session_feedback[session_name]['promoter_keywords'].extend(keywords)
                session_feedback[session_name]['motivations'].append(motivation)
            
            elif row['NPS_Category'] == 'Detractor':
                session_feedback[session_name]['detractor_mentions'] += 1
    
    # Calculate averages and most common elements
    for session, data in session_feedback.items():
        if data['avg_nps_of_fans']:
            data['avg_nps_of_fans'] = np.mean(data['avg_nps_of_fans'])
        else:
            data['avg_nps_of_fans'] = 0
            
        data['top_keywords'] = Counter(data['promoter_keywords']).most_common(5)
        data['track_distribution'] = Counter(data['tracks_represented'])
    
    return session_feedback


def get_low_scorer_session_feedback(df):
    """Get comprehensive feedback from low scorers about what they didn't like"""
    detractors = df[df['NPS_Score'] <= 6].copy()
    
    comprehensive_negative_feedback = []
    
    for _, row in detractors.iterrows():
        improve_text = str(row.get('What should we improve?', ''))
        valuable_text = str(row.get('What was the most valuable part of the program?', ''))
        anything_else = str(row.get('Anything else you want to share with us?', ''))
        
        # Combine all feedback
        all_feedback = f"{improve_text} {valuable_text} {anything_else}"
        
        if len(improve_text) > 30 and improve_text != 'nan':  # Focus on substantial improvement feedback
            comprehensive_negative_feedback.append({
                'nps_score': row['NPS_Score'],
                'track': row['TRACK'],
                'improvement_feedback': improve_text,
                'valuable_feedback': valuable_text,
                'additional_feedback': anything_else,
                'total_length': len(all_feedback)
            })
    
    # Sort by feedback length (most comprehensive first)
    comprehensive_negative_feedback.sort(key=lambda x: x['total_length'], reverse=True)
    
    return comprehensive_negative_feedback


def print_session_analysis(session_feedback, negative_feedback):
    """Print comprehensive session analysis"""
    print("=" * 80)
    print("SESSION-SPECIFIC FEEDBACK ANALYSIS")
    print("=" * 80)
    
    # Sort sessions by total mentions
    sorted_sessions = sorted(session_feedback.items(), key=lambda x: x[1]['total_mentions'], reverse=True)
    
    print(f"\n🏆 TOP 10 MOST POPULAR SESSIONS:")
    print("-" * 60)
    
    for i, (session, data) in enumerate(sorted_sessions[:10], 1):
        print(f"\n{i}. {session}")
        print(f"   Total mentions: {data['total_mentions']}")
        print(f"   Avg NPS of fans: {data['avg_nps_of_fans']:.1f}")
        print(f"   Promoter mentions: {data['promoter_mentions']}")
        print(f"   Tracks: {dict(data['track_distribution'])}")
        
        if data['top_keywords']:
            keywords_str = ", ".join([f"{kw[0]} ({kw[1]})" for kw in data['top_keywords']])
            print(f"   🔑 Keywords: {keywords_str}")
        
        # Show a sample motivation
        if data['motivations']:
            sample_motivation = [m for m in data['motivations'] if len(m) > 10 and m != 'nan']
            if sample_motivation:
                print(f"   💬 Sample: \"{sample_motivation[0][:100]}...\"")
    
    print(f"\n\n📝 COMPREHENSIVE NEGATIVE FEEDBACK FROM LOW SCORERS:")
    print("-" * 60)
    
    for i, feedback in enumerate(negative_feedback[:5], 1):
        print(f"\n{i}. NPS {feedback['nps_score']} ({feedback['track']} Track):")
        print(f"   What should we improve:")
        print(f"   \"{feedback['improvement_feedback']}\"")
        
        if len(feedback['valuable_feedback']) > 10 and feedback['valuable_feedback'] != 'nan':
            print(f"   What was valuable:")
            print(f"   \"{feedback['valuable_feedback']}\"")


def save_session_analysis(session_feedback, negative_feedback):
    """Save analysis results to CSV files"""
    os.makedirs("csv", exist_ok=True)
    
    # Session popularity data
    session_data = []
    session_keywords = []
    
    for session, data in session_feedback.items():
        session_data.append({
            'Session': session,
            'Total_Mentions': data['total_mentions'],
            'Promoter_Mentions': data['promoter_mentions'],
            'Detractor_Mentions': data['detractor_mentions'],
            'Avg_NPS_of_Fans': round(data['avg_nps_of_fans'], 1),
            'Track_Distribution': str(dict(data['track_distribution']))
        })
        
        # Keywords for each session
        for keyword, count in data['top_keywords']:
            session_keywords.append({
                'Session': session,
                'Keyword': keyword,
                'Mentions': count
            })
    
    # Negative feedback data
    negative_data = []
    for feedback in negative_feedback:
        negative_data.append({
            'NPS_Score': feedback['nps_score'],
            'Track': feedback['track'],
            'Improvement_Feedback': feedback['improvement_feedback'],
            'Valuable_Feedback': feedback['valuable_feedback'],
            'Additional_Feedback': feedback['additional_feedback'],
            'Total_Length': feedback['total_length']
        })
    
    # Save to CSV files
    pd.DataFrame(session_data).to_csv("csv/session_popularity.csv", index=False)
    pd.DataFrame(session_keywords).to_csv("csv/session_keywords.csv", index=False)
    pd.DataFrame(negative_data).to_csv("csv/comprehensive_negative_feedback.csv", index=False)
    
    print(f"\nSession analysis saved to:")
    print(f"  • csv/session_popularity.csv")
    print(f"  • csv/session_keywords.csv")
    print(f"  • csv/comprehensive_negative_feedback.csv")


def main():
    """Main function to run session analysis"""
    try:
        df = pd.read_csv("csv/imported_data.csv")
        df = extract_nps_scores(df)
        
        session_feedback = analyze_session_feedback(df)
        negative_feedback = get_low_scorer_session_feedback(df)
        
        print_session_analysis(session_feedback, negative_feedback)
        save_session_analysis(session_feedback, negative_feedback)
        
        return session_feedback, negative_feedback
        
    except FileNotFoundError:
        print("Error: csv/imported_data.csv not found. Please run step1 first.")
        return None, None
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None, None


if __name__ == "__main__":
    main()
