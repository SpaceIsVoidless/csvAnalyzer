import csv
from datetime import datetime, timedelta
import random

def generate_test_data(filename, num_records=100):
    # Create users with IDs and names
    user_data = {
        "user_1": "Alice Johnson",
        "user_2": "Bob Smith",
        "user_3": "Carol Williams",
        "user_4": "David Brown",
        "user_5": "Eva Martinez"
    }
    users = list(user_data.keys())
    actions = ["login", "logout", "view", "edit", "delete"]
    
    # Create test records
    records = []
    base_time = datetime(2025, 5, 20, 13, 0, 0)  # Fixed start time for consistency
    
    # Generate normal activities
    for i in range(num_records):
        user = random.choice(users)
        action = random.choice(actions)
        time_offset = timedelta(minutes=i)  # Spread events over time
        timestamp = (base_time + time_offset).isoformat()
        
        records.append({
            'timestamp': timestamp,
            'user_id': user,
            'username': user_data[user],
            'action': action
        })
    
    # Generate suspicious activities (>10 same actions within 5 minutes)
    suspicious_user = random.choice(users)
    suspicious_action = random.choice(actions)
    suspicious_start_time = base_time + timedelta(minutes=30)
    
    # Add 12 identical actions within 4 minutes
    for i in range(12):
        timestamp = (suspicious_start_time + timedelta(seconds=i*20)).isoformat()
        records.append({
            'timestamp': timestamp,
            'user_id': suspicious_user,
            'username': user_data[suspicious_user],
            'action': suspicious_action
        })
    
    # Sort records by timestamp
    records.sort(key=lambda x: x['timestamp'])
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'user_id', 'username', 'action']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(records)

if __name__ == '__main__':
    generate_test_data('activity.csv')
    print("Test data has been generated in activity.csv with suspicious activities")