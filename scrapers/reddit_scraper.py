import praw

# Reddit credentials
reddit = praw.Reddit(
    client_id='D4DxUqV8CL1rBWk8z-wdMA',
    client_secret='wUZrrKs_eiQDX2sdnMri4w6LyQBDjg',
    user_agent='StockSentimentAnalyzer by /u/Kindly_Smile_3861'
)

# Relevant subreddits (only existant/active ones)
subreddits = [
    "stocks", "investing", "IndianStockMarket", "wallstreetbets",
    "ValueInvesting", "StockMarket", "finance", "economy",
    "StartupIndia", "Business", "investingindia", "technology", "IPO"
]

# Keywords to filter posts
keywords = ["stock", "share", "NSE", "BSE", "Infosys", "IPO", "earnings", "CEO", "founder", "revenue", "profit"]

def fetch_reddit_posts(keyword, limit_per_sub=5):
    posts = []
    for sub in subreddits:
        try:
            subreddit_obj = reddit.subreddit(sub)
            for submission in subreddit_obj.search(keyword, sort="new", limit=limit_per_sub):
                text = submission.title
                if submission.selftext:
                    text += " " + submission.selftext
                # Filter by keywords
                if any(k.lower() in text.lower() for k in keywords):
                    posts.append(text)
        except Exception as e:
            print(f"Skipping subreddit '{sub}' due to error: {e}")
            continue
    return posts
