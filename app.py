# app.py

from scrapers.reddit_scraper import fetch_reddit_posts
from scrapers.twitter_scraper import fetch_twitter_posts  # You’ll create this using snscrape
from scrapers.news import fetch_all_news  # Yahoo + MoneyControl combined
from nlp.sentiment import analyze_sentiment
from collections import defaultdict, Counter
from datetime import datetime

# ===== CONFIGURATION =====
stock_symbols = ["INFY", "AMZN", "TCS", "RELIANCE"]
keywords = ["earnings", "buyback", "IPO", "dividend", "merger", "acquisition",
            "CEO", "guidance", "options", "calls", "puts", "intraday", "swing"]
limit_per_subreddit = 5
news_limit_per_stock = 5
twitter_limit_per_stock = 5

# ===== FETCH DATA =====
all_texts_per_stock = defaultdict(list)

for symbol in stock_symbols:
    # --- Reddit ---
    reddit_posts = fetch_reddit_posts(symbol, limit_per_sub=limit_per_subreddit)
    reddit_filtered = [p for p in reddit_posts if any(k.lower() in p.lower() for k in keywords)]

    # --- Twitter ---
    twitter_posts = fetch_twitter_posts(symbol, limit=twitter_limit_per_stock)
    twitter_filtered = [t for t in twitter_posts if any(k.lower() in t.lower() for k in keywords)]

    # --- News ---
    news_headlines = fetch_all_news(symbol, limit=news_limit_per_stock)
    news_filtered = [n for n in news_headlines if any(k.lower() in n.lower() for k in keywords)]

    # Combine all sources
    all_texts_per_stock[symbol].extend(reddit_filtered + twitter_filtered + news_filtered)

# ===== SENTIMENT ANALYSIS =====
structured_data = defaultdict(list)
summary_counter = Counter()

for symbol, texts in all_texts_per_stock.items():
    if not texts:
        continue

    sentiments = analyze_sentiment(texts)
    summary_counter.update(sentiments)

    for text, sentiment in zip(texts, sentiments):
        structured_data[symbol].append({
            "headline": text[:200] + ("..." if len(text) > 200 else ""),
            "full_text": text,
            "sentiment": sentiment.upper(),
            "timestamp": datetime.now().isoformat(),
            "relevance": "High" if any(k.lower() in text.lower() for k in ["earnings", "buyback", "merger", "IPO"]) else "Medium"
        })

# ===== PRINT SUMMARY =====
print("====== SENTIMENT SUMMARY =====")
print(summary_counter)

print("\n====== DETAILED PER STOCK =====")
for symbol, items in structured_data.items():
    print(f"\n=== {symbol} ===")
    for i, item in enumerate(items, 1):
        print(f"{i}. [{item['sentiment']}] {item['headline']} ({item['relevance']})")
