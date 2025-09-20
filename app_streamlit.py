import streamlit as st
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import plotly.graph_objects as go
import random

st.set_page_config(page_title="AI Stock Sentiment Analyzer", layout="wide")

# ===== UPDATED CSS: Jet Black BG & "Mirrio" Animation =====
st.markdown("""
<style>
/* --- COLOR PALETTE & DESIGN SYSTEM ---
* BG-Primary: #000000 (Jet Black)
* BG-Secondary: #161b22 (Card/Component BG)
* Accent/Brand: #7c3aed (Vibrant Violet)
* Text-Primary: #f0f6fc (Bright, near-white)
...
*/

/* --- General & Background --- */
body, .stApp { 
    background: #000000 !important; 
    font-family: 'Inter', sans-serif;
    overflow: hidden; /* Hide scrollbars caused by animation */
}

/* --- *** NEW: Mirrio Background Animation *** --- */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    background: 
        radial-gradient(circle at 20% 25%, rgba(124, 58, 237, 0.25), transparent 35%),
        radial-gradient(circle at 80% 75%, rgba(34, 197, 94, 0.2), transparent 35%);
    z-index: -1;
    animation: move-glow 25s ease-in-out infinite alternate;
    will-change: transform;
}

@keyframes move-glow {
    from {
        transform: translate(-10vw, -10vh) scale(1);
        filter: blur(15px);
    }
    to {
        transform: translate(10vw, 10vh) scale(1.2);
        filter: blur(30px);
    }
}

/* --- Header, Inputs, and other styles are preserved --- */
.stApp, .block-container {
    padding: 1rem 2rem 2rem 2rem !important;
    max-width: 100vw !important;
}
.header-container {
    text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(124, 58, 237, 0.2);
}
.header-title {
    font-size: 2.8em; font-weight: 900; letter-spacing: -1.5px; color: #f0f6fc;
}
.header-subtitle { color: #8b949e; font-size: 1.1em; margin-top: -5px; }
.ticker-wrap {
    width: 100%; overflow: hidden; background-color: rgba(22, 27, 34, 0.8); /* Slightly transparent */
    backdrop-filter: blur(5px);
    border-radius: 8px; box-shadow: 0 2px 10px #00000040;
    padding: 0.6rem 0; margin-bottom: 2rem; border: 1px solid #30363d;
}
.ticker-move { display: inline-block; white-space: nowrap; animation: ticker 40s linear infinite; }
.ticker-item { display: inline-block; padding: 0 2rem; font-size: 1.1em; font-weight: 700; color: #c9d1d9; }
@keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.stTextInput>div>div>input {
    background: #161b22; color: #f0f6fc; border-radius: 10px; padding: 0.8em 1.2em;
    border: 1px solid #30363d; font-size: 17px;
}
.stTextInput>div>div>input:focus {
    border: 2px solid #7c3aed !important; 
    outline: none; box-shadow: 0 0 10px rgba(124, 58, 237, 0.5) !important;
}
.stButton>button {
    background: linear-gradient(92deg, #7c3aed, #a855f7); color: white; border-radius: 11px;
    font-size: 18px; font-weight: 700; padding: 0.8em 2.3em; 
    border: none; box-shadow: 0 0 12px rgba(124, 58, 237, 0.5);
    transition: all 0.2s ease-in-out; margin-top: 29px;
}
.stButton>button:hover { filter: brightness(1.1); transform: scale(1.03); box-shadow: 0 0 18px rgba(168, 85, 247, 0.6); }
div[role="radiogroup"] {
    display: flex; border-bottom: 2px solid #30363d; margin-bottom: 20px; gap: 15px;
}
div[role="radiogroup"] input[type="radio"] { display: none; }
div[role="radiogroup"] label {
    cursor: pointer; padding: 10px 20px; font-size: 1.1em; font-weight: 700;
    color: #8b949e; position: relative; top: 2px;
    transition: color 0.2s ease-in-out; border-bottom: 3px solid transparent;
}
div[role="radiogroup"] input[type="radio"]:checked + label {
    color: #f0f6fc; border-bottom: 3px solid #7c3aed;
}
div[role="radiogroup"] label:hover { color: #c9d1d9; }
.stock-group-header {
    font-size: 1.7em; font-weight: 800; color: #c9d1d9;
    padding-bottom: 8px; margin-top: 15px; margin-bottom: 12px;
}
.result-card {
    border-radius: 12px; background: #161b22; margin-bottom: 10px;
    padding: 14px 20px; border: 1px solid #30363d; max-width: 900px;
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.sentiment-chiklet {
    border-radius: 16px; font-weight: 700; padding: 4px 16px; font-size: 0.95em;
}
.positive { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.negative { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.neutral { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.result-source { font-size: 1em; color: #8b949e; font-weight: 600; }
.result-snippet { color: #c9d1d9; font-size: 1.1em; margin-bottom: 10px; font-weight: 400; }
.result-meta { font-size: 0.9em; color: #8b949e; opacity: 0.9; display: flex; gap: 2em; font-weight: 500; }
.result-meta b { color: #c9d1d9; }
.signal-chiklet {
    display: inline-block; background: #161b22; color: #f0f6fc; border-radius: 28px;
    margin: 0 7px 10px 0; padding: 10px 22px; font-size: 1.1em; font-weight: 800;
    box-shadow: none; border: 1.5px solid #30363d; min-width: 92px; text-align: center;
}
.signal-buy { border-color: #22c55e; }
.signal-sell { border-color: #ef4444; }
.signal-hold { border-color: #f59e0b; }
</style>
""", unsafe_allow_html=True)

# --- Data Simulation Functions (Unchanged) ---
DATA_CORPUS = [
    ("POSITIVE", "{stock} surges {percent}% after beating earnings expectations by a wide margin."),("POSITIVE", "Strong institutional buying reported in {stock} following positive analyst upgrades."),("POSITIVE", "Rumors of a potential buyback program send {stock} shares soaring."),("POSITIVE", "{stock} announces a strategic partnership with a major tech firm, boosting investor confidence."),("POSITIVE", "Upgraded to 'Overweight' by {analyst}, {stock} sees significant pre-market gains."),("POSITIVE", "New product launch for {stock} receives overwhelmingly positive early reviews."),("NEGATIVE", "{stock} plummets as quarterly revenue misses analyst forecasts."),("NEGATIVE", "Regulatory probe into {stock}'s business practices raises serious concerns among investors."),("NEGATIVE", "{stock} issues a downward revision of its full-year guidance, citing macroeconomic headwinds."),("NEGATIVE", "Key executive departure at {stock} sparks fears about the company's future direction."),("NEGATIVE", "{analyst} downgrades {stock} to 'Sell', pointing to increased competition."),("NEGATIVE", "Profit booking and technical resistance lead to a sharp correction in {stock} price."),("NEUTRAL", "{stock} trades flat as the market awaits the central bank's interest rate decision."),("NEUTRAL", "Volume for {stock} remains average with no significant news to drive price action."),("NEUTRAL", "Analysts maintain a 'Hold' rating on {stock}, citing a balanced risk-reward profile."),("NEUTRAL", "Sector-wide consolidation sees {stock} moving in a narrow range."),("NEUTRAL", "{stock} is currently range-bound, waiting for a clear catalyst."),
]
ANALYSTS = ["Goldman Sachs", "Morgan Stanley", "J.P. Morgan", "BofA Securities", "Jefferies"]
SOURCES = ["Reuters", "Bloomberg", "WSJ", "MarketWatch", "Economic Times"]
def generate_realistic_data(stocks, keywords):
    results = []; num_articles = random.randint(20, 35)
    for _ in range(num_articles):
        stock = random.choice(stocks)
        sentiment, template = random.choice(DATA_CORPUS)
        if keywords and random.random() > 0.3:
            keyword = random.choice(keywords)
            possible_templates = [t for t in DATA_CORPUS if keyword in t[1].lower()]
            if possible_templates: sentiment, template = random.choice(possible_templates)
        text = template.format(stock=stock, percent=random.randint(2, 12), analyst=random.choice(ANALYSTS))
        results.append({"stock": stock, "text": text, "sentiment": sentiment, "source": random.choice(SOURCES), "relevance": random.choice(["High", "Medium", "Low"]), "date": datetime.now() - timedelta(hours=random.randint(1, 48))})
    return results

# ======== HEADER + DYNAMIC TICKER ========
st.markdown("""
<div class='header-container'>
    <div class='header-title'>AI Market Sentiment Analyzer</div>
    <p class='header-subtitle'>Uncover market trends from real-time data</p>
</div>
<div class="ticker-wrap"><div class="ticker-move">
<div class="ticker-item">Latest: <span style='color:#f59e0b;'>Sector Rebound In Focus</span></div>
<div class="ticker-item"><span style='color:#22c55e;'>NIFTY Tests 25,000 Level</span></div>
<div class="ticker-item">Risk Watch: <span style='color:#ef4444;'>Global Inflation Data Due</span></div>
<div class="ticker-item"><span style='color:#7c3aed;'>Tech Stocks Lead Gains</span></div>
<div class="ticker-item"><span style='color:#f59e0b;'>Crude Oil Prices Stabilize</span></div>
<div class="ticker-item">Latest: <span style='color:#f59e0b;'>Sector Rebound In Focus</span></div>
<div class="ticker-item"><span style='color:#22c55e;'>NIFTY Tests 25,000 Level</span></div>
<div class="ticker-item">Risk Watch: <span style='color:#ef4444;'>Global Inflation Data Due</span></div>
<div class="ticker-item"><span style='color:#7c3aed;'>Tech Stocks Lead Gains</span></div>
<div class="ticker-item"><span style='color:#f59e0b;'>Crude Oil Prices Stabilize</span></div>
</div></div>
""", unsafe_allow_html=True)


# ===== INPUTS + BUTTON INLINE =====
st.markdown("##### 🔍 Enter Analysis Parameters")
col1, col2, col_btn = st.columns([3, 2.7, 1.3])
with col1:
    stock_symbols_input = st.text_input("Stocks or Indices", placeholder="AAPL, TSLA, INFY, NIFTY…", label_visibility="collapsed")
with col2:
    keywords_input = st.text_input("Keywords", placeholder="buyback, earnings, downgrade…", label_visibility="collapsed")
with col_btn:
    submit = st.button("✨ Analyze Market", use_container_width=True)

# ======== STATE MANAGEMENT & PROCESSING ========
if submit:
    with st.spinner('AI is scanning the market...'):
        stock_symbols = [s.strip().upper() for s in stock_symbols_input.split(",") if s.strip()] or ["AAPL", "TSLA", "INFY", "RELIANCE"]
        keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]
        st.session_state.results = generate_realistic_data(stock_symbols, keywords)
        sentiments_list = [res['sentiment'].lower() for res in st.session_state.results]
        st.session_state.summary = Counter(sentiments_list)

# ======== DISPLAY RESULTS (Checks if results exist in state) ========
if 'results' in st.session_state and st.session_state.results:
    # --- REVERTED to original two-column layout ---
    result_col, chart_col = st.columns([4, 1.8], gap="large")

    with result_col:
        st.subheader("📰 Detailed News Feed")
        tab_options = ["📈 Positive", "📉 Negative", "⚖️ Neutral"]
        selected_tab = st.radio("Select sentiment view", tab_options, horizontal=True, label_visibility="collapsed")
        sentiment_map = {"📈 Positive": "positive", "📉 Negative": "negative", "⚖️ Neutral": "neutral"}
        sentiment_key = sentiment_map[selected_tab]
        
        filtered_data = [item for item in st.session_state.results if item['sentiment'].lower() == sentiment_key]

        if not filtered_data:
            st.info(f"No {sentiment_key.capitalize()} results found for the current analysis.")
        else:
            grouped_by_stock = defaultdict(list)
            for item in filtered_data: grouped_by_stock[item['stock']].append(item)
            for stock, items in grouped_by_stock.items():
                st.markdown(f"<div class='stock-group-header'>{stock}</div>", unsafe_allow_html=True)
                for item in items:
                    st.markdown(f"""
                        <div class='result-card'><div class='card-header'>
                        <span class='result-source'>{item['source']}</span>
                        <span class='sentiment-chiklet {sentiment_key}'>{item['sentiment']}</span>
                        </div><div class='result-snippet'>{item['text']}</div><div class='result-meta'>
                        <span>Relevance: <b>{item['relevance']}</b></span>
                        <span>{item['date'].strftime('%d %b, %Y %I:%M %p')}</span>
                        </div></div>""", unsafe_allow_html=True)

    with chart_col:
        st.subheader("📊 Sentiment Mix")
        summary_counter = st.session_state.summary
        labels = ["Positive", "Negative", "Neutral"]
        values = [summary_counter["positive"], summary_counter["negative"], summary_counter["neutral"]]
        colors = ['#22c55e', '#ef4444', '#f59e0b']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors), sort=False)])
        fig_pie.update_traces(textinfo='percent+value', textfont_size=14, pull=[0.08 if v == max(values, default=0) else 0 for v in values])
        fig_pie.update_layout(margin=dict(l=4, r=4, t=4, b=4), paper_bgcolor='rgba(0,0,0,0)', font_color='#f0f6fc', height=280, 
                              legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("🪙 Trading Signals")
        signals = [("Buy", "signal-buy", summary_counter["positive"]), ("Sell", "signal-sell", summary_counter["negative"]), ("Hold", "signal-hold", summary_counter["neutral"])]
        signals.sort(key=lambda x: x[2], reverse=True)
        
        st.markdown("<div style='display:flex;flex-wrap:wrap;gap:10px;padding-top:8px;'>", unsafe_allow_html=True)
        for name, cls, count in signals:
            st.markdown(f"<span class='signal-chiklet {cls}'>{name}: {count}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)