from collections import defaultdict, deque
from datetime import datetime, timedelta
import csv
from typing import Dict, List, Set, Tuple
import json
from operator import itemgetter

def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime object."""
    return datetime.fromisoformat(ts)

def analyze_activity(filename: str) -> Tuple[List[Tuple[str, str, int]], Set[Tuple[str, str, str, datetime]]]:
    """
    Analyze activity data to find:
    1. Top 5 users by action count
    2. Users performing same action >10 times in 5-minute windows
    """
    user_actions = defaultdict(int)  # Track total actions per user
    user_action_windows = defaultdict(lambda: defaultdict(deque))  # Track time windows per user+action
    suspicious_activities = set()  # Store suspicious activities
    user_names = {}  # Store user names
    
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = parse_timestamp(row['timestamp'])
            user_id = row['user_id']
            action = row['action']
            
            # Store username if available
            if 'username' in row:
                user_names[user_id] = row['username']
            
            # Count total actions per user
            user_actions[user_id] += 1
            
            # Sliding window analysis
            window = user_action_windows[user_id][action]
            window.append(timestamp)
            
            # Remove timestamps older than 5 minutes
            while window and (timestamp - window[0]) > timedelta(minutes=5):
                window.popleft()
            
            # Check if user has performed same action >10 times in window
            if len(window) > 10:
                suspicious_activities.add((user_id, user_names.get(user_id, user_id), action, timestamp))
    
    # Get top 5 users by action count
    top_users = [(uid, user_names.get(uid, uid), count) for uid, count in 
                sorted(user_actions.items(), key=itemgetter(1), reverse=True)[:5]]
    
    return top_users, suspicious_activities

def format_output(top_users: List[Tuple[str, str, int]], 
                 suspicious: Set[Tuple[str, str, str, datetime]], 
                 output_format: str = 'text') -> None:
    """Format and display the analysis results."""
    if output_format == 'text':
        print("\n=== Top 5 Users by Action Count ===")
        for user_id, username, count in top_users:
            print(f"{username} ({user_id}): {count} actions")
        
        print("\n=== Suspicious Activity (>10 same actions in 5 minutes) ===")
        for user_id, username, action, timestamp in sorted(suspicious, key=lambda x: x[3]):
            print(f"{username} ({user_id}) performed '{action}' suspiciously at {timestamp}")
    
    elif output_format == 'json':
        result = {
            'top_users': [{'user_id': uid, 'username': uname, 'count': count} for uid, uname, count in top_users],
            'suspicious_activities': [
                {'user_id': uid, 'username': uname, 'action': action, 'timestamp': ts.isoformat()}
                for uid, uname, action, ts in suspicious
            ]
        }
        print(json.dumps(result, indent=2))

def main():
    # Analyze the activity data
    top_users, suspicious = analyze_activity('activity.csv')
    
    # Output results in both text and JSON formats
    print("\n=== Plain Text Output ===")
    format_output(top_users, suspicious, 'text')
    
    print("\n=== JSON Output ===")
    format_output(top_users, suspicious, 'json')

if __name__ == '__main__':
    main()