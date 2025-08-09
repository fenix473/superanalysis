"""
Step 8: Track-Specific Feedback Analysis
Analyzes feedback by track (EXEC, PROD, DEV) focusing on:
- Keywords from top scorers (promoters)
- Most comprehensive reviews from low scorers (detractors)
- All sessions grouped by track with keywords or best comments
"""

import pandas as pd
from collections import Counter
import re
import os


def extract_nps_scores(df):
    """Extract NPS scores from the NPS column"""
    nps_col = ('On a scale from 0 to 10. How likely are you to recommend '
               'this program to a friend or colleague?')
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
    phrases = re.findall(
        r'\b(?:ai|data|learning|hands.?on|practical|networking|'
        r'conversations|speakers|framework|sessions?|insights?|'
        r'experience|knowledge|tools?|technology|implementation|'
        r'strategy|strategic|leadership|transformation|collaboration|'
        r'workshop|discussions?)\b', text)

    # Also extract important single words
    stop_words = {
        'the', 'and', 'was', 'were', 'are', 'is', 'it', 'of', 'to', 'in',
        'for', 'with', 'on', 'at', 'by', 'from', 'this', 'that', 'they',
        'them', 'their', 'would', 'could', 'should', 'very', 'really',
        'great', 'good', 'nice', 'well', 'also', 'more', 'most', 'all',
        'some', 'any', 'had', 'have', 'has', 'been', 'being', 'will',
        'can', 'may', 'might', 'much', 'many', 'but', 'not', 'only',
        'just', 'about', 'than', 'into', 'over', 'through', 'during',
        'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off',
        'again', 'further', 'then', 'once', 'program', 'course'
    }

    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text)
    meaningful_words = [word for word in words if word not in stop_words]

    # Combine phrases and words
    all_keywords = phrases + meaningful_words
    return all_keywords


def analyze_all_sessions_by_track(df):
    """Analyze all sessions grouped by track with keywords or best comments"""
    results = {}

    for track in ['EXEC', 'PROD', 'DEV']:
        track_data = df[df['TRACK'] == track].copy()
        track_data['NPS_Category'] = track_data['NPS_Score'].apply(categorize_nps)

        # Get session columns
        session_cols = ['What session did you enjoy the most?',
                        'What is the second session you enjoyed the most?']

        track_sessions = {}

        for session_col in session_cols:
            # Get unique session names for this track
            session_responses = track_data[session_col].dropna()
            session_responses = session_responses[session_responses != '']
            session_responses = session_responses[session_responses != 'nan']

            if len(session_responses) == 0:
                continue

            # Group by actual session names
            for session_name in session_responses.unique():
                if pd.isna(session_name) or session_name == '' or session_name == 'nan':
                    continue

                # Get participants who enjoyed this specific session
                session_participants = track_data[track_data[session_col] == session_name]

                if len(session_participants) == 0:
                    continue

                # Get feedback from these participants
                session_feedback = []
                for _, row in session_participants.iterrows():
                    # Get motivation for choosing this session
                    if session_col == 'What session did you enjoy the most?':
                        motivation_col = 'What motivated your choice?'
                    else:
                        motivation_col = 'What motivated your choice?.1'
                    motivation_text = str(row.get(motivation_col, ''))

                    # Get general feedback
                    valuable_col = 'What was the most valuable part of the program?'
                    valuable_text = str(row.get(valuable_col, ''))
                    anything_col = 'Anything else you want to share with us?'
                    anything_else = str(row.get(anything_col, ''))

                    # Combine feedback
                    combined_feedback = f"{motivation_text} {valuable_text} {anything_else}".strip()
                    if combined_feedback and combined_feedback != 'nan':
                        session_feedback.append({
                            'nps_score': row['NPS_Score'],
                            'nps_category': row['NPS_Category'],
                            'feedback': combined_feedback,
                            'length': len(combined_feedback)
                        })

                if len(session_feedback) == 0:
                    continue

                # Create session key (clean up session name)
                session_key = session_name
                if len(session_key) > 60:
                    session_key = session_key[:57] + "..."

                # Analyze based on number of reviews
                if len(session_feedback) > 3:
                    # Extract keywords from all feedback
                    all_feedback_text = ' '.join([item['feedback'] for item in session_feedback])
                    keywords = extract_keywords(all_feedback_text)
                    keyword_counts = Counter(keywords).most_common(6)

                    track_sessions[session_key] = {
                        'type': 'keywords',
                        'review_count': len(session_feedback),
                        'keywords': keyword_counts,
                        'avg_nps': (sum(item['nps_score'] for item in session_feedback) /
                                    len(session_feedback)),
                        'full_name': session_name
                    }
                else:
                    # Find the best comment (highest NPS score, then longest feedback)
                    best_comment = max(session_feedback,
                                     key=lambda x: (x['nps_score'], x['length']))

                    track_sessions[session_key] = {
                        'type': 'best_comment',
                        'review_count': len(session_feedback),
                        'best_comment': best_comment,
                        'avg_nps': (sum(item['nps_score'] for item in session_feedback) /
                                    len(session_feedback)),
                        'full_name': session_name
                    }

        results[track] = track_sessions

    return results


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

            all_text = (f"{valuable_text} {motivation_text} {motivation_text2} "
                        f"{session_enjoyed} {session2_enjoyed} {anything_else}")
            keywords = extract_keywords(all_text)
            positive_keywords.extend(keywords)

        # Get most comprehensive negative reviews from detractors
        comprehensive_reviews = []
        for _, row in detractors.iterrows():
            improve_text = str(row.get('What should we improve?', ''))
            if len(improve_text) > 50 and improve_text != 'nan':
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
            'comprehensive_reviews': comprehensive_reviews[:3],
            'avg_nps': track_data['NPS_Score'].mean()
        }

    return results


def print_all_sessions_analysis(session_results):
    """Print analysis of all sessions by track"""
    print("\n" + "=" * 80)
    print("ALL SESSIONS ANALYSIS BY TRACK")
    print("=" * 80)
    
    for track, sessions in session_results.items():
        print(f"\n{'='*20} {track} TRACK SESSIONS {'='*20}")
        
        if not sessions:
            print("  No session data available for this track")
            continue
            
        for session_name, data in sessions.items():
            print(f"\n📋 {session_name}")
            if 'full_name' in data and data['full_name'] != session_name:
                print(f"   Full: {data['full_name']}")
            print(f"   Reviews: {data['review_count']} | Avg NPS: {data['avg_nps']:.1f}")
            
            if data['type'] == 'keywords':
                print("   🔑 Keywords:")
                for keyword, count in data['keywords']:
                    print(f"     • {keyword} ({count} mentions)")
            else:
                print("   💬 Best Comment:")
                comment = data['best_comment']
                print(f"     NPS {comment['nps_score']} ({comment['nps_category']}):")
                print(f"     \"{comment['feedback']}\"")
        
        print("-" * 60)


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

        print("\n🔑 TOP KEYWORDS FROM PROMOTERS:")
        if data['top_keywords']:
            for keyword, count in data['top_keywords']:
                print(f"  • {keyword} ({count} mentions)")
        else:
            print("  No significant keywords found")

        print("\n📝 MOST COMPREHENSIVE NEGATIVE REVIEWS:")
        if data['comprehensive_reviews']:
            for i, review in enumerate(data['comprehensive_reviews'], 1):
                print(f"\n  {i}. NPS {review['nps_score']} ({review['length']} chars):")
                print(f"     \"{review['feedback']}\"")
        else:
            print("  No comprehensive negative reviews found")

        print("-" * 60)


def save_all_sessions_analysis(session_results):
    """Save all sessions analysis to CSV"""
    os.makedirs("csv", exist_ok=True)
    
    # Create data for CSV
    session_data = []
    
    for track, sessions in session_results.items():
        for session_name, data in sessions.items():
            if data['type'] == 'keywords':
                for keyword, count in data['keywords']:
                    session_data.append({
                        'Track': track,
                        'Session': session_name,
                        'Type': 'Keywords',
                        'Review_Count': data['review_count'],
                        'Avg_NPS': round(data['avg_nps'], 1),
                        'Keyword': keyword,
                        'Mentions': count,
                        'Best_Comment': ''
                    })
            else:
                comment = data['best_comment']
                session_data.append({
                    'Track': track,
                    'Session': session_name,
                    'Type': 'Best_Comment',
                    'Review_Count': data['review_count'],
                    'Avg_NPS': round(data['avg_nps'], 1),
                    'Keyword': '',
                    'Mentions': 0,
                    'Best_Comment': comment['feedback']
                })
    
    # Save to CSV
    pd.DataFrame(session_data).to_csv("csv/all_sessions_analysis.csv", index=False)
    print("\nAll sessions analysis saved to: csv/all_sessions_analysis.csv")


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

    print("\nAnalysis saved to:")
    print("  • csv/track_summary.csv")
    print("  • csv/track_keywords.csv")
    print("  • csv/track_reviews.csv")


def main():
    """Main function to run track analysis"""
    try:
        df = pd.read_csv("csv/imported_data.csv")
        df = extract_nps_scores(df)

        # Original track analysis
        results = analyze_track_feedback(df)
        print_track_analysis(results)
        save_track_analysis(results)
        
        # New all sessions analysis
        session_results = analyze_all_sessions_by_track(df)
        print_all_sessions_analysis(session_results)
        save_all_sessions_analysis(session_results)

        return results, session_results

    except FileNotFoundError:
        print("Error: csv/imported_data.csv not found. Please run step1 first.")
        return None, None
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None, None


if __name__ == "__main__":
    main()
