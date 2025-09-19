# scrapers/news.py

from scrapers.news_scraper_web import fetch_moneycontrol_news
from scrapers.yahoo_news_scraper import fetch_yahoo_news

def fetch_all_news(symbol, limit=5):
    # You can try both sources
    try:
        mc_news = fetch_moneycontrol_news(symbol, limit=limit)
    except:
        mc_news = []
    try:
        yahoo_news = fetch_yahoo_news(symbol, limit=limit)
    except:
        yahoo_news = []
    return mc_news + yahoo_news
