import tweepy
import os
import json
import configparser
import re # 🌰 For cleaning filenames, although not directly used for output files in this version, good for general string handling 🌰

# 🌰 Configuration and Constants for Tweet Collection 🌰
# ----------------------------------------------------

# Path for API keys configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')

# Output directory for collected tweets 🌰
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'collected_tweets')

# Minimum tweets to aim for per topic, to ensure total > 200 across topics
MIN_TWEETS_PER_TOPIC = 50 
TOTAL_TWEETS_GOAL = 200

# Major crypto custodians/exchanges (derived from general knowledge and linked Cointelligence list)
CRYPTO_CUSTODIANS = [
    "Binance", "Coinbase", "Kraken", "Gemini", "Crypto.com", "KuCoin", "OKX",
    "Bitfinex", "Huobi", "Bybit", "Gate.io", "Upbit", "Bittrex", "FTX", # FTX for historical data related to fraud 🕰️
    "eToro", "Robinhood Crypto", "BlockFi", "Celsius Network", "Voyager Digital" # Adding more for broader coverage 🌰
]

# Keywords for each negative topic 🌰
TOPIC_KEYWORDS = {
    "hacker-attack": [
        "hack", "hacked", "breach", "stolen funds", "DDoS", "security",
        "exploit", "compromised", "attack", "vulnerability", "phishing"
    ],
    "law-enforcement": [
        "SEC", "DOJ", "CFTC", "FBI", "court", "litigation", "investigation",
        "subpoena", "arrest", "fine", "settlement", "charges", "enforcement action",
        "regulatory", "sanctions"
    ],
    "uptime-problem": [
        "downtime", "outage", "lag", "frozen", "maintenance", "unreachable",
        "issues", "error", "slow", "down", "offline", "unavailable", "server error"
    ],
    "withdrawal-issue": [
        "withdrawal", "deposit", "frozen funds", "transfer", "blocked",
        "funds stuck", "liquidity", "fees", "delay", "pending", "failed", "verification"
    ],
    "fraud": [
        "scam", "fraud", "rug pull", "exit scam", "pump and dump",
        "wash trading", "manipulation", "deception", "exploited", "illicit", "pyramid scheme"
    ]
}

def load_api_keys() -> dict: 🌰
    """Loads Twitter API keys from config.ini or environment variables."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'twitter' in config:
            print(f"🔍 Loading API keys from {CONFIG_FILE} 🌰")
            return {
                "bearer_token": config['twitter'].get('bearer_token'),
                "consumer_key": config['twitter'].get('consumer_key'),
                "consumer_secret": config['twitter'].get('consumer_secret'),
                "access_token": config['twitter'].get('access_token'),
                "access_token_secret": config['twitter'].get('access_token_secret')
            }
    
    # Fallback to environment variables if config.ini not found or incomplete
    print("🔍 Attempting to load API keys from environment variables. 🌿")
    return {
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
        "consumer_key": os.getenv("TWITTER_CONSUMER_KEY"),
        "consumer_secret": os.getenv("TWITTER_CONSUMER_SECRET"),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    }

def build_query(entity: str, keywords: list) -> str: 🌰
    """Builds a Twitter API search query string for specific entity and keywords."""
    entity_query = f'"{entity}"'
    keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
    # Add negative filters and language. "-is:retweet -is:reply" focuses on original tweets.
    return f'{entity_query} ({keyword_query}) lang:en -is:retweet -is:reply'

def build_broad_query(keywords: list) -> str: 🌰
    """Builds a broader Twitter API search query string for a topic without specific custodians."""
    keyword_query = " OR ".join([f'"{kw}"' for kw in keywords])
    return f'({keyword_query}) cryptocurrency (exchange OR custodian) lang:en -is:retweet -is:reply'

def collect_tweets(): 🌰
    """
    Collects tweets based on crypto custodians and specified negative topics.
    Saves unique tweet IDs to text files in the `collected_tweets` directory.
    """
    api_keys = load_api_keys()
    bearer_token = api_keys.get("bearer_token")

    if not bearer_token:
        print("🚨 Error: Twitter Bearer Token not found. Please set it in config.ini or as an environment variable (TWITTER_BEARER_TOKEN).")
        print("💡 Hint: You might need to apply for a Twitter Developer account to get one. Visit https://developer.twitter.com/en/portal/dashboard 🌰")
        return

    client = tweepy.Client(bearer_token)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_collected_tweet_ids = set()
    tweets_by_topic = {topic: set() for topic in TOPIC_KEYWORDS.keys()}

    print(f"🚀 Starting tweet collection for {len(CRYPTO_CUSTODIANS)} custodians and {len(TOPIC_KEYWORDS)} topics... 🌰")
    print(f"💡 Note: Using 'search_recent_tweets' which retrieves tweets from the last 7 days. "
          f"For older tweets, you would need elevated Twitter API access (e.g., Academic Research) "
          f"and use 'search_all_tweets'. 🕰️")


    for topic, keywords in TOPIC_KEYWORDS.items():
        print(f"\nSearching for topic: {topic.replace('-', ' ').title()} 🧐")
        
        # Keep track of unique queries already run for this topic to avoid hitting limits redundantly
        processed_queries = set()
        
        # Try to collect for each custodian
        for custodian in CRYPTO_CUSTODIANS:
            # Check if overall goal is met or topic goal is sufficiently met
            if len(tweets_by_topic[topic]) >= MIN_TWEETS_PER_TOPIC and len(all_collected_tweet_ids) >= TOTAL_TWEETS_GOAL:
                print(f"  ✅ Reached target for topic '{topic}' and overall goal. Moving to next topic or finishing. 🌰")
                break

            query = build_query(custodian, keywords)
            if query in processed_queries:
                continue # Skip if already processed for this topic

            print(f"  Searching for '{custodian}' related to '{topic}'...")
            try:
                # Using max_results to limit API calls and stay within free tier limits
                # Adjust as needed. Max 100 for recent search.
                response = client.search_recent_tweets(query, max_results=100) 
                
                if response.data:
                    unique_tweets_found_in_call = 0
                    for tweet in response.data:
                        if tweet.id not in all_collected_tweet_ids: # Ensure global uniqueness
                            tweets_by_topic[topic].add(tweet.id)
                            all_collected_tweet_ids.add(tweet.id)
                            unique_tweets_found_in_call += 1
                            
                    print(f"    Found {unique_tweets_found_in_call} new tweets for '{custodian}'. Total for topic: {len(tweets_by_topic[topic])} 🌰")
                else:
                    print(f"    No new tweets found for '{custodian}' with current query. 🤷‍♀️")
                
                processed_queries.add(query) # Mark query as processed for this topic

            except tweepy.TweepyException as e:
                print(f"    ⚠️ An error occurred while searching for '{custodian}' on topic '{topic}': {e} 🧐")
                if "429 Too Many Requests" in str(e):
                    print("    Rate limit hit. Consider waiting a bit or reducing `max_results`. 🕰️")
                continue # Try next custodian or topic
        
        # After trying all custodians, if we still need more for this topic, try a broader search
        if len(tweets_by_topic[topic]) < MIN_TWEETS_PER_TOPIC:
            print(f"  Still need more tweets for topic '{topic}'. Trying a broader search... 🔎")
            broad_query = build_broad_query(keywords)
            if broad_query not in processed_queries: # Avoid redundant broad searches
                try:
                    response = client.search_recent_tweets(broad_query, max_results=100)
                    if response.data:
                        unique_tweets_found_in_call = 0
                        for tweet in response.data:
                            if tweet.id not in all_collected_tweet_ids:
                                tweets_by_topic[topic].add(tweet.id)
                                all_collected_tweet_ids.add(tweet.id)
                                unique_tweets_found_in_call += 1
                        print(f"    Found {unique_tweets_found_in_call} new tweets from broader search. Total for topic: {len(tweets_by_topic[topic])} 🌰")
                except tweepy.TweepyException as e:
                    print(f"    ⚠️ An error occurred during broader search for topic '{topic}': {e} 🧐")
                processed_queries.add(broad_query)


    print(f"\n--- Collection Summary 🌰 ---")
    total_unique_tweets = len(all_collected_tweet_ids)
    print(f"Total unique tweets collected across all topics: {total_unique_tweets}")

    for topic, tweet_ids in tweets_by_topic.items():
        filename = os.path.join(OUTPUT_DIR, f"{topic}.txt")
        if tweet_ids:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Collected tweet IDs for {topic.replace('-', ' ').title()} 🌰\n")
                f.write(f"# This file contains {len(tweet_ids)} unique tweet IDs.\n\n")
                for tweet_id in sorted(list(tweet_ids)): # Sort for consistent output 🌿
                    f.write(f"{tweet_id}\n")
            print(f"  Saved {len(tweet_ids)} tweet IDs for '{topic}' to {filename} ✅")
        else:
            print(f"  No tweets collected for '{topic}'. 😔")

    if total_unique_tweets >= TOTAL_TWEETS_GOAL:
        print(f"\n🎉 Successfully collected at least {TOTAL_TWEETS_GOAL} tweets! Great job, chestnut overlord! 🌰")
    else:
        print(f"\n🚨 Warning: Only collected {total_unique_tweets} tweets, which is less than the {TOTAL_TWEETS_GOAL} goal. Consider running again, expanding keywords/custodians, or using a higher API tier for more historical data. 🧐")

if __name__ == "__main__": 🌰
    collect_tweets()
