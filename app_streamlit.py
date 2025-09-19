# app_streamlit.py

import streamlit as st
from scrapers.reddit_scraper import fetch_reddit_posts
from scrapers.news_scraper import fetch_all_news
from nlp.sentiment import analyze_sentiment
from collections import defaultdict, Counter
from datetime import datetime
import re

# ===== CUSTOM CSS =====
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #f0f0f0;
    font-family: 'Source Code Pro', monospace;
}
.stButton>button {
    background-color: #1f2937;
    color: #f0f0f0;
    border-radius: 12px;
    padding: 0.5em 1.5em;
    font-size: 18px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #3b82f6;
    color: white;
    transform: scale(1.05);
    box-shadow: 0 0 20px #3b82f6;
}
input[type=text] {
    background-color: #1f2937 !important;
    color: #f0f0f0 !important;
    border-radius: 10px;
    padding: 0.5em;
}
.sentiment-positive { color: #10b981; font-weight: bold; }
.sentiment-negative { color: #ef4444; font-weight: bold; }
.sentiment-neutral { color: #facc15; font-weight: bold; }
.expander { background-color: #1f2937; border-radius: 8px; padding: 0.5em; margin-bottom: 0.5em; }
</style>
""", unsafe_allow_html=True)

# ===== STREAMLIT UI =====
st.title("🚀 AI Stock Sentiment Aggregator")

# --- Interactive input fields ---
stock_symbols_input = st.text_input(
    "🔍 Search Stocks",
    placeholder="Type stock symbols like INFY, AAPL, TSLA..."
)
keywords_input = st.text_input(
    "🔍 Keywords",
    placeholder="earnings, buyback, IPO, dividend..."
)

limit_per_subreddit = st.number_input("Reddit posts per stock", 1, 20, 5)
news_limit_per_stock = st.number_input("News articles per stock", 1, 20, 5)

# ===== FETCH & ANALYZE BUTTON =====
if st.button("Fetch & Analyze Sentiment"):

    stock_symbols = [s.strip().upper() for s in stock_symbols_input.split(",") if s.strip()]
    keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

    all_texts_per_stock = defaultdict(list)

    # ===== FETCH DATA =====
    with st.spinner("Fetching data..."):
        for symbol in stock_symbols:
            reddit_posts = fetch_reddit_posts(symbol, limit_per_sub=limit_per_subreddit) or []
            news_headlines = fetch_all_news(symbol, limit=news_limit_per_stock) or []

            # Combine all posts (skip strict filtering)
            all_texts_per_stock[symbol].extend(reddit_posts + news_headlines)

    # ===== SENTIMENT ANALYSIS =====
    structured_data = defaultdict(list)
    summary_counter = Counter()

    for symbol, texts in all_texts_per_stock.items():
        if not texts:
            st.warning(f"No posts/news found for {symbol}")
            continue

        sentiments = analyze_sentiment(texts)
        summary_counter.update(sentiments)

        for text, sentiment in zip(texts, sentiments):
            # Highlight keywords
            highlighted_text = text
            for k in keywords:
                highlighted_text = re.sub(f"(?i)({k})", r"**\1**", highlighted_text)

            structured_data[symbol].append({
                "headline": highlighted_text[:200] + ("..." if len(highlighted_text) > 200 else ""),
                "full_text": highlighted_text,
                "sentiment": sentiment.upper(),
                "timestamp": datetime.now().isoformat(),
                "relevance": "High" if any(k in text.lower() for k in ["earnings", "buyback", "merger", "ipo"]) else "Medium"
            })

    # ===== DISPLAY RESULTS =====
    st.subheader("📈 Sentiment Summary")
    if summary_counter:
        st.write(summary_counter)
    else:
        st.info("No sentiment data found.")

    for symbol, items in structured_data.items():
        st.subheader(f"🔹 Stock: {symbol}")
        for i, item in enumerate(items, 1):
            sentiment_class = f"sentiment-{item['sentiment'].lower()}"
            with st.expander(f"{i}. {item['headline']} [{item['sentiment']}]"):
                st.markdown(f"<span class='{sentiment_class}'>{item['sentiment']}</span>", unsafe_allow_html=True)
                st.write(item['full_text'])
                st.write(f"Relevance: {item['relevance']}")
