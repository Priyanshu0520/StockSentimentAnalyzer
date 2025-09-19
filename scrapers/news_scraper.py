import requests
from bs4 import BeautifulSoup
import yfinance as yf

# --- Yahoo Finance News ---
def fetch_yahoo_news(symbol, limit=5):
    headlines = []
    try:
        news = yf.Ticker(symbol).news
        if not news:
            return headlines

        for n in news[:limit]:
            # Safe extraction of title
            if isinstance(n, dict):
                title = n.get('title')
                if title:
                    headlines.append(title)
            elif isinstance(n, str):
                headlines.append(n)
    except Exception as e:
        print(f"Error fetching Yahoo news for {symbol}: {e}")
    return headlines[:limit]


# --- MoneyControl News ---
def fetch_moneycontrol_news(keyword, limit=5):
    headlines = []
    try:
        url = f"https://www.moneycontrol.com/news/tags/{keyword}.html"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.select('div.articleTitle a')[:limit]
        headlines = [a.get_text(strip=True) for a in articles]
    except Exception as e:
        print(f"Error fetching MoneyControl news for {keyword}: {e}")
    return headlines[:limit]


# --- Combine all sources ---
def fetch_all_news(symbol, limit=5):
    news_yahoo = fetch_yahoo_news(symbol, limit)
    news_mc = fetch_moneycontrol_news(symbol, limit)
    return news_yahoo + news_mc
