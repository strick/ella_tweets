import openai
import tweepy
import time
import json
import requests
from requests_oauthlib import OAuth1Session
import random
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API credentials
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY");

# File to store tweeted messages
tweeted_messages_file = os.getenv("TWEETED_MESSAGES_FILE")

# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")


# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)


# Authenticate with OpenAI
#openai.api_key = openai_api_key
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get(openai_api_key),
)

# Load previously tweeted messages from file
tweeted_messages = set()
try:
    with open(tweeted_messages_file, 'r', encoding='utf-8') as file:
        tweeted_messages = set(line.strip() for line in file)
except FileNotFoundError:
    pass

# Function to generate a unique message
def generate_message(tries = 1):

    # Keep trying to generate a new message until a unique one is found
    while True:

        user_prompt = get_day_message()

        system_prompt = ("Generate a tweet from either Ella or her Daddy based on their characters in the 'Ella and Daddy' children's book series. The series depicts Ella, a 7-year-old girl, and her single father engaging in everyday activities with a humorous twist.\n\n"
        "Character Backgrounds:\n"
        "Ella: Enjoys swimming, playing outdoors, Barbies, dogs, soccer, gymnastics, dance, martial arts, Roblox, cartwheels, and drawing. Attends a regular elementary school.\n"
        "Daddy: A work-from-home single parent. Interests include computers, programming, RPG video games, Marvel movies, Star Wars, fantasy books, quietness, running, and camping.\n"
        "Tweet Creation Guidelines:\n"
        "Probability: 80% chance the tweet is from Ella, 20% from Daddy.\n"
        "Content: Reflect their personalities and daily activities. Ensure humor and fun suitable for kids aged 3-10.\n"
        "Activity Focus: Clearly mention an ongoing or upcoming activity.\n"
        "Interaction: End with a question engaging the reader, related to the tweet's content.\n"
        "Hashtags: Include relevant hashtags.  Always include these two hashtags: #ChildrensBooks, #DaddyDaughterTime \n"
        "Character Limit: Ensure the tweet is under 150 characters.\n"
        "Style: Avoid quotation marks and specific days of the week.\n"
        "Exclusions: Do not include activities listed in the provided exclusion list.\n"
        "Purpose: The tweet should capture the essence of Ella and Daddy's relationship and the fun, everyday moments they share, resonating with the young audience of the book series.\n"
        "Exclusion List:\n")
       
        system_prompt += get_last_tweets()

        #print(f"System Prompt is: {system_prompt}")
        print(f"User Prompt: {user_prompt}")        

        #response = openai.ChatCompletion.create(
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=
            [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.7,  # Higher, up to 1, for more creativity
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        message = chat_completion.choices[0].message.content



        # Check if the message starts and ends with "
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]

        if message not in tweeted_messages:
           
            print("MESSAGE LEN" + str(len(message)))
            if(len(message) > 280 and tries < 3): 
                tries += 1
                generate_message(tries)
            
            return message

def get_last_tweets():
    # Read the last 10 tweets from the file
    
    try:
        with open(tweeted_messages_file, 'r', encoding='utf-8') as file:
            last_tweets = [line.strip() for line in file.readlines()[-30:]]
    except FileNotFoundError:
        last_tweets = []

    last_tweets = "\n- ".join(last_tweets)

    # Add - for the first tweet.
    return "- " + last_tweets

def get_day_message():

    current_time = datetime.now()
    current_hour = current_time.hour
    current_weekday = current_time.weekday()

    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    current_day = weekday_names[current_weekday]

    # 1) If it's Monday to Friday morning
    if current_weekday in range(0, 5) and 6 <= current_hour < 9:
        day_message = f"It's the morning and Ella is getting ready for school.  "

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

import random

def load_events_from_file(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def get_random_event():
    if random.random() < 0.25:
        events = load_events_from_file('events.txt')
        print("Random event occurred!")
        return random.choice(events)
    return ""

# Load events from the file


# Test the function
#event = get_random_event(events)
#if event:
#  print(event)
#else:
#    print("No event this time.")



# Function to post a daily tweet
def post_daily_tweet():

    while True:
        message = generate_message()
        tweeted_messages.add(message) # Add to the set of tweeted messages

        # Write the tweeted message to the file
        with open(tweeted_messages_file, 'a', encoding='utf-8') as file:
            file.write(message + '\n')

        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json={"text": message},
        )

        if response.status_code != 201:
            print("Error posting to twitter: " + response.text)
            print("Trying again...")
            continue
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )

        print(f"Tweeted: {message}")

        sleep_time = get_next_runtime()
        time.sleep(sleep_time)

def get_next_runtime():
    # Get the current time
    current_time = datetime.now()

    # Add at least 4 hours to the current time
    next_run_time = current_time + timedelta(hours=4)

    # Add random hours and minutes within the desired range (0 to 6 hours, 0 to 59 minutes)
    next_run_time += timedelta(hours=random.randint(0, 6), minutes=random.randint(0, 59), seconds=random.randint(0, 59))

    if next_run_time.hour >= 21 or next_run_time.hour < 7:
        # Set the time to 7 AM the next day
        next_run_time = next_run_time.replace(hour=7, minute=random.randint(0, 59), second=random.randint(0, 59)) + timedelta(days=1)

    # Check if sleep_time is negative or very small
    sleep_time = (next_run_time - datetime.now()).total_seconds()
    while sleep_time <= 60:  # less than a minute
        print("Computed next run time is too close. Adjusting...")
        # Add a few minutes and recompute sleep time
        next_run_time += timedelta(minutes=random.randint(1, 10))
        sleep_time = (next_run_time - datetime.now()).total_seconds()

    print(f"Sleeping until {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sleep time is: {sleep_time}")

    return sleep_time


# Start tweeting
post_daily_tweet()

