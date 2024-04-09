# main.py

import config_loader
import twitter_auth
import openai_integration
import tweet_mechanism

# Load environment variables
consumer_key = config_loader.get_env_var("CONSUMER_KEY")
consumer_secret = config_loader.get_env_var("CONSUMER_SECRET")
access_token = config_loader.get_env_var("ACCESS_TOKEN")
access_token_secret = config_loader.get_env_var("ACCESS_TOKEN_SECRET")
openai_api_key = config_loader.get_env_var("OPENAI_API_KEY")
tweeted_messages_file = config_loader.get_env_var("TWEETED_MESSAGES_FILE")

# Set up Twitter authentication
oauth = twitter_auth.get_oauth_session(consumer_key, consumer_secret)

# Set up OpenAI
openai_integration.setup_openai(openai_api_key)

# Start Tweeting
tweet_mechanism.post_daily_tweet(oauth, openai_api_key, tweeted_messages_file)
