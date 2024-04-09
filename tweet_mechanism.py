# tweet_mechanism.py

import random
from datetime import datetime, timedelta

def get_day_message():
    
    current_time = datetime.now()
    current_hour = current_time.hour
    current_weekday = current_time.weekday()

    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    current_day = weekday_names[current_weekday]

    # 1) If it's Monday to Friday morning
    if current_weekday in range(0, 5) and 6 <= current_hour < 9:
        day_message = f"It's {current_day} morning where Ella needs to get ready for school.  "

    # 2) If it's Monday to Friday afternoon
    if current_weekday in range(0, 5) and 9 <= current_hour < 15:
        day_message = f"Ella is in school right now.  "

    if current_weekday in range(0, 5) and 15 <= current_hour < 19:
        day_message = f"Ella is out of school.  "

    # 3) If it's Monday to Thursday evening
    if current_weekday in range(0, 4) and 19 <= current_hour:
        day_message = f"It's evening time Ella has school tomorrow.  "

    # 4) If it's Sunday evening
    if current_weekday == 6 and 18 <= current_hour:
        day_message = "It's evening time and Ella has school tomorrow.  "

    # 5) If it's Friday or Saturday evening
    if current_weekday == 4 and 18 <= current_hour:
        day_message = "It's a Friday evening and Ellas weekend begins.  "

    if current_weekday == 5 and 18 <= current_hour:
        day_message = "It's Saturday night"

    # 6) If it's Saturday or Sunday morning
    if current_weekday in [5, 6] and 6 <= current_hour < 12:
        day_message = f"It's {current_day} morning.  "

    # 7) If it's Saturday or Sunday afternoon
    if current_weekday in [5, 6] and 12 <= current_hour < 18:
        day_message = f"It's {current_day} afternoon.  "

    return day_message + get_random_event()

def generate_message(openai_api_key, tweeted_messages_file):
    # ... [similar code as provided above]

def post_daily_tweet(oauth, openai_api_key, tweeted_messages_file):
    # ... [similar code as provided above]
