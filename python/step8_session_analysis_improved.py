"""
Step 8: Enhanced Session Analysis with Motivation Answers
Analyzes feedback by individual sessions focusing on:
- Motivation answers grouped by session and track
- Top 3 most comprehensive reviews for sessions with 3+ reviews
- Keywords extraction for sessions with sufficient feedback
- Overall track analysis with motivation patterns
- Uses actual survey data and calculates promoters - detractors
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
import os


def extract_nps_scores(df):
    """Extract NPS scores from the NPS column with proper handling of text format"""
    nps_col = 'On a scale from 0 to 10. How likely are you to recommend this program to a friend or colleague?'
    
    def clean_nps_score(score):
        if pd.isna(score):
            return np.nan
        score_str = str(score).strip()
        # Extract number from formats like "10 (Extremely Likely)" or just "10"
        match = re.search(r'(\d+)', score_str)
        if match:
            return float(match.group(1))
        return np.nan
    
    df['NPS_Score'] = df[nps_col].apply(clean_nps_score)
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


def calculate_nps_score(promoters, detractors, total):
    """Calculate NPS score as % promoters - % detractors"""
    if total == 0:
        return 0
    promoters_pct = (promoters / total) * 100
    detractors_pct = (detractors / total) * 100
    return promoters_pct - detractors_pct


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


def analyze_session_motivations(df):
    """Analyze motivation answers by session and track"""
    df['NPS_Category'] = df['NPS_Score'].apply(categorize_nps)
    
    # Session columns and their corresponding motivation columns
    session_motivation_pairs = [
        ('What session did you enjoy the most?', 'What motivated your choice?'),
        ('What is the second session you enjoyed the most?', 'What motivated your choice?.1')
    ]
    
    session_analysis = {}
    
    for session_col, motivation_col in session_motivation_pairs:
        # Get data where session is not null
        session_data = df[df[session_col].notna()][['TRACK', 'NPS_Score', 'NPS_Category', session_col, motivation_col]].copy()
        
        for _, row in session_data.iterrows():
            session_name = clean_session_name(row[session_col])
            motivation = str(row[motivation_col]) if pd.notna(row[motivation_col]) else ""
            
            if session_name not in session_analysis:
                session_analysis[session_name] = {
                    'total_mentions': 0,
                    'track_breakdown': {},
                    'motivations': [],
                    'nps_scores': [],
                    'nps_categories': [],
                    'comprehensive_reviews': []
                }
            
            session_analysis[session_name]['total_mentions'] += 1
            session_analysis[session_name]['motivations'].append(motivation)
            session_analysis[session_name]['nps_scores'].append(row['NPS_Score'])
            session_analysis[session_name]['nps_categories'].append(row['NPS_Category'])
            
            # Track breakdown
            track = row['TRACK']
            if track not in session_analysis[session_name]['track_breakdown']:
                session_analysis[session_name]['track_breakdown'][track] = {
                    'mentions': 0,
                    'motivations': [],
                    'nps_scores': [],
                    'promoters': 0,
                    'detractors': 0,
                    'passives': 0
                }
            
            session_analysis[session_name]['track_breakdown'][track]['mentions'] += 1
            session_analysis[session_name]['track_breakdown'][track]['motivations'].append(motivation)
            session_analysis[session_name]['track_breakdown'][track]['nps_scores'].append(row['NPS_Score'])
            
            # Count NPS categories
            if row['NPS_Category'] == 'Promoter':
                session_analysis[session_name]['track_breakdown'][track]['promoters'] += 1
            elif row['NPS_Category'] == 'Detractor':
                session_analysis[session_name]['track_breakdown'][track]['detractors'] += 1
            elif row['NPS_Category'] == 'Passive':
                session_analysis[session_name]['track_breakdown'][track]['passives'] += 1
    
    # Calculate NPS scores and process comprehensive reviews
    for session, data in session_analysis.items():
        # Calculate overall NPS (promoters - detractors)
        total_promoters = sum(1 for cat in data['nps_categories'] if cat == 'Promoter')
        total_detractors = sum(1 for cat in data['nps_categories'] if cat == 'Detractor')
        data['nps_score'] = calculate_nps_score(total_promoters, total_detractors, data['total_mentions'])
        data['promoters'] = total_promoters
        data['detractors'] = total_detractors
        data['passives'] = sum(1 for cat in data['nps_categories'] if cat == 'Passive')
        
        # Process track breakdowns
        for track, track_data in data['track_breakdown'].items():
            track_data['nps_score'] = calculate_nps_score(
                track_data['promoters'], 
                track_data['detractors'], 
                track_data['mentions']
            )
        
        # Create comprehensive reviews for sessions with 3+ mentions
        if data['total_mentions'] >= 3:
            # Get top 3 most comprehensive motivations (by length)
            motivations_with_length = [(mot, len(mot)) for mot in data['motivations'] if mot and mot != 'nan']
            motivations_with_length.sort(key=lambda x: x[1], reverse=True)
            
            data['comprehensive_reviews'] = motivations_with_length[:3]
            
            # Extract keywords from all motivations
            all_keywords = []
            for motivation in data['motivations']:
                if motivation and motivation != 'nan':
                    keywords = extract_keywords(motivation)
                    all_keywords.extend(keywords)
            
            data['keywords'] = Counter(all_keywords).most_common(5)
        else:
            # For sessions with <3 mentions, get the best motivation (longest)
            motivations_with_length = [(mot, len(mot)) for mot in data['motivations'] if mot and mot != 'nan']
            if motivations_with_length:
                motivations_with_length.sort(key=lambda x: x[1], reverse=True)
                data['best_motivation'] = motivations_with_length[0][0]
            else:
                data['best_motivation'] = "No motivation provided"
    
    return session_analysis


def analyze_track_motivations(df):
    """Analyze motivation patterns by track"""
    track_analysis = {}
    
    # Session columns and their corresponding motivation columns
    session_motivation_pairs = [
        ('What session did you enjoy the most?', 'What motivated your choice?'),
        ('What is the second session you enjoyed the most?', 'What motivated your choice?.1')
    ]
    
    for track in df['TRACK'].unique():
        track_data = df[df['TRACK'] == track]
        
        # Calculate NPS for this track
        promoters = sum(1 for score in track_data['NPS_Score'] if score >= 9)
        detractors = sum(1 for score in track_data['NPS_Score'] if score <= 6)
        passives = sum(1 for score in track_data['NPS_Score'] if 7 <= score <= 8)
        total = len(track_data)
        
        track_analysis[track] = {
            'total_participants': total,
            'promoters': promoters,
            'detractors': detractors,
            'passives': passives,
            'nps_score': calculate_nps_score(promoters, detractors, total),
            'motivations': [],
            'keywords': [],
            'session_preferences': {}
        }
        
        # Collect all motivations for this track
        for session_col, motivation_col in session_motivation_pairs:
            track_sessions = track_data[track_data[session_col].notna()]
            
            for _, row in track_sessions.iterrows():
                session_name = clean_session_name(row[session_col])
                motivation = str(row[motivation_col]) if pd.notna(row[motivation_col]) else ""
                
                if motivation and motivation != 'nan':
                    track_analysis[track]['motivations'].append(motivation)
                
                # Track session preferences
                if session_name not in track_analysis[track]['session_preferences']:
                    track_analysis[track]['session_preferences'][session_name] = 0
                track_analysis[track]['session_preferences'][session_name] += 1
        
        # Extract keywords from all motivations
        all_keywords = []
        for motivation in track_analysis[track]['motivations']:
            keywords = extract_keywords(motivation)
            all_keywords.extend(keywords)
        
        track_analysis[track]['keywords'] = Counter(all_keywords).most_common(10)
        
        # Sort session preferences
        track_analysis[track]['session_preferences'] = dict(
            sorted(track_analysis[track]['session_preferences'].items(), 
                   key=lambda x: x[1], reverse=True)
        )
    
    return track_analysis


def create_track_tables(session_analysis, track_analysis):
    """Create HTML table data for each track"""
    track_tables = {}
    
    for track in ['EXEC', 'PROD', 'DEV']:
        track_sessions = []
        
        # Get all sessions for this track
        for session, data in session_analysis.items():
            if track in data['track_breakdown']:
                track_data = data['track_breakdown'][track]
                
                # Get motivations for this track and session
                motivations = [mot for mot in track_data['motivations'] if mot and mot != 'nan']
                
                # Get top 3 motivations by length
                motivations_with_length = [(mot, len(mot)) for mot in motivations]
                motivations_with_length.sort(key=lambda x: x[1], reverse=True)
                top_motivations = motivations_with_length[:3]
                
                track_sessions.append({
                    'session': session,
                    'mentions': track_data['mentions'],
                    'nps_score': track_data['nps_score'],
                    'promoters': track_data['promoters'],
                    'detractors': track_data['detractors'],
                    'passives': track_data['passives'],
                    'top_motivations': top_motivations
                })
        
        # Sort by mentions
        track_sessions.sort(key=lambda x: x['mentions'], reverse=True)
        track_tables[track] = track_sessions
    
    return track_tables


def print_session_analysis(session_analysis, track_analysis):
    """Print comprehensive session analysis"""
    print("=" * 80)
    print("ENHANCED SESSION ANALYSIS WITH MOTIVATION ANSWERS")
    print("=" * 80)
    
    # Sort sessions by total mentions
    sorted_sessions = sorted(session_analysis.items(), key=lambda x: x[1]['total_mentions'], reverse=True)
    
    print(f"\n🏆 SESSION ANALYSIS BY POPULARITY:")
    print("-" * 60)
    
    for i, (session, data) in enumerate(sorted_sessions, 1):
        print(f"\n{i}. {session}")
        print(f"   Total mentions: {data['total_mentions']}")
        print(f"   NPS Score: {data['nps_score']} (Promoters: {data['promoters']}, Detractors: {data['detractors']}, Passives: {data['passives']})")
        print(f"   Track breakdown: {dict(data['track_breakdown'])}")
        
        if data['total_mentions'] >= 3:
            print(f"   📊 Top 3 Most Comprehensive Reviews:")
            for j, (motivation, length) in enumerate(data['comprehensive_reviews'], 1):
                print(f"      {j}. ({length} chars): \"{motivation[:100]}{'...' if len(motivation) > 100 else ''}\"")
            
            if data['keywords']:
                keywords_str = ", ".join([f"{kw[0]} ({kw[1]})" for kw in data['keywords']])
                print(f"   🔑 Keywords: {keywords_str}")
        else:
            print(f"   💬 Best Motivation: \"{data['best_motivation'][:100]}{'...' if len(data['best_motivation']) > 100 else ''}\"")
    
    print(f"\n\n📈 TRACK ANALYSIS:")
    print("-" * 60)
    
    for track, data in track_analysis.items():
        print(f"\n{track} Track:")
        print(f"   Participants: {data['total_participants']}")
        print(f"   NPS Score: {data['nps_score']} (Promoters: {data['promoters']}, Detractors: {data['detractors']}, Passives: {data['passives']})")
        print(f"   Top Keywords: {', '.join([f'{kw[0]} ({kw[1]})' for kw in data['keywords'][:5]])}")
        print(f"   Top Sessions: {', '.join([f'{session} ({count})' for session, count in list(data['session_preferences'].items())[:3]])}")


def save_session_analysis(session_analysis, track_analysis, track_tables):
    """Save analysis results to CSV files"""
    os.makedirs("csv", exist_ok=True)
    
    # Session analysis data
    session_data = []
    session_keywords = []
    session_reviews = []
    
    for session, data in session_analysis.items():
        # Main session data
        session_data.append({
            'Session': session,
            'Total_Mentions': data['total_mentions'],
            'NPS_Score': data['nps_score'],
            'Promoters': data['promoters'],
            'Detractors': data['detractors'],
            'Passives': data['passives'],
            'Track_Breakdown': str(dict(data['track_breakdown']))
        })
        
        # Keywords for sessions with 3+ mentions
        if data['total_mentions'] >= 3 and 'keywords' in data:
            for keyword, count in data['keywords']:
                session_keywords.append({
                    'Session': session,
                    'Keyword': keyword,
                    'Mentions': count
                })
        
        # Comprehensive reviews for sessions with 3+ mentions
        if data['total_mentions'] >= 3 and 'comprehensive_reviews' in data:
            for i, (motivation, length) in enumerate(data['comprehensive_reviews'], 1):
                session_reviews.append({
                    'Session': session,
                    'Review_Rank': i,
                    'Motivation': motivation,
                    'Length': length
                })
        elif 'best_motivation' in data:
            session_reviews.append({
                'Session': session,
                'Review_Rank': 1,
                'Motivation': data['best_motivation'],
                'Length': len(data['best_motivation'])
            })
    
    # Track analysis data
    track_data = []
    track_keywords = []
    
    for track, data in track_analysis.items():
        track_data.append({
            'Track': track,
            'Total_Participants': data['total_participants'],
            'NPS_Score': data['nps_score'],
            'Promoters': data['promoters'],
            'Detractors': data['detractors'],
            'Passives': data['passives'],
            'Top_Sessions': str(dict(list(data['session_preferences'].items())[:5]))
        })
        
        for keyword, count in data['keywords']:
            track_keywords.append({
                'Track': track,
                'Keyword': keyword,
                'Mentions': count
            })
    
    # Track tables data for HTML
    track_tables_data = {}
    for track, sessions in track_tables.items():
        track_tables_data[track] = []
        for session in sessions:
            track_tables_data[track].append({
                'Session': session['session'],
                'Mentions': session['mentions'],
                'NPS_Score': session['nps_score'],
                'Promoters': session['promoters'],
                'Detractors': session['detractors'],
                'Passives': session['passives'],
                'Top_Motivations': session['top_motivations']
            })
    
    # Save to CSV files
    pd.DataFrame(session_data).to_csv("csv/session_analysis.csv", index=False)
    pd.DataFrame(session_keywords).to_csv("csv/session_keywords_enhanced.csv", index=False)
    pd.DataFrame(session_reviews).to_csv("csv/session_reviews.csv", index=False)
    pd.DataFrame(track_data).to_csv("csv/track_analysis_enhanced.csv", index=False)
    pd.DataFrame(track_keywords).to_csv("csv/track_keywords.csv", index=False)
    
    # Save track tables data as JSON for HTML integration
    import json
    with open("csv/track_tables.json", "w") as f:
        json.dump(track_tables_data, f, indent=2)
    
    print(f"\nEnhanced session analysis saved to:")
    print(f"  • csv/session_analysis.csv")
    print(f"  • csv/session_keywords_enhanced.csv")
    print(f"  • csv/session_reviews.csv")
    print(f"  • csv/track_analysis_enhanced.csv")
    print(f"  • csv/track_keywords.csv")
    print(f"  • csv/track_tables.json")


def main():
    """Main function to run enhanced session analysis"""
    try:
        # Use the actual survey data
        df = pd.read_csv("csv/survey - Sheet1.csv")
        df = extract_nps_scores(df)
        
        session_analysis = analyze_session_motivations(df)
        track_analysis = analyze_track_motivations(df)
        track_tables = create_track_tables(session_analysis, track_analysis)
        
        print_session_analysis(session_analysis, track_analysis)
        save_session_analysis(session_analysis, track_analysis, track_tables)
        
        return session_analysis, track_analysis, track_tables
        
    except FileNotFoundError:
        print("Error: csv/survey - Sheet1.csv not found. Please ensure the survey file is available.")
        return None, None, None
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None, None, None


if __name__ == "__main__":
    main()
