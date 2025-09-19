# scrapers/twitter_scraper.py
import snscrape.modules.twitter as sntwitter
import pandas as pd

def fetch_twitter_posts(keyword, limit=10):
    tweets_list = []

    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword}').get_items()):
            if i >= limit:
                break
            tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])
    except Exception as e:
        print(f"Warning: Twitter scraping failed for '{keyword}': {e}")

    # Convert to DataFrame (optional, useful if you want metadata later)
    tweets_df = pd.DataFrame(tweets_list, columns=['Date', 'Tweet ID', 'Content', 'Username'])
    
    # Return only the tweet content for sentiment analysis
    return tweets_df['Content'].tolist()
