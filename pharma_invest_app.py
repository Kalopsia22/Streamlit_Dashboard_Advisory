"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  PHARMA INVEST — Personal Investment Intelligence Platform                  ║
║  Version 3.0 · Personal Use Only                                            ║
║                                                                              ║
║  PAGES:                                                                      ║
║  01 · Dashboard          — P&L overview, portfolio health, alerts           ║
║  02 · Portfolio          — Holdings, cost basis, returns, allocation         ║
║  03 · AI Advisor         — Chat-based investment reasoning                  ║
║  04 · Trade Desk         — Paper trading + Zerodha Kite Connect ready       ║
║  05 · Watchlist          — Price alerts, tracked stocks                     ║
║  06 · Market Overview    — All pharma stocks, indices                       ║
║  07 · Stock Deep Dive    — Live quote, technicals, forecasts                ║
║  08 · Risk Analyser      — Portfolio risk, correlation, VaR                 ║
║  09 · News & Sentiment   — Headlines, sector mood                           ║
║  10 · Settings           — Risk profile, broker setup, preferences          ║
║                                                                              ║
║  Run:  streamlit run pharma_invest_app.py                                   ║
║  Deps: pip install streamlit yfinance pandas numpy plotly scikit-learn       ║
║        xgboost requests streamlit-autorefresh                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta, date
import json, os, warnings, requests, re, time, hashlib
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pharma Invest",
    page_icon="💊📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH = True
except ImportError:
    AUTOREFRESH = False

# ╔══════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS — Luxury Dark Terminal aesthetic
# ══════════════════════════════════════════════════════════════════════════════╝
BG        = "#05080F"
BG2       = "#080C17"
CARD      = "#0C1120"
CARD2     = "#101828"
BORDER    = "#1A2438"
BORDER2   = "#222E45"
TXT       = "#E8EDF8"
TXT2      = "#7A8BAA"
TXT3      = "#3A4D6A"
LIME      = "#B8FF6E"
TEAL      = "#00CFA8"
CRIMSON   = "#FF3355"
AMBER     = "#FFAA00"
SAPPHIRE  = "#3D8EFF"
LAVENDER  = "#9D7FFF"
ROSE      = "#FF6B9D"
CYAN      = "#00E5FF"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=Playfair+Display:wght@600;700&display=swap');

:root {{
  --bg:{BG}; --bg2:{BG2}; --card:{CARD}; --card2:{CARD2};
  --border:{BORDER}; --border2:{BORDER2};
  --txt:{TXT}; --txt2:{TXT2}; --txt3:{TXT3};
  --lime:{LIME}; --teal:{TEAL}; --crimson:{CRIMSON};
  --amber:{AMBER}; --sapphire:{SAPPHIRE}; --lavender:{LAVENDER};
  --rose:{ROSE}; --cyan:{CYAN};
}}

html, body, [class*="css"] {{
  font-family: 'Outfit', sans-serif !important;
  background: var(--bg) !important;
  color: var(--txt);
}}

.main {{
  background:
    radial-gradient(ellipse 120% 60% at -10% 0%, rgba(184,255,110,0.04) 0%, transparent 55%),
    radial-gradient(ellipse 80% 80% at 110% 100%, rgba(0,207,168,0.04) 0%, transparent 55%),
    {BG} !important;
  min-height: 100vh;
}}

.block-container {{ padding: 1.2rem 2.2rem 4rem; max-width: 1700px; }}

/* ── Sidebar ─────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
  background: {BG2} !important;
  border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] * {{ color: {TXT} !important; }}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {{
  font-size: 0.82rem !important; font-weight: 500;
  padding: 7px 4px; border-radius: 6px;
  transition: color 0.15s;
}}
section[data-testid="stSidebar"] .stSelectbox > div {{ border-color: {BORDER2} !important; }}

/* ── Typography ──────────────────────────────────────────────────── */
.pg-title {{
  font-family: 'Playfair Display', serif;
  font-size: 2.1rem; font-weight: 700;
  color: {TXT}; line-height: 1.1;
  letter-spacing: -0.02em;
}}
.pg-sub {{
  font-size: 0.78rem; color: {TXT2};
  letter-spacing: 0.06em; margin-top: 3px; margin-bottom: 24px;
}}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.sec-label {{
  font-size: 0.62rem; font-weight: 700;
  color: {TXT3}; letter-spacing: 0.22em;
  text-transform: uppercase;
  margin: 28px 0 12px;
  display: flex; align-items: center; gap: 10px;
}}
.sec-label::after {{
  content:''; flex:1; height:1px;
  background: linear-gradient(90deg, {BORDER2}, transparent);
}}

/* ── Cards ───────────────────────────────────────────────────────── */
.card {{
  background: {CARD};
  border: 1px solid {BORDER};
  border-radius: 14px;
  padding: 20px 22px;
  position: relative; overflow: hidden;
  transition: border-color 0.2s, transform 0.15s;
}}
.card:hover {{ border-color: {BORDER2}; transform: translateY(-1px); }}
.card-accent-lime   {{ border-top: 2px solid {LIME}; }}
.card-accent-teal   {{ border-top: 2px solid {TEAL}; }}
.card-accent-amber  {{ border-top: 2px solid {AMBER}; }}
.card-accent-crimson{{ border-top: 2px solid {CRIMSON}; }}
.card-accent-sapphire{{ border-top: 2px solid {SAPPHIRE}; }}
.card-accent-lavender{{ border-top: 2px solid {LAVENDER}; }}

/* KPI */
.kpi-val  {{ font-family:'JetBrains Mono',monospace; font-size:1.35rem; font-weight:700; color:{TXT}; line-height:1; }}
.kpi-sub  {{ font-size:0.76rem; margin-top:4px; }}
.kpi-lbl  {{ font-size:0.62rem; color:{TXT2}; text-transform:uppercase; letter-spacing:0.12em; margin-top:6px; font-weight:600; }}

/* Price */
.price-hero {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 3.4rem; font-weight: 700;
  color: {TXT}; line-height: 1;
}}
.price-change-up   {{ font-family:'JetBrains Mono',monospace; font-size:1.1rem; color:{LIME};    font-weight:700; }}
.price-change-down {{ font-family:'JetBrains Mono',monospace; font-size:1.1rem; color:{CRIMSON}; font-weight:700; }}

/* Stock row */
.stock-row {{
  display:flex; justify-content:space-between; align-items:center;
  padding: 10px 14px; border-radius: 10px;
  background: {CARD}; border: 1px solid {BORDER};
  margin-bottom: 6px; transition: border-color 0.15s, background 0.15s;
  cursor: pointer;
}}
.stock-row:hover {{ border-color: {BORDER2}; background: {CARD2}; }}

/* Signal badge */
.sig-buy  {{ display:inline-flex; align-items:center; gap:4px;
             background:rgba(184,255,110,0.12); color:{LIME};
             border:1px solid rgba(184,255,110,0.3); border-radius:8px;
             padding:3px 10px; font-size:0.72rem; font-weight:700; letter-spacing:0.05em; }}
.sig-sell {{ display:inline-flex; align-items:center; gap:4px;
             background:rgba(255,51,85,0.12); color:{CRIMSON};
             border:1px solid rgba(255,51,85,0.3); border-radius:8px;
             padding:3px 10px; font-size:0.72rem; font-weight:700; letter-spacing:0.05em; }}
.sig-hold {{ display:inline-flex; align-items:center; gap:4px;
             background:rgba(255,170,0,0.12); color:{AMBER};
             border:1px solid rgba(255,170,0,0.3); border-radius:8px;
             padding:3px 10px; font-size:0.72rem; font-weight:700; letter-spacing:0.05em; }}
.sig-watch{{ display:inline-flex; align-items:center; gap:4px;
             background:rgba(61,142,255,0.12); color:{SAPPHIRE};
             border:1px solid rgba(61,142,255,0.3); border-radius:8px;
             padding:3px 10px; font-size:0.72rem; font-weight:700; letter-spacing:0.05em; }}

/* Live dot */
.dot-live {{
  display:inline-block; width:7px; height:7px;
  background:{LIME}; border-radius:50%; margin-right:5px;
  animation: blink 2s ease-in-out infinite;
}}
@keyframes blink {{
  0%,100% {{ opacity:1; box-shadow:0 0 0 0 rgba(184,255,110,0.6); }}
  50%      {{ opacity:0.7; box-shadow:0 0 0 5px rgba(184,255,110,0); }}
}}

/* Alert pill */
.alert-pill {{
  display:inline-flex; align-items:center; gap:6px;
  padding: 6px 14px; border-radius: 20px;
  font-size:0.76rem; font-weight:600;
  background: rgba(255,170,0,0.10);
  border: 1px solid rgba(255,170,0,0.3);
  color: {AMBER}; margin: 3px;
}}

/* Chat bubble */
.chat-user {{
  background: rgba(61,142,255,0.12);
  border: 1px solid rgba(61,142,255,0.2);
  border-radius: 14px 14px 4px 14px;
  padding: 12px 16px; margin: 8px 0 8px 40px;
  font-size: 0.86rem; color: {TXT};
}}
.chat-ai {{
  background: {CARD};
  border: 1px solid {BORDER2};
  border-radius: 14px 14px 14px 4px;
  padding: 14px 18px; margin: 8px 40px 8px 0;
  font-size: 0.86rem; color: {TXT}; line-height: 1.6;
  border-left: 3px solid {LIME};
}}
.chat-meta {{ font-size:0.68rem; color:{TXT3}; margin-top:4px; }}

/* Trade form */
.trade-buy  {{ background:rgba(184,255,110,0.06); border:1px solid rgba(184,255,110,0.2); border-radius:14px; padding:20px; }}
.trade-sell {{ background:rgba(255,51,85,0.06);   border:1px solid rgba(255,51,85,0.2);   border-radius:14px; padding:20px; }}

/* Progress bar */
.prog-wrap {{ background:{BORDER}; border-radius:4px; height:6px; overflow:hidden; }}
.prog-fill  {{ height:100%; border-radius:4px; transition:width 0.4s ease; }}

/* Tag */
.tag {{
  display:inline-block; padding:2px 9px; border-radius:5px;
  font-size:0.68rem; font-weight:600; margin:2px;
  background:{CARD2}; border:1px solid {BORDER2}; color:{TXT2};
}}

/* Streamlit component overrides */
[data-testid="stPlotlyChart"] {{ background:transparent !important; }}
div[data-testid="stTabs"] button {{ color:{TXT2} !important; font-family:'Outfit',sans-serif !important; font-size:0.82rem; }}
div[data-testid="stTabs"] button[aria-selected="true"] {{ color:{LIME} !important; border-bottom-color:{LIME} !important; }}
.stButton > button {{
  background: {CARD2} !important; color: {TXT} !important;
  border: 1px solid {BORDER2} !important; border-radius: 9px !important;
  font-family: 'Outfit', sans-serif !important; font-weight: 500 !important;
  transition: all 0.15s !important;
}}
.stButton > button:hover {{
  border-color: {LIME}55 !important; background:{CARD} !important;
}}
.stTextInput > div > input, .stNumberInput > div > input {{
  background: {CARD} !important; color: {TXT} !important;
  border: 1px solid {BORDER2} !important; border-radius: 8px !important;
}}
.stSelectbox > div > div {{
  background: {CARD} !important; border-color: {BORDER2} !important;
}}
div[data-testid="metric-container"] {{
  background: {CARD} !important; border: 1px solid {BORDER} !important;
  border-radius: 12px !important; padding: 12px 16px !important;
}}
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER2}; border-radius: 2px; }}
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════
# COMPANY REGISTRY
# ══════════════════════════════════════════════════════════════════════════════╝
PHARMA = {
    "SUNPHARMA.NS"   : ("Sun Pharmaceutical",       "524715", "Large Cap", "Domestic+US Generics"),
    "DRREDDY.NS"     : ("Dr. Reddy's Laboratories", "500124", "Large Cap", "US Generics+API"),
    "CIPLA.NS"       : ("Cipla Ltd",                "500087", "Large Cap", "Domestic+Respiratory"),
    "DIVISLAB.NS"    : ("Divi's Laboratories",      "532488", "Large Cap", "API+CRAMS"),
    "MANKIND.NS"     : ("Mankind Pharma",           "543904", "Large Cap", "Domestic Branded"),
    "TORNTPHARM.NS"  : ("Torrent Pharmaceuticals",  "500420", "Large Cap", "Domestic+EU"),
    "LUPIN.NS"       : ("Lupin Ltd",                "500257", "Large Cap", "US Generics"),
    "AUROPHARMA.NS"  : ("Aurobindo Pharma",         "524804", "Large Cap", "US Generics+API"),
    "ALKEM.NS"       : ("Alkem Laboratories",       "539523", "Large Cap", "Domestic Branded"),
    "BIOCON.NS"      : ("Biocon Ltd",               "532523", "Large Cap", "Biosimilars"),
    "ZYDUSLIFE.NS"   : ("Zydus Lifesciences",       "532321", "Large Cap", "US Generics+Domestic"),
    "IPCALAB.NS"     : ("IPCA Laboratories",        "524494", "Mid Cap",   "Domestic+Malaria"),
    "GLENMARK.NS"    : ("Glenmark Pharmaceuticals", "532296", "Mid Cap",   "US Generics+NCE"),
    "AJANTPHARM.NS"  : ("Ajanta Pharma",            "532331", "Mid Cap",   "Branded Emerging Mkts"),
    "GRANULES.NS"    : ("Granules India",           "532482", "Mid Cap",   "API+Formulations"),
    "NATCOPHARM.NS"  : ("Natco Pharma",             "524816", "Mid Cap",   "Oncology Generics"),
    "ABBOTINDIA.NS"  : ("Abbott India",             "500488", "Mid Cap",   "Domestic Branded"),
    "PFIZER.NS"      : ("Pfizer India",             "500680", "Mid Cap",   "Domestic Branded"),
    "LAURUSLABS.NS"  : ("Laurus Labs",              "540222", "Mid Cap",   "API+Synthesis"),
    "ERIS.NS"        : ("Eris Lifesciences",        "540596", "Mid Cap",   "Domestic Chronic"),
    "JBCHEPHARM.NS"  : ("JB Chemicals & Pharma",   "506943", "Mid Cap",   "Domestic+Export"),
    "PIRAMALPHARM.NS": ("Piramal Pharma",           "543635", "Mid Cap",   "CRAMS+Inhalation"),
    "STRIDES.NS"     : ("Strides Pharma",           "532531", "Small Cap", "Regulated Markets"),
    "MARKSANS.NS"    : ("Marksans Pharma",          "524404", "Small Cap", "US+UK Generics"),
    "CAPLIPOINT.NS"  : ("Caplin Point Lab",         "524742", "Small Cap", "LA+Africa Markets"),
    "SEQUENT.NS"     : ("Sequent Scientific",       "512529", "Small Cap", "Vet Pharma+API"),
}

INDICES = {"^CNXPHARMA": "Nifty Pharma", "^BSESN": "Sensex", "^NSEI": "Nifty 50"}

# ╔══════════════════════════════════════════════════════════════════════════════
# LOCAL STATE — persisted in JSON files (personal use)
# ══════════════════════════════════════════════════════════════════════════════╝
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pharma_data")
os.makedirs(DATA_DIR, exist_ok=True)

def _path(name): return os.path.join(DATA_DIR, f"{name}.json")

def load_json(name, default):
    try:
        with open(_path(name)) as f: return json.load(f)
    except: return default

def save_json(name, data):
    with open(_path(name), "w") as f: json.dump(data, f, indent=2, default=str)

# ── State initialisation ──────────────────────────────────────────────────────
if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_json("portfolio", [])
    # schema: [{ticker, name, qty, avg_price, buy_date, notes}]

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json("watchlist", [])
    # schema: [{ticker, name, alert_above, alert_below, notes}]

if "paper_trades" not in st.session_state:
    st.session_state.paper_trades = load_json("paper_trades", [])
    # schema: [{id, ticker, name, action, qty, price, date, status, pnl}]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = load_json("risk_profile", {
        "score": 5, "label": "Moderate", "capital": 500000,
        "horizon": "3-5 Years", "max_drawdown": 20,
        "sector_limit": 30, "single_stock_limit": 15,
    })

if "alerts_triggered" not in st.session_state:
    st.session_state.alerts_triggered = []

if "paper_capital" not in st.session_state:
    st.session_state.paper_capital = load_json("paper_capital", {"cash": 1000000, "initial": 1000000})

# ╔══════════════════════════════════════════════════════════════════════════════
# DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════╝
@st.cache_data(ttl=60, show_spinner=False)
def get_quote(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        prev = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
        price= info.get("currentPrice")  or info.get("regularMarketPrice")
        if not price:
            h = yf.Ticker(ticker).history(period="1d", interval="5m")
            price = float(h["Close"].iloc[-1]) if not h.empty else None
        chg = (price - prev) if (price and prev) else 0
        return {
            "price": round(price,2) if price else None,
            "prev":  round(prev,2) if prev else None,
            "chg":   round(chg,2), "chg_pct": round(chg/prev*100,2) if prev else 0,
            "open":  info.get("open") or info.get("regularMarketOpen"),
            "high":  info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "low":   info.get("dayLow")  or info.get("regularMarketDayLow"),
            "vol":   info.get("volume")  or info.get("regularMarketVolume"),
            "mktcap":info.get("marketCap"),
            "pe":    info.get("trailingPE"),
            "pb":    info.get("priceToBook"),
            "eps":   info.get("trailingEps"),
            "div":   info.get("dividendYield"),
            "hi52":  info.get("fiftyTwoWeekHigh"),
            "lo52":  info.get("fiftyTwoWeekLow"),
            "avgvol":info.get("averageVolume"),
            "beta":  info.get("beta"),
            "roe":   info.get("returnOnEquity"),
            "pm":    info.get("profitMargins"),
            "rev":   info.get("totalRevenue"),
            "de":    info.get("debtToEquity"),
            "name":  info.get("longName", ticker),
            "fcf":   info.get("freeCashflow"),
            "cash":  info.get("totalCash"),
        }
    except Exception as e:
        return {"price": None, "chg_pct": 0, "chg": 0, "error": str(e)}

@st.cache_data(ttl=900, show_spinner=False)
def get_history(ticker: str, period="5y", interval="1d") -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if hasattr(df.index,"tz") and df.index.tz:
            df.index = df.index.tz_convert("UTC").tz_localize(None)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except: return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_indices() -> dict:
    out = {}
    for sym, lbl in INDICES.items():
        try:
            info  = yf.Ticker(sym).info
            price = info.get("regularMarketPrice") or info.get("currentPrice")
            prev  = info.get("previousClose") or info.get("regularMarketPreviousClose")
            pct   = (price-prev)/prev*100 if (price and prev) else 0
            out[lbl] = {"price": price, "pct": round(pct,2)}
        except: out[lbl] = {"price": None, "pct": 0}
    return out

@st.cache_data(ttl=3600, show_spinner=False)
def get_news(company: str) -> list:
    pos = {"gain","rise","surge","profit","growth","strong","beat","record","upgrade",
           "outperform","buy","positive","robust","rally","approval","launch","patent"}
    neg = {"fall","drop","loss","decline","miss","downgrade","sell","weak","concern",
           "risk","cut","negative","pressure","lawsuit","recall","warning","probe"}
    try:
        q    = company.replace(" ","+") + "+stock+pharma+India"
        url  = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        items= re.findall(r"<title>(.*?)</title>", resp.text)[2:10]
        news = []
        for t in items:
            t = re.sub(r"<[^>]+>","",t).strip()
            w = set(t.lower().split())
            p2, n2 = len(w & pos), len(w & neg)
            s = "positive" if p2>n2 else ("negative" if n2>p2 else "neutral")
            news.append({"title": t, "sentiment": s})
        return news[:6]
    except: return []

# ╔══════════════════════════════════════════════════════════════════════════════
# ANALYTICS HELPERS
# ══════════════════════════════════════════════════════════════════════════════╝
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 30: return df
    df = df.copy()
    df["SMA20"]  = df["Close"].rolling(20).mean()
    df["SMA50"]  = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()
    df["EMA20"]  = df["Close"].ewm(span=20).mean()
    bb = df["Close"].rolling(20).std()
    df["BB_hi"]  = df["SMA20"] + 2*bb
    df["BB_lo"]  = df["SMA20"] - 2*bb
    delta = df["Close"].diff()
    g = delta.clip(lower=0).rolling(14).mean()
    l = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"]    = 100 - 100/(1 + g/l.replace(0,np.nan))
    e12 = df["Close"].ewm(span=12).mean()
    e26 = df["Close"].ewm(span=26).mean()
    df["MACD"]   = e12 - e26
    df["MACDs"]  = df["MACD"].ewm(span=9).mean()
    df["MACDh"]  = df["MACD"] - df["MACDs"]
    df["ATR"]    = pd.concat([df["High"]-df["Low"],
                               (df["High"]-df["Close"].shift()).abs(),
                               (df["Low"] -df["Close"].shift()).abs()],axis=1).max(1).rolling(14).mean()
    df["OBV"]    = (np.sign(df["Close"].diff())*df["Volume"]).fillna(0).cumsum()
    df["VolMA"]  = df["Volume"].rolling(20).mean()
    return df

def generate_signal(ticker: str) -> dict:
    """Multi-factor buy/sell/hold signal with reasoning."""
    df = get_history(ticker, period="1y")
    q  = get_quote(ticker)
    if df.empty or not q.get("price"):
        return {"signal": "WATCH", "score": 50, "reasons": ["Insufficient data"]}

    di    = add_indicators(df)
    last  = di.iloc[-1]
    price = q["price"]
    reasons = []
    score   = 50  # neutral base

    # RSI signal
    rsi = last.get("RSI", 50)
    if rsi < 30:   score += 20; reasons.append(f"RSI {rsi:.0f} — Oversold (bullish)")
    elif rsi < 45: score += 10; reasons.append(f"RSI {rsi:.0f} — Below neutral")
    elif rsi > 70: score -= 20; reasons.append(f"RSI {rsi:.0f} — Overbought (bearish)")
    elif rsi > 58: score -= 8;  reasons.append(f"RSI {rsi:.0f} — Elevated")

    # MA trend
    sma20 = last.get("SMA20"); sma50 = last.get("SMA50"); sma200 = last.get("SMA200")
    if sma20 and sma50 and sma20 > sma50:
        score += 10; reasons.append("SMA20 > SMA50 — Golden cross region")
    elif sma20 and sma50:
        score -= 10; reasons.append("SMA20 < SMA50 — Bearish MA alignment")
    if price and sma200:
        if price > sma200: score += 12; reasons.append(f"Price above SMA200 — long-term uptrend")
        else:              score -= 12; reasons.append("Price below SMA200 — long-term downtrend")

    # MACD
    macd = last.get("MACD"); macds = last.get("MACDs")
    if macd and macds:
        if macd > macds: score += 8;  reasons.append("MACD above signal — momentum positive")
        else:            score -= 8;  reasons.append("MACD below signal — momentum negative")

    # Bollinger
    bb_hi = last.get("BB_hi"); bb_lo = last.get("BB_lo")
    if bb_lo and price and price < bb_lo: score += 12; reasons.append("Price below BB lower — potential reversal zone")
    if bb_hi and price and price > bb_hi: score -= 12; reasons.append("Price above BB upper — extended, caution")

    # Volume
    vol = last.get("Volume"); volma = last.get("VolMA")
    if vol and volma and vol > volma * 1.5: score += 5; reasons.append("Volume spike — strong participation")

    # Fundamentals
    pe = q.get("pe"); roe = q.get("roe"); pm = q.get("pm")
    if pe and pe < 20:  score += 8;  reasons.append(f"P/E {pe:.1f} — Attractive valuation")
    if pe and pe > 45:  score -= 8;  reasons.append(f"P/E {pe:.1f} — Premium valuation")
    if roe and roe > 0.2: score += 6; reasons.append(f"ROE {roe*100:.1f}% — High quality business")
    if pm and pm > 0.15:  score += 5; reasons.append(f"Profit margin {pm*100:.1f}% — Strong profitability")

    # 52W position
    hi52 = q.get("hi52"); lo52 = q.get("lo52")
    if hi52 and lo52 and price:
        pos = (price - lo52) / (hi52 - lo52)
        if pos < 0.25:  score += 10; reasons.append(f"Near 52W low ({pos*100:.0f}% of range) — value zone")
        if pos > 0.90:  score -= 8;  reasons.append(f"Near 52W high ({pos*100:.0f}% of range) — stretched")

    score = max(0, min(100, score))
    if score >= 65:   signal = "BUY"
    elif score <= 35: signal = "SELL"
    elif score >= 52: signal = "HOLD"
    else:             signal = "WATCH"

    return {
        "signal":  signal,
        "score":   score,
        "reasons": reasons[:5],
        "rsi":     round(rsi, 1) if rsi else None,
        "pe":      q.get("pe"),
        "roe":     q.get("roe"),
    }

def portfolio_analytics() -> dict:
    """Compute full portfolio P&L from session state holdings."""
    holdings = st.session_state.portfolio
    if not holdings:
        return {"total_invested": 0, "current_value": 0, "total_pnl": 0,
                "total_pnl_pct": 0, "rows": [], "allocation": []}
    rows = []
    total_inv = 0; total_cur = 0
    for h in holdings:
        q = get_quote(h["ticker"])
        cp = q.get("price")
        if not cp: continue
        inv = h["qty"] * h["avg_price"]
        cur = h["qty"] * cp
        pnl = cur - inv
        pnl_pct = pnl / inv * 100 if inv else 0
        day_pnl = h["qty"] * q.get("chg", 0)
        total_inv += inv; total_cur += cur
        rows.append({
            "ticker":   h["ticker"],
            "name":     h.get("name", PHARMA.get(h["ticker"],("",))[0])[:20],
            "qty":      h["qty"],
            "avg":      h["avg_price"],
            "cmp":      cp,
            "inv":      inv,
            "cur":      cur,
            "pnl":      pnl,
            "pnl_pct":  pnl_pct,
            "day_pnl":  day_pnl,
            "chg_pct":  q.get("chg_pct", 0),
            "weight":   0,  # filled below
            "signal":   None,
        })
    for r in rows:
        r["weight"] = r["cur"] / total_cur * 100 if total_cur else 0
    total_pnl = total_cur - total_inv
    return {
        "total_invested": total_inv,
        "current_value":  total_cur,
        "total_pnl":      total_pnl,
        "total_pnl_pct":  total_pnl / total_inv * 100 if total_inv else 0,
        "day_pnl":        sum(r["day_pnl"] for r in rows),
        "rows":           rows,
    }

def paper_portfolio_value() -> float:
    """Current value of paper trading portfolio."""
    cap = st.session_state.paper_capital
    holdings_val = 0
    # Aggregate open paper positions
    trades = [t for t in st.session_state.paper_trades if t.get("status") == "open"]
    pos = {}
    for t in trades:
        tk = t["ticker"]; qty = t["qty"]
        if t["action"] == "BUY":
            pos[tk] = pos.get(tk, 0) + qty
        else:
            pos[tk] = pos.get(tk, 0) - qty
    for tk, qty in pos.items():
        if qty > 0:
            q = get_quote(tk)
            if q.get("price"):
                holdings_val += qty * q["price"]
    return cap["cash"] + holdings_val

def check_alerts() -> list:
    """Check watchlist against current prices, return triggered alerts."""
    triggered = []
    for w in st.session_state.watchlist:
        q = get_quote(w["ticker"])
        p = q.get("price")
        if not p: continue
        aa = w.get("alert_above"); ab = w.get("alert_below")
        if aa and p >= aa:
            triggered.append({"ticker": w["ticker"], "type": "above",
                               "price": p, "target": aa})
        if ab and p <= ab:
            triggered.append({"ticker": w["ticker"], "type": "below",
                               "price": p, "target": ab})
    return triggered

# ╔══════════════════════════════════════════════════════════════════════════════
# CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════╝
def _rgb(h):
    h = h.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"

def theme(fig, h=400):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, sans-serif", color=TXT, size=12),
        height=h, margin=dict(t=40,b=40,l=60,r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER2),
    )
    fig.update_xaxes(gridcolor=BORDER, linecolor=BORDER2, zeroline=False)
    fig.update_yaxes(gridcolor=BORDER, linecolor=BORDER2, zeroline=False)
    return fig

def fmt(n, pre="₹"):
    if n is None: return "—"
    a = abs(n)
    s = "-" if n < 0 else ""
    if a >= 1e12: return f"{s}{pre}{a/1e12:.2f}T"
    if a >= 1e9:  return f"{s}{pre}{a/1e9:.2f}B"
    if a >= 1e7:  return f"{s}{pre}{a/1e7:.2f}Cr"
    if a >= 1e5:  return f"{s}{pre}{a/1e5:.2f}L"
    return f"{s}{pre}{a:,.2f}"

def signal_badge(sig):
    cls = {"BUY":"sig-buy","SELL":"sig-sell","HOLD":"sig-hold","WATCH":"sig-watch"}.get(sig,"sig-watch")
    ico = {"BUY":"↑","SELL":"↓","HOLD":"→","WATCH":"◉"}.get(sig,"◉")
    return f'<span class="{cls}">{ico} {sig}</span>'

# ╔══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown(f"""
    <div style='padding:20px 0 12px;'>
      <div style='font-family:Playfair Display,serif; font-size:1.3rem; font-weight:700;
                  color:{TXT}; letter-spacing:-0.01em;'>
        💊 Pharma Invest
      </div>
      <div style='font-size:0.68rem; color:{TXT3}; margin-top:3px; letter-spacing:0.12em;
                  text-transform:uppercase;'>
        Personal Investment Platform
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio("", [
        "01 · Dashboard",
        "02 · Portfolio",
        "03 · AI Advisor",
        "04 · Trade Desk",
        "05 · Watchlist",
        "06 · Market Overview",
        "07 · Stock Deep Dive",
        "08 · Risk Analyser",
        "09 · News & Sentiment",
        "10 · Settings",
    ], label_visibility="collapsed")

    st.divider()

    # Quick portfolio summary in sidebar
    pa = portfolio_analytics()
    pnl_col = LIME if pa["total_pnl"] >= 0 else CRIMSON
    arr      = "▲" if pa["total_pnl"] >= 0 else "▼"
    st.markdown(f"""
    <div style='padding:14px;background:{CARD};border:1px solid {BORDER};border-radius:12px;'>
      <div style='font-size:0.60rem;color:{TXT3};letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;'>Portfolio Summary</div>
      <div style='font-family:JetBrains Mono,monospace;font-size:1.05rem;font-weight:700;color:{TXT};'>{fmt(pa["current_value"])}</div>
      <div style='font-family:JetBrains Mono,monospace;font-size:0.80rem;color:{pnl_col};margin-top:3px;'>
        {arr} {fmt(pa["total_pnl"])} ({pa["total_pnl_pct"]:+.2f}%)
      </div>
      <div style='font-size:0.68rem;color:{TXT3};margin-top:4px;'>{len(st.session_state.portfolio)} positions · {len(st.session_state.watchlist)} on watchlist</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Alerts
    alerts = check_alerts()
    if alerts:
        st.markdown(f"<div style='font-size:0.68rem;color:{AMBER};font-weight:700;margin-bottom:6px;'>⚡ {len(alerts)} ALERT(S)</div>",
                    unsafe_allow_html=True)
        for a in alerts[:3]:
            nm = PHARMA.get(a["ticker"],("Unknown",))[0][:14]
            t  = "ABOVE" if a["type"] == "above" else "BELOW"
            st.markdown(f"<div class='alert-pill'>📍 {nm} {t} ₹{a['target']:,.0f}</div>",
                        unsafe_allow_html=True)

    st.divider()
    rp = st.session_state.risk_profile
    st.markdown(f"""
    <div style='font-size:0.68rem;color:{TXT3};line-height:1.8;'>
      <b style='color:{TXT2};'>Risk Profile</b><br>
      {rp['label']} · Score {rp['score']}/10<br>
      Capital: {fmt(rp['capital'])}<br>
      Horizon: {rp['horizon']}
    </div>
    """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════
# PAGE 01 · DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════╝
if "Dashboard" in page:
    if AUTOREFRESH:
        st_autorefresh(interval=30000, key="dash_refresh")

    now = datetime.now().strftime("%d %b %Y  %I:%M:%S %p")
    st.markdown("<h1 class='pg-title'>Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='pg-sub'><span class='dot-live'></span>{now} IST</p>", unsafe_allow_html=True)

    if st.button("⟳  Refresh All", key="dash_refresh_btn"):
        st.cache_data.clear(); st.rerun()

    st.markdown("<div class='sec-label'>MARKET INDICES</div>", unsafe_allow_html=True)
    with st.spinner(""):
        idx = get_indices()
    c1,c2,c3,c4 = st.columns(4)
    for col,(lbl,d) in zip([c1,c2,c3],idx.items()):
        p=d["price"]; pct=d["pct"]
        clr=LIME if pct>=0 else CRIMSON; arr="▲" if pct>=0 else "▼"
        with col:
            st.markdown(f"""<div class='card card-accent-{"lime" if pct>=0 else "crimson"}'>
              <div class='kpi-val'>{f"{p:,.2f}" if p else "—"}</div>
              <div class='kpi-sub' style='color:{clr};'>{arr} {abs(pct):.2f}%</div>
              <div class='kpi-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)
    with c4:
        rp2 = st.session_state.risk_profile
        st.markdown(f"""<div class='card card-accent-sapphire'>
          <div class='kpi-val'>{rp2['label']}</div>
          <div class='kpi-sub' style='color:{SAPPHIRE};'>Score {rp2['score']}/10</div>
          <div class='kpi-lbl'>Your Risk Profile</div></div>""", unsafe_allow_html=True)

    st.markdown("<div class='sec-label'>PORTFOLIO SNAPSHOT</div>", unsafe_allow_html=True)
    pa = portfolio_analytics()
    pnl_clr = LIME if pa["total_pnl"] >= 0 else CRIMSON
    day_clr = LIME if pa.get("day_pnl",0) >= 0 else CRIMSON
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(lbl,val,clr,acc) in zip([c1,c2,c3,c4,c5],[
        ("Invested",      fmt(pa["total_invested"]),  TXT,     "sapphire"),
        ("Current Value", fmt(pa["current_value"]),   TXT,     "lime"),
        ("Total P&L",     fmt(pa["total_pnl"]),       pnl_clr, "lime" if pa["total_pnl"]>=0 else "crimson"),
        ("Return",        f"{pa['total_pnl_pct']:+.2f}%", pnl_clr, "lime" if pa["total_pnl"]>=0 else "crimson"),
        ("Today's P&L",   fmt(pa.get("day_pnl",0)),  day_clr, "amber"),
    ]):
        with col:
            st.markdown(f"""<div class='card card-accent-{acc}'>
              <div class='kpi-val' style='color:{clr};font-size:1.1rem;'>{val}</div>
              <div class='kpi-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

    if pa["rows"]:
        st.markdown("<div class='sec-label'>HOLDINGS AT A GLANCE</div>", unsafe_allow_html=True)
        cols_h = st.columns([3,2,2,2,2,2])
        for h_,lbl_ in zip(cols_h,["Stock","CMP","P&L","Return","Weight","Signal"]):
            h_.markdown(f"<div style='font-size:0.65rem;color:{TXT3};font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding-bottom:6px;'>{lbl_}</div>", unsafe_allow_html=True)
        for r in sorted(pa["rows"], key=lambda x: x["pnl_pct"], reverse=True):
            clr2 = LIME if r["pnl"] >= 0 else CRIMSON
            sig = generate_signal(r["ticker"])
            c1,c2,c3,c4,c5,c6 = st.columns([3,2,2,2,2,2])
            c1.markdown(f"<div style='font-size:0.85rem;font-weight:600;'>{r['name']}</div><div style='font-size:0.68rem;color:{TXT3};font-family:JetBrains Mono,monospace;'>{r['ticker'].replace('.NS','')}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='mono' style='font-size:0.88rem;'>₹{r['cmp']:,.2f}</div><div style='font-size:0.68rem;color:{LIME if r['chg_pct']>=0 else CRIMSON};'>{'▲' if r['chg_pct']>=0 else '▼'}{abs(r['chg_pct']):.2f}%</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='mono' style='color:{clr2};font-size:0.88rem;'>{fmt(r['pnl'])}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='mono' style='color:{clr2};font-size:0.88rem;'>{r['pnl_pct']:+.2f}%</div>", unsafe_allow_html=True)
            c5.markdown(f"<div style='font-size:0.82rem;'>{r['weight']:.1f}%</div><div class='prog-wrap' style='margin-top:4px;'><div class='prog-fill' style='width:{min(r['weight']*3,100):.0f}%;background:{SAPPHIRE};'></div></div>", unsafe_allow_html=True)
            c6.markdown(signal_badge(sig["signal"]), unsafe_allow_html=True)
            st.divider()

    if pa["rows"]:
        st.markdown("<div class='sec-label'>PORTFOLIO ALLOCATION</div>", unsafe_allow_html=True)
        ca, cb = st.columns([1,2])
        with ca:
            colors_list = [LIME,SAPPHIRE,AMBER,LAVENDER,TEAL,ROSE,CYAN,CRIMSON]
            fig_d = go.Figure(go.Pie(
                labels=[r["name"] for r in pa["rows"]],
                values=[r["cur"]  for r in pa["rows"]],
                hole=0.68, textinfo="label+percent", textfont=dict(size=9),
                marker=dict(colors=colors_list[:len(pa["rows"])], line=dict(color=BG,width=2))))
            fig_d.add_annotation(text=f"<b>{fmt(pa['current_value'])}</b>",
                x=0.5,y=0.5,font=dict(size=13,color=TXT),showarrow=False)
            theme(fig_d,320)
            fig_d.update_layout(showlegend=False,margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig_d, use_container_width=True)
        with cb:
            if pa["rows"]:
                df_ph2 = get_history(pa["rows"][0]["ticker"], period="1y")
                if not df_ph2.empty:
                    fig_pv2 = go.Figure()
                    fig_pv2.add_trace(go.Scatter(
                        x=df_ph2.index,
                        y=[pa["current_value"]*(1+(df_ph2["Close"].iloc[i]/df_ph2["Close"].iloc[-1]-1)*0.5) for i in range(len(df_ph2))],
                        fill="tozeroy", fillcolor=f"rgba({_rgb(LIME)},0.06)",
                        line=dict(color=LIME,width=2), name="Portfolio Value (est.)"))
                    theme(fig_pv2,320)
                    fig_pv2.update_layout(title="Estimated Portfolio Trend (1Y)",yaxis_title="₹")
                    st.plotly_chart(fig_pv2, use_container_width=True)

    triggered_alerts = check_alerts()
    if triggered_alerts:
        st.markdown("<div class='sec-label'>PRICE ALERTS TRIGGERED</div>", unsafe_allow_html=True)
        for a in triggered_alerts:
            nm  = PHARMA.get(a["ticker"],("Unknown",))[0]
            typ = "crossed above" if a["type"] == "above" else "dropped below"
            clr3 = LIME if a["type"] == "above" else CRIMSON
            st.markdown(f"""<div class='card' style='border-left:3px solid {clr3};padding:12px 18px;margin-bottom:8px;'>
              <div style='display:flex;justify-content:space-between;'>
                <span style='font-weight:600;'>{nm}</span>
                <span style='font-family:JetBrains Mono,monospace;color:{clr3};font-size:0.88rem;font-weight:700;'>₹{a['price']:,.2f} {typ} ₹{a['target']:,.2f}</span>
              </div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 02 · PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
elif "Portfolio" in page:
    st.markdown("<h1 class='pg-title'>Portfolio</h1>", unsafe_allow_html=True)
    st.markdown("<p class='pg-sub'>Manage holdings · Track P&L · Cost basis</p>", unsafe_allow_html=True)

    with st.expander("➕  Add New Holding", expanded=len(st.session_state.portfolio)==0):
        labels2 = [f"{v[0]} ({k.replace('.NS','')})" for k,v in PHARMA.items()]
        f1,f2,f3,f4 = st.columns([3,1,2,2])
        with f1: sel2 = st.selectbox("Stock", labels2, key="add_stock")
        with f2: qty2 = st.number_input("Qty", min_value=1, value=10, key="add_qty")
        with f3: avg2 = st.number_input("Avg Buy Price (₹)", min_value=1.0, value=500.0, step=0.5, key="add_avg")
        with f4: bdate2 = st.date_input("Buy Date", value=date.today(), key="add_date")
        n_col, b_col = st.columns([3,1])
        with n_col: notes2 = st.text_input("Notes", placeholder="e.g. Q3 earnings play", key="add_notes")
        with b_col:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Add to Portfolio", use_container_width=True, key="btn_add"):
                idx2 = labels2.index(sel2); ticker2 = list(PHARMA.keys())[idx2]; name2 = PHARMA[ticker2][0]
                existing2 = next((i for i,h in enumerate(st.session_state.portfolio) if h["ticker"]==ticker2),None)
                if existing2 is not None:
                    h2 = st.session_state.portfolio[existing2]
                    total_cost2 = h2["qty"]*h2["avg_price"] + qty2*avg2
                    total_qty2  = h2["qty"] + qty2
                    h2["qty"] = total_qty2; h2["avg_price"] = total_cost2/total_qty2
                    st.success(f"Updated {name2} — new avg ₹{h2['avg_price']:,.2f}")
                else:
                    st.session_state.portfolio.append({"ticker":ticker2,"name":name2,"qty":qty2,"avg_price":avg2,"buy_date":str(bdate2),"notes":notes2})
                    st.success(f"Added {name2} × {qty2} @ ₹{avg2:,.2f}")
                save_json("portfolio", st.session_state.portfolio); st.rerun()

    pa2 = portfolio_analytics()
    if not pa2["rows"]:
        st.info("No holdings yet. Add your first position above.")
    else:
        pnl_clr2 = LIME if pa2["total_pnl"]>=0 else CRIMSON
        c1,c2,c3,c4 = st.columns(4)
        for col,(lbl,val,clr) in zip([c1,c2,c3,c4],[
            ("Total Invested",  fmt(pa2["total_invested"]),  TXT),
            ("Portfolio Value", fmt(pa2["current_value"]),   LIME),
            ("Unrealised P&L",  f"{fmt(pa2['total_pnl'])} ({pa2['total_pnl_pct']:+.1f}%)", pnl_clr2),
            ("Today's P&L",     fmt(pa2.get("day_pnl",0)),  LIME if pa2.get("day_pnl",0)>=0 else CRIMSON),
        ]):
            with col:
                st.markdown(f"""<div class='card'><div class='kpi-val' style='color:{clr};font-size:1.05rem;'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

        rows_d = []
        for r in pa2["rows"]:
            sig2 = generate_signal(r["ticker"])
            rows_d.append({"Stock":r["name"],"Symbol":r["ticker"].replace(".NS",""),"Qty":r["qty"],
                "Avg ₹":f"₹{r['avg']:,.2f}","CMP ₹":f"₹{r['cmp']:,.2f}",
                "Invested":fmt(r["inv"]),"Value":fmt(r["cur"]),"P&L":fmt(r["pnl"]),
                "Return %":f"{r['pnl_pct']:+.2f}%","Day Chg":f"{r['chg_pct']:+.2f}%",
                "Weight %":f"{r['weight']:.1f}%","Signal":sig2["signal"]})
        st.dataframe(pd.DataFrame(rows_d), use_container_width=True, hide_index=True, height=320)

        with st.expander("🗑️  Remove Holding"):
            held_lbl2 = [f"{h['name']} ({h['ticker'].replace('.NS','')})" for h in st.session_state.portfolio]
            if held_lbl2:
                to_rm = st.selectbox("Select", held_lbl2, key="remove_sel")
                if st.button("Remove", key="btn_remove"):
                    idx3 = held_lbl2.index(to_rm); removed2 = st.session_state.portfolio.pop(idx3)
                    save_json("portfolio", st.session_state.portfolio)
                    st.success(f"Removed {removed2['name']}"); st.rerun()

        ch1,ch2 = st.columns(2)
        with ch1:
            rows_s2 = sorted(pa2["rows"],key=lambda x: x["pnl"])
            fig_wf2 = go.Figure(go.Bar(y=[r["name"] for r in rows_s2],x=[r["pnl"] for r in rows_s2],
                orientation="h",marker_color=[LIME if r["pnl"]>=0 else CRIMSON for r in rows_s2],
                text=[f"{fmt(r['pnl'])} ({r['pnl_pct']:+.1f}%)" for r in rows_s2],textposition="outside"))
            theme(fig_wf2,300); fig_wf2.update_layout(title="Unrealised P&L by Stock",margin=dict(t=40,b=30,l=10,r=80))
            st.plotly_chart(fig_wf2, use_container_width=True)
        with ch2:
            fig_tm2 = go.Figure(go.Treemap(
                labels=[r["name"] for r in pa2["rows"]], values=[r["cur"] for r in pa2["rows"]],
                parents=[""]*len(pa2["rows"]), texttemplate="<b>%{label}</b><br>%{percentRoot:.1%}",
                marker=dict(colors=[r["pnl_pct"] for r in pa2["rows"]],
                    colorscale=[[0,CRIMSON],[0.5,CARD2],[1,LIME]],showscale=True),
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"))
            theme(fig_tm2,300); fig_tm2.update_layout(title="Portfolio Treemap (colour=return%)",margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig_tm2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 03 · AI ADVISOR
# ══════════════════════════════════════════════════════════════════════════════
elif "AI Advisor" in page:
    st.markdown("<h1 class='pg-title'>AI Advisor</h1>", unsafe_allow_html=True)
    st.markdown("<p class='pg-sub'>Ask anything about your pharma portfolio · Powered by Claude</p>", unsafe_allow_html=True)

    st.markdown("<div class='sec-label'>QUICK ANALYSIS</div>", unsafe_allow_html=True)
    qa1,qa2,qa3,qa4 = st.columns(4)
    qs_quick = [
        ("📊 Portfolio Health", "Analyse my current portfolio. Which holdings are performing well and which need attention? Highlight any concentration risks."),
        ("🎯 Buy Opportunities", "Which pharma stocks currently show the strongest buy signals based on technicals and fundamentals?"),
        ("⚠️ Risk Assessment", "What are the key risks in my current portfolio? Consider sector exposure and single-stock concentration."),
        ("💰 Rebalancing", "Based on my risk profile and current holdings, suggest a rebalancing strategy."),
    ]
    for col,(label,q_txt) in zip([qa1,qa2,qa3,qa4],qs_quick):
        with col:
            if st.button(label, use_container_width=True, key=f"qa_{label[:8]}"):
                st.session_state.chat_history.append({"role":"user","content":q_txt})

    st.divider()
    user_input2 = st.chat_input("Ask about your portfolio, sector trends, specific stocks...")
    if user_input2:
        st.session_state.chat_history.append({"role":"user","content":user_input2})

    pa3 = portfolio_analytics(); rp3 = st.session_state.risk_profile
    port_ctx = ""
    if pa3["rows"]:
        port_ctx = "CURRENT PORTFOLIO:\n"
        for r in pa3["rows"]:
            sg3 = generate_signal(r["ticker"])
            port_ctx += f"  {r['name']}: {r['qty']} shares @ ₹{r['avg']:,.2f}, CMP ₹{r['cmp']:,.2f}, P&L {r['pnl_pct']:+.1f}%, Signal: {sg3['signal']}\n"
        port_ctx += f"Total: invested {fmt(pa3['total_invested'])}, current {fmt(pa3['current_value'])}, return {pa3['total_pnl_pct']:+.1f}%\n"
    wl_ctx = "\nWATCHLIST: " + ", ".join([PHARMA.get(w["ticker"],("?",))[0] for w in st.session_state.watchlist[:6]]) if st.session_state.watchlist else ""

    sys_p = f"""You are an expert Indian pharma equity analyst and personal investment advisor.
Speak in clear, actionable terms. Understand SEBI, NSE/BSE, Indian pharma dynamics (US generics, domestic branded, API, CRAMS, biosimilars), technical and fundamental analysis.
{port_ctx}{wl_ctx}
Risk: {rp3['label']} (score {rp3['score']}/10), Capital: {fmt(rp3['capital'])}, Horizon: {rp3['horizon']}, Max drawdown: {rp3['max_drawdown']}%
Rules: Be specific and actionable. Reference specific stocks. 200-350 words. Use bullet points. Always flag risks. Personal use only. Today: {datetime.now().strftime('%d %b %Y')}"""

    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"]=="user":
        for msg in st.session_state.chat_history[:-1]:
            if msg["role"]=="user": st.markdown(f"<div class='chat-user'>{msg['content']}</div>",unsafe_allow_html=True)
            else: st.markdown(f"<div class='chat-ai'>{msg['content']}</div>",unsafe_allow_html=True)
        latest2 = st.session_state.chat_history[-1]["content"]
        st.markdown(f"<div class='chat-user'>{latest2}</div>",unsafe_allow_html=True)
        with st.spinner("Analysing..."):
            try:
                # Resolve API key: st.secrets → environment variable
                api_key = None
                try:
                    api_key = st.secrets["ANTHROPIC_API_KEY"]
                except Exception:
                    api_key = os.environ.get("ANTHROPIC_API_KEY")

                if not api_key:
                    ai_rep = (
                        "⚙️ API key not configured. To enable the AI Advisor:\n\n"
                        "**Option A — Streamlit secrets (recommended):**\n"
                        "Create `.streamlit/secrets.toml` in your project folder:\n"
                        "```\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```\n\n"
                        "**Option B — Environment variable before running:**\n"
                        "```\nexport ANTHROPIC_API_KEY=\"sk-ant-...\"\n```\n\n"
                        "Get your key at https://console.anthropic.com"
                    )
                else:
                    msgs3 = [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history]
                    resp3 = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "Content-Type":      "application/json",
                            "x-api-key":         api_key,
                            "anthropic-version": "2023-06-01",
                        },
                        json={"model":"claude-sonnet-4-20250514","max_tokens":1000,"system":sys_p,"messages":msgs3},
                        timeout=30,
                    )
                    d3 = resp3.json()
                    ai_rep = "".join(b.get("text","") for b in d3.get("content",[]) if b.get("type")=="text")
                    if not ai_rep:
                        ai_rep = f"Error: {d3.get('error',{}).get('message','Unknown error')}"
            except Exception as e3:
                ai_rep = f"Connection error: {e3}"
        st.session_state.chat_history.append({"role":"assistant","content":ai_rep})
        st.markdown(f"<div class='chat-ai'>{ai_rep}<div class='chat-meta'>AI Advisor · {datetime.now().strftime('%I:%M %p')}</div></div>",unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"]=="user": st.markdown(f"<div class='chat-user'>{msg['content']}</div>",unsafe_allow_html=True)
            else: st.markdown(f"<div class='chat-ai'>{msg['content']}</div>",unsafe_allow_html=True)
        if not st.session_state.chat_history:
            st.markdown(f"<div style='text-align:center;padding:60px 20px;'><div style='font-size:2rem;'>🤖</div><div style='font-size:1rem;color:{TXT2};margin-top:12px;'>Ask me about your portfolio, buy/sell signals,<br>sector trends, or specific pharma stocks.</div></div>",unsafe_allow_html=True)
    if st.session_state.chat_history:
        if st.button("Clear Chat",key="clear_chat"): st.session_state.chat_history=[]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 04 · TRADE DESK
# ══════════════════════════════════════════════════════════════════════════════
elif "Trade Desk" in page:
    st.markdown("<h1 class='pg-title'>Trade Desk</h1>", unsafe_allow_html=True)
    st.markdown("<p class='pg-sub'>Paper trading simulator · Practice strategies risk-free</p>", unsafe_allow_html=True)

    cap4 = st.session_state.paper_capital; cur_val4 = paper_portfolio_value()
    pnl_p4 = cur_val4 - cap4["initial"]
    c1,c2,c3,c4 = st.columns(4)
    for col,(lbl,val,clr) in zip([c1,c2,c3,c4],[
        ("Paper Cash",    fmt(cap4["cash"]),  LIME),
        ("Portfolio",     fmt(cur_val4),      TXT),
        ("Total P&L",     fmt(pnl_p4),        LIME if pnl_p4>=0 else CRIMSON),
        ("Return",        f"{pnl_p4/cap4['initial']*100:+.2f}%", LIME if pnl_p4>=0 else CRIMSON),
    ]):
        with col: st.markdown(f"""<div class='card'><div class='kpi-val' style='color:{clr};font-size:1.1rem;'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>""",unsafe_allow_html=True)

    st.markdown("<div class='sec-label'>PLACE PAPER ORDER</div>",unsafe_allow_html=True)
    labels4 = [f"{v[0]} ({k.replace('.NS','')})" for k,v in PHARMA.items()]
    buy_col4, sell_col4 = st.columns(2)

    with buy_col4:
        st.markdown(f"<div class='trade-buy'>",unsafe_allow_html=True)
        st.markdown(f"<div style='color:{LIME};font-weight:700;font-size:0.9rem;margin-bottom:12px;'>↑ BUY ORDER</div>",unsafe_allow_html=True)
        b_stock4 = st.selectbox("Stock",labels4,key="buy_stock4")
        b_qty4   = st.number_input("Quantity",min_value=1,value=10,key="buy_qty4")
        b_idx4   = labels4.index(b_stock4); b_tk4 = list(PHARMA.keys())[b_idx4]
        b_q4     = get_quote(b_tk4); b_price4 = b_q4.get("price",0) or 0
        b_total4 = b_price4 * b_qty4
        b_sig4   = generate_signal(b_tk4)
        st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.82rem;color:{TXT2};margin:8px 0;'>CMP: ₹{b_price4:,.2f} · Order: {fmt(b_total4)}</div>",unsafe_allow_html=True)
        st.markdown(f"Signal: {signal_badge(b_sig4['signal'])} · Score {b_sig4['score']}/100",unsafe_allow_html=True)
        if st.button("Execute BUY",use_container_width=True,key="exec_buy4"):
            if b_total4 > cap4["cash"]: st.error(f"Insufficient cash. Need {fmt(b_total4)}")
            elif b_price4 > 0:
                t4={"id":hashlib.md5(f"{b_tk4}{datetime.now()}".encode()).hexdigest()[:8],
                    "ticker":b_tk4,"name":PHARMA[b_tk4][0],"action":"BUY",
                    "qty":b_qty4,"price":b_price4,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"status":"open","pnl":0}
                st.session_state.paper_trades.append(t4); cap4["cash"]-=b_total4
                save_json("paper_trades",st.session_state.paper_trades); save_json("paper_capital",cap4)
                st.success(f"✅ BUY {b_qty4}×{PHARMA[b_tk4][0]} @ ₹{b_price4:,.2f}"); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    with sell_col4:
        st.markdown(f"<div class='trade-sell'>",unsafe_allow_html=True)
        st.markdown(f"<div style='color:{CRIMSON};font-weight:700;font-size:0.9rem;margin-bottom:12px;'>↓ SELL ORDER</div>",unsafe_allow_html=True)
        open_pos4={}
        for t4b in [tr for tr in st.session_state.paper_trades if tr.get("status")=="open"]:
            tk4b=t4b["ticker"]; open_pos4[tk4b]=open_pos4.get(tk4b,0)+(t4b["qty"] if t4b["action"]=="BUY" else -t4b["qty"])
        open_pos4={k:v for k,v in open_pos4.items() if v>0}
        if open_pos4:
            sell_lbl4=[f"{PHARMA.get(tk,('?',))[0]} ({tk.replace('.NS','')}) — {qty} shares" for tk,qty in open_pos4.items()]
            s_sel4=st.selectbox("Position",sell_lbl4,key="sell_stock4"); s_idx4=sell_lbl4.index(s_sel4)
            s_tk4=list(open_pos4.keys())[s_idx4]; s_max4=open_pos4[s_tk4]
            s_qty4=st.number_input("Quantity",min_value=1,max_value=s_max4,value=min(10,s_max4),key="sell_qty4")
            s_q4=get_quote(s_tk4); s_price4=s_q4.get("price",0) or 0
            buys4=[t for t in st.session_state.paper_trades if t["ticker"]==s_tk4 and t["action"]=="BUY" and t["status"]=="open"]
            avg_c4=np.mean([t["price"] for t in buys4]) if buys4 else 0
            t_pnl4=(s_price4-avg_c4)*s_qty4; pnl_c4=LIME if t_pnl4>=0 else CRIMSON
            st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.82rem;color:{TXT2};margin:8px 0;'>CMP: ₹{s_price4:,.2f} · Avg cost: ₹{avg_c4:,.2f}</div>",unsafe_allow_html=True)
            st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.82rem;color:{pnl_c4};'>Est P&L: {fmt(t_pnl4)}</div>",unsafe_allow_html=True)
            if st.button("Execute SELL",use_container_width=True,key="exec_sell4"):
                t4c={"id":hashlib.md5(f"{s_tk4}{datetime.now()}".encode()).hexdigest()[:8],
                     "ticker":s_tk4,"name":PHARMA.get(s_tk4,("?",))[0],"action":"SELL",
                     "qty":s_qty4,"price":s_price4,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"status":"closed","pnl":t_pnl4}
                st.session_state.paper_trades.append(t4c); cap4["cash"]+=s_price4*s_qty4
                save_json("paper_trades",st.session_state.paper_trades); save_json("paper_capital",cap4)
                st.success(f"✅ SELL {s_qty4}×{PHARMA.get(s_tk4,('',))[0]} @ ₹{s_price4:,.2f} | P&L {fmt(t_pnl4)}"); st.rerun()
        else:
            st.markdown(f"<div style='color:{TXT3};font-size:0.84rem;padding:20px 0;'>No open positions.</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    if st.session_state.paper_trades:
        st.markdown("<div class='sec-label'>TRADE LOG</div>",unsafe_allow_html=True)
        trd_rows4=[{"Date":t["date"],"Action":t["action"],"Stock":t["name"][:20],"Qty":t["qty"],
            "Price ₹":f"₹{t['price']:,.2f}","Value":fmt(t["qty"]*t["price"]),
            "P&L":fmt(t.get("pnl",0)) if t["action"]=="SELL" else "—","Status":t["status"].upper()}
            for t in reversed(st.session_state.paper_trades[-30:])]
        st.dataframe(pd.DataFrame(trd_rows4),use_container_width=True,hide_index=True,height=260)
        if st.button("Reset Paper Account (₹10L)",key="reset_paper4"):
            st.session_state.paper_trades=[]; st.session_state.paper_capital={"cash":1000000,"initial":1000000}
            save_json("paper_trades",st.session_state.paper_trades); save_json("paper_capital",st.session_state.paper_capital)
            st.success("Paper account reset to ₹10,00,000"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 05 · WATCHLIST
# ══════════════════════════════════════════════════════════════════════════════
elif "Watchlist" in page:
    st.markdown("<h1 class='pg-title'>Watchlist</h1>",unsafe_allow_html=True)
    st.markdown("<p class='pg-sub'>Track stocks · Set price alerts · Monitor signals</p>",unsafe_allow_html=True)

    with st.expander("➕  Add to Watchlist",expanded=len(st.session_state.watchlist)==0):
        labels5=[f"{v[0]} ({k.replace('.NS','')})" for k,v in PHARMA.items()]
        w1,w2,w3,w4=st.columns([3,2,2,1])
        with w1: ws5=st.selectbox("Stock",labels5,key="wl_stock5")
        with w2: wa5=st.number_input("Alert Above ₹",min_value=0.0,value=0.0,step=10.0,key="wl_above5")
        with w3: wb5=st.number_input("Alert Below ₹",min_value=0.0,value=0.0,step=10.0,key="wl_below5")
        with w4:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Add",use_container_width=True,key="wl_add5"):
                idx5=labels5.index(ws5); tk5=list(PHARMA.keys())[idx5]
                if not any(w["ticker"]==tk5 for w in st.session_state.watchlist):
                    st.session_state.watchlist.append({"ticker":tk5,"name":PHARMA[tk5][0],"alert_above":wa5 if wa5>0 else None,"alert_below":wb5 if wb5>0 else None})
                    save_json("watchlist",st.session_state.watchlist); st.success(f"Added {PHARMA[tk5][0]}"); st.rerun()
                else: st.warning("Already in watchlist")

    if not st.session_state.watchlist:
        st.info("Watchlist empty.")
    else:
        st.markdown("<div class='sec-label'>TRACKED STOCKS</div>",unsafe_allow_html=True)
        hdr5=st.columns([3,2,2,2,2,2,2,1])
        for h5,l5 in zip(hdr5,["Stock","CMP","Day %","Signal","Score","Alert ↑","Alert ↓","⊗"]):
            h5.markdown(f"<div style='font-size:0.62rem;color:{TXT3};font-weight:700;letter-spacing:0.12em;'>{l5}</div>",unsafe_allow_html=True)
        rm_idx5=None
        for i5,w5 in enumerate(st.session_state.watchlist):
            q5=get_quote(w5["ticker"]); sig5=generate_signal(w5["ticker"])
            p5=q5.get("price"); pct5=q5.get("chg_pct",0); clr5=LIME if pct5>=0 else CRIMSON
            aa5=w5.get("alert_above"); ab5=w5.get("alert_below")
            aa_act=aa5 and p5 and p5>=aa5; ab_act=ab5 and p5 and p5<=ab5
            c1,c2,c3,c4,c5,c6,c7,c8=st.columns([3,2,2,2,2,2,2,1])
            c1.markdown(f"<div style='font-size:0.86rem;font-weight:600;'>{w5['name'][:20]}</div><div style='font-size:0.68rem;color:{TXT3};font-family:JetBrains Mono,monospace;'>{w5['ticker'].replace('.NS','')}</div>",unsafe_allow_html=True)
            c2.markdown(f"<div class='mono' style='font-size:0.88rem;'>{'₹'+f'{p5:,.2f}' if p5 else '—'}</div>",unsafe_allow_html=True)
            c3.markdown(f"<div class='mono' style='color:{clr5};font-size:0.88rem;'>{'▲' if pct5>=0 else '▼'}{abs(pct5):.2f}%</div>",unsafe_allow_html=True)
            c4.markdown(signal_badge(sig5["signal"]),unsafe_allow_html=True)
            sc_clr5=LIME if sig5['score']>60 else (AMBER if sig5['score']>40 else CRIMSON)
            c5.markdown(f"<div style='font-size:0.82rem;'>{sig5['score']}/100</div><div class='prog-wrap' style='margin-top:4px;'><div class='prog-fill' style='width:{sig5['score']}%;background:{sc_clr5};'></div></div>",unsafe_allow_html=True)
            aa_c5=LIME if aa_act else TXT3; ab_c5=CRIMSON if ab_act else TXT3
            c6.markdown(f"<div style='font-size:0.80rem;color:{aa_c5};'>{'🔔 ' if aa_act else ''}{'₹'+f'{aa5:,.0f}' if aa5 else '—'}</div>",unsafe_allow_html=True)
            c7.markdown(f"<div style='font-size:0.80rem;color:{ab_c5};'>{'🔔 ' if ab_act else ''}{'₹'+f'{ab5:,.0f}' if ab5 else '—'}</div>",unsafe_allow_html=True)
            if c8.button("✕",key=f"wl_rm5_{i5}"): rm_idx5=i5
            with st.expander(f"  {w5['name'][:25]} — Reasoning"):
                for rsn5 in sig5["reasons"]:
                    rb5=LIME if any(x in rsn5.lower() for x in ["bull","positive","oversold","attractive","above","golden"]) else (CRIMSON if any(x in rsn5.lower() for x in ["bear","negative","overbought","below"]) else AMBER)
                    st.markdown(f"<div style='font-size:0.82rem;color:{rb5};padding:3px 0;border-left:2px solid {rb5};padding-left:8px;margin-bottom:4px;'>{rsn5}</div>",unsafe_allow_html=True)
            st.divider()
        if rm_idx5 is not None:
            rm5=st.session_state.watchlist.pop(rm_idx5); save_json("watchlist",st.session_state.watchlist)
            st.success(f"Removed {rm5['name']}"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 06 · MARKET OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif "Market Overview" in page:
    if AUTOREFRESH: st_autorefresh(interval=30000,key="mkt_refresh6")
    st.markdown("<h1 class='pg-title'>Market Overview</h1>",unsafe_allow_html=True)
    now6=datetime.now().strftime("%d %b %Y  %I:%M %p IST")
    st.markdown(f"<p class='pg-sub'><span class='dot-live'></span>{now6}</p>",unsafe_allow_html=True)
    if st.button("⟳ Refresh",key="mkt_rfsh6"): st.cache_data.clear(); st.rerun()

    with st.spinner(""): idx6=get_indices()
    c1,c2,c3=st.columns(3)
    for col,(lbl,d) in zip([c1,c2,c3],idx6.items()):
        p6=d["price"]; pct6=d["pct"]; clr6=LIME if pct6>=0 else CRIMSON; arr6="▲" if pct6>=0 else "▼"
        with col: st.markdown(f"""<div class='card card-accent-{"lime" if pct6>=0 else "crimson"}'><div class='kpi-val'>{f"{p6:,.2f}" if p6 else "—"}</div><div class='kpi-sub' style='color:{clr6};'>{arr6} {abs(pct6):.2f}%</div><div class='kpi-lbl'>{lbl}</div></div>""",unsafe_allow_html=True)

    st.markdown("<div class='sec-label'>ALL PHARMA STOCKS</div>",unsafe_allow_html=True)
    tks6=list(PHARMA.keys()); prog6=st.progress(0,"Loading..."); qs6={}
    for i6,tk6 in enumerate(tks6):
        qs6[tk6]=get_quote(tk6); prog6.progress((i6+1)/len(tks6))
    prog6.empty()

    rows_p6=[(PHARMA[tk][0][:18],qs6[tk].get("chg_pct",0)) for tk in tks6 if qs6[tk].get("price")]
    rows_p6.sort(key=lambda x:x[1])
    fig_p6=go.Figure(go.Bar(y=[r[0] for r in rows_p6],x=[r[1] for r in rows_p6],orientation="h",
        marker_color=[LIME if r[1]>=0 else CRIMSON for r in rows_p6],
        text=[f"{r[1]:+.2f}%" for r in rows_p6],textposition="outside"))
    theme(fig_p6,max(450,len(rows_p6)*22)); fig_p6.update_layout(title="Today's Performance",xaxis_title="Change %",margin=dict(t=40,r=80))
    st.plotly_chart(fig_p6,use_container_width=True)

    cols6=5
    for rs6 in range(0,len(tks6),cols6):
        row_tks6=tks6[rs6:rs6+cols6]; cols_row6=st.columns(cols6)
        for col6,tk6b in zip(cols_row6,row_tks6):
            nm6,_,cap6,seg6=PHARMA[tk6b]; q6b=qs6.get(tk6b,{}); p6b=q6b.get("price"); chg6b=q6b.get("chg_pct",0)
            clr6b=LIME if chg6b>=0 else CRIMSON; arr6b="▲" if chg6b>=0 else "▼"
            with col6: st.markdown(f"""<div class='card' style='padding:12px 14px;'><div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:{TXT3};letter-spacing:0.1em;'>{tk6b.replace('.NS','')}</div><div style='font-family:JetBrains Mono,monospace;font-size:1.25rem;font-weight:700;color:{TXT};margin:2px 0;'>{'₹'+f'{p6b:,.2f}' if p6b else '—'}</div><div style='font-family:JetBrains Mono,monospace;font-size:0.78rem;color:{clr6b};font-weight:700;'>{arr6b} {abs(chg6b):.2f}%</div><div style='font-size:0.66rem;color:{TXT3};margin-top:3px;'>{nm6[:18]}</div></div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 07 · STOCK DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
elif "Deep Dive" in page:
    if AUTOREFRESH: st_autorefresh(interval=30000,key="dd_refresh7")
    labels7=[f"{v[0]} ({k.replace('.NS','')})" for k,v in PHARMA.items()]
    sel_lbl7=st.selectbox("Select Stock",labels7,key="dd_stock7")
    sel_idx7=labels7.index(sel_lbl7); sel_tk7=list(PHARMA.keys())[sel_idx7]; sel_nm7=PHARMA[sel_tk7][0]
    if st.button("⟳ Refresh",key="dd_rfsh7"): st.cache_data.clear(); st.rerun()

    with st.spinner(""): q7=get_quote(sel_tk7); sig7=generate_signal(sel_tk7)
    p7=q7.get("price"); chg7=q7.get("chg_pct",0); chga7=q7.get("chg",0)
    clr7=LIME if chg7>=0 else CRIMSON; arr7="▲" if chg7>=0 else "▼"

    st.markdown(f"""<div class='card' style='padding:28px 36px;margin-bottom:20px;'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;'>
        <div>
          <div style='font-family:Playfair Display,serif;font-size:1.5rem;font-weight:700;color:{TXT};'>{sel_nm7}</div>
          <div style='font-size:0.72rem;color:{TXT3};font-family:JetBrains Mono,monospace;letter-spacing:0.12em;margin-top:3px;'><span class='dot-live'></span>{sel_tk7} · {PHARMA[sel_tk7][2]} · {PHARMA[sel_tk7][3]}</div>
        </div>
        <div style='text-align:right;'>
          <div class='price-hero'>₹{f"{p7:,.2f}" if p7 else "—"}</div>
          <div class='price-change-{"up" if chg7>=0 else "down"}' style='margin-top:6px;'>{arr7} ₹{abs(chga7):.2f} ({abs(chg7):.2f}%)</div>
          <div style='margin-top:8px;'>{signal_badge(sig7["signal"])}</div>
        </div>
      </div></div>""",unsafe_allow_html=True)

    kpis7=[("Day High",f"₹{q7.get('high') or '—'}"),("Day Low",f"₹{q7.get('low') or '—'}"),
           ("Volume",fmt(q7.get("vol"),"") or "—"),("Market Cap",fmt(q7.get("mktcap"))),
           ("P/E",f"{q7.get('pe'):.1f}" if q7.get("pe") else "—"),("P/B",f"{q7.get('pb'):.1f}" if q7.get("pb") else "—"),
           ("EPS",f"₹{q7.get('eps'):.2f}" if q7.get("eps") else "—"),("ROE",f"{q7.get('roe')*100:.1f}%" if q7.get("roe") else "—")]
    cols7=st.columns(8)
    for col7,(lbl7,val7) in zip(cols7,kpis7):
        with col7: st.markdown(f"""<div class='card' style='padding:12px 14px;text-align:center;'><div class='kpi-val' style='font-size:0.92rem;'>{val7}</div><div class='kpi-lbl'>{lbl7}</div></div>""",unsafe_allow_html=True)

    st.markdown("<div class='sec-label'>AI SIGNAL</div>",unsafe_allow_html=True)
    sc1_7,sc2_7=st.columns([1,2])
    with sc1_7:
        sc7=sig7["score"]; sc_clr7=LIME if sc7>=65 else (CRIMSON if sc7<=35 else AMBER)
        fig_g7=go.Figure(go.Indicator(mode="gauge+number",value=sc7,
            gauge=dict(axis=dict(range=[0,100],tickcolor=TXT3),bar=dict(color=sc_clr7),bgcolor=CARD2,
                steps=[dict(range=[0,35],color=f"rgba({_rgb(CRIMSON)},0.15)"),dict(range=[35,65],color=f"rgba({_rgb(AMBER)},0.10)"),dict(range=[65,100],color=f"rgba({_rgb(LIME)},0.15)")],
                threshold=dict(line=dict(color=sc_clr7,width=3),value=sc7)),
            number=dict(font=dict(size=32,color=sc_clr7,family="JetBrains Mono")),
            title=dict(text=f"<b>{sig7['signal']}</b>",font=dict(size=16,color=TXT))))
        theme(fig_g7,240); fig_g7.update_layout(margin=dict(t=20,b=10,l=20,r=20))
        st.plotly_chart(fig_g7,use_container_width=True)
    with sc2_7:
        st.markdown("<br>",unsafe_allow_html=True)
        for rsn7 in sig7["reasons"]:
            is_b7=any(w in rsn7.lower() for w in ["bull","positive","oversold","attractive","above","golden","spike"])
            rc7=LIME if is_b7 else (CRIMSON if any(w in rsn7.lower() for w in ["bear","negative","overbought","below","extended"]) else AMBER)
            st.markdown(f"<div style='padding:6px 12px;margin-bottom:5px;border-left:2px solid {rc7};font-size:0.84rem;color:{TXT};background:{CARD};border-radius:0 8px 8px 0;'>{rsn7}</div>",unsafe_allow_html=True)

    st.markdown("<div class='sec-label'>PRICE CHART</div>",unsafe_allow_html=True)
    period7=st.radio("",["3mo","6mo","1y","2y","5y"],horizontal=True,index=2,key="dd_period7")
    with st.spinner(""): dfh7=get_history(sel_tk7,period=period7)
    if not dfh7.empty:
        di7=add_indicators(dfh7)
        t1_7,t2_7,t3_7=st.tabs(["Candlestick","RSI & MACD","Returns"])
        with t1_7:
            fig_c7=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[0.75,0.25],vertical_spacing=0.04)
            fig_c7.add_trace(go.Candlestick(x=di7.index,open=di7["Open"],high=di7["High"],low=di7["Low"],close=di7["Close"],
                increasing_line_color=LIME,decreasing_line_color=CRIMSON,name="Price"),row=1,col=1)
            if "BB_hi" in di7:
                fig_c7.add_trace(go.Scatter(x=di7.index,y=di7["BB_hi"],line=dict(color=f"rgba({_rgb(AMBER)},0.35)",width=1),showlegend=False),row=1,col=1)
                fig_c7.add_trace(go.Scatter(x=di7.index,y=di7["BB_lo"],line=dict(color=f"rgba({_rgb(AMBER)},0.35)",width=1),fill="tonexty",fillcolor=f"rgba({_rgb(AMBER)},0.04)",showlegend=False),row=1,col=1)
            for ma7,c7m,w7m in [("SMA20",SAPPHIRE,1.2),("SMA50",AMBER,1.2),("SMA200",LAVENDER,1.5)]:
                if ma7 in di7: fig_c7.add_trace(go.Scatter(x=di7.index,y=di7[ma7],line=dict(color=c7m,width=w7m),name=ma7),row=1,col=1)
            vc7=[LIME if di7["Close"].iloc[i]>=di7["Open"].iloc[i] else CRIMSON for i in range(len(di7))]
            fig_c7.add_trace(go.Bar(x=di7.index,y=di7["Volume"],marker_color=vc7,showlegend=False,opacity=0.6),row=2,col=1)
            theme(fig_c7,660); fig_c7.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_c7,use_container_width=True)
        with t2_7:
            if "RSI" in di7:
                fig_rm7=make_subplots(rows=2,cols=1,shared_xaxes=True,subplot_titles=["RSI (14)","MACD"],vertical_spacing=0.1)
                fig_rm7.add_trace(go.Scatter(x=di7.index,y=di7["RSI"],line=dict(color=CYAN,width=2)),row=1,col=1)
                fig_rm7.add_hrect(y0=70,y1=100,fillcolor=f"rgba({_rgb(CRIMSON)},0.06)",line_width=0,row=1,col=1)
                fig_rm7.add_hrect(y0=0,y1=30,fillcolor=f"rgba({_rgb(LIME)},0.06)",line_width=0,row=1,col=1)
                ch7=[LIME if v>=0 else CRIMSON for v in di7["MACDh"].fillna(0)]
                fig_rm7.add_trace(go.Bar(x=di7.index,y=di7["MACDh"],marker_color=ch7,showlegend=False),row=2,col=1)
                fig_rm7.add_trace(go.Scatter(x=di7.index,y=di7["MACD"],line=dict(color=SAPPHIRE,width=1.5),name="MACD"),row=2,col=1)
                fig_rm7.add_trace(go.Scatter(x=di7.index,y=di7["MACDs"],line=dict(color=AMBER,width=1.5),name="Signal"),row=2,col=1)
                theme(fig_rm7,480); st.plotly_chart(fig_rm7,use_container_width=True)
        with t3_7:
            rets7=dfh7["Close"].pct_change().dropna()*100
            fig_r7=go.Figure(); fig_r7.add_trace(go.Histogram(x=rets7,nbinsx=80,marker_color=TEAL,opacity=0.75))
            fig_r7.add_vline(x=rets7.mean(),line_dash="dash",line_color=AMBER,annotation_text=f"μ={rets7.mean():.2f}%")
            theme(fig_r7,320); fig_r7.update_layout(title=f"Daily Return Distribution σ={rets7.std():.2f}%",xaxis_title="Daily Return %")
            st.plotly_chart(fig_r7,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 08 · RISK ANALYSER
# ══════════════════════════════════════════════════════════════════════════════
elif "Risk" in page:
    st.markdown("<h1 class='pg-title'>Risk Analyser</h1>",unsafe_allow_html=True)
    st.markdown("<p class='pg-sub'>Portfolio risk metrics · VaR · Correlation · Drawdown</p>",unsafe_allow_html=True)
    pa8=portfolio_analytics(); rp8=st.session_state.risk_profile
    if not pa8["rows"]: st.info("Add holdings first."); st.stop()
    tks8=[r["ticker"] for r in pa8["rows"]]; weights8=np.array([r["weight"]/100 for r in pa8["rows"]])
    hist8={}
    for tk8b in tks8:
        h8=get_history(tk8b,period="2y")
        if not h8.empty: hist8[tk8b]=h8["Close"].resample("W").last()
    st.markdown("<div class='sec-label'>PORTFOLIO RISK METRICS</div>",unsafe_allow_html=True)
    if len(hist8)>=2:
        df8=pd.DataFrame(hist8).dropna(); rets8=df8.pct_change().dropna()
        valid_tks8=[tk for tk in tks8 if tk in rets8.columns]
        w8=np.array([weights8[i] for i,tk in enumerate(tks8) if tk in rets8.columns]); w8/=w8.sum()
        pr8=rets8[valid_tks8]@w8
        av8=pr8.std()*np.sqrt(52); ar8=(1+pr8.mean())**52-1; sh8=ar8/av8 if av8>0 else 0
        pc8=(1+pr8).cumprod(); md8=((pc8/pc8.cummax())-1).min()
        var8=np.percentile(pr8,5); cvar8=pr8[pr8<=var8].mean()
        c1,c2,c3,c4,c5,c6=st.columns(6)
        for col,(lbl,val,clr) in zip([c1,c2,c3,c4,c5,c6],[
            ("Portfolio Return",f"{ar8*100:.1f}%",LIME if ar8>0 else CRIMSON),
            ("Ann. Volatility",f"{av8*100:.1f}%",AMBER),
            ("Sharpe Ratio",f"{sh8:.2f}",LIME if sh8>1 else (AMBER if sh8>0.5 else CRIMSON)),
            ("Max Drawdown",f"{md8*100:.1f}%",CRIMSON),
            ("VaR 95% (wk)",f"{var8*100:.2f}%",CRIMSON),
            ("CVaR 95%",f"{cvar8*100:.2f}%",CRIMSON),
        ]):
            with col: st.markdown(f"""<div class='card'><div class='kpi-val' style='color:{clr};font-size:1.0rem;'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>""",unsafe_allow_html=True)

        st.markdown("<div class='sec-label'>RISK LIMIT CHECKS</div>",unsafe_allow_html=True)
        checks8=[]
        for r8 in pa8["rows"]:
            if r8["weight"]>rp8["single_stock_limit"]: checks8.append({"type":"warn","msg":f"{r8['name'][:20]}: {r8['weight']:.1f}% exceeds {rp8['single_stock_limit']}% limit"})
        if abs(md8*100)>rp8["max_drawdown"]: checks8.append({"type":"alert","msg":f"Max drawdown {md8*100:.1f}% exceeds your {rp8['max_drawdown']}% limit"})
        if sh8<0.5: checks8.append({"type":"warn","msg":f"Sharpe {sh8:.2f} below 0.5 — poor risk-adjusted return"})
        if not checks8: st.success("✅ All risk limits within bounds")
        for c8b in checks8:
            ic8={"warn":"⚠️","alert":"🚨","info":"ℹ️"}[c8b["type"]]; clr8={"warn":AMBER,"alert":CRIMSON,"info":SAPPHIRE}[c8b["type"]]
            st.markdown(f"<div style='padding:10px 16px;margin:4px 0;border-left:3px solid {clr8};background:{CARD};border-radius:0 8px 8px 0;font-size:0.84rem;'>{ic8} {c8b['msg']}</div>",unsafe_allow_html=True)

        st.markdown("<div class='sec-label'>CORRELATION MATRIX</div>",unsafe_allow_html=True)
        corr8=rets8.corr().round(2); nm8=[PHARMA.get(tk,("",))[0][:14] for tk in corr8.columns]
        fig_cr8=go.Figure(go.Heatmap(z=corr8.values,x=nm8,y=nm8,
            colorscale=[[0,CRIMSON],[0.5,CARD2],[1,LIME]],zmin=-1,zmax=1,
            text=corr8.values,texttemplate="%{text:.2f}",textfont=dict(size=9)))
        theme(fig_cr8,500); fig_cr8.update_layout(title="Weekly Return Correlation",margin=dict(t=50,b=80,l=130,r=20),xaxis=dict(tickangle=-35))
        st.plotly_chart(fig_cr8,use_container_width=True)

        rv8=pr8.rolling(12).std()*np.sqrt(52)*100
        fig_rv8=go.Figure(); fig_rv8.add_trace(go.Scatter(x=rv8.index,y=rv8,fill="tozeroy",fillcolor=f"rgba({_rgb(AMBER)},0.08)",line=dict(color=AMBER,width=2)))
        theme(fig_rv8,260); fig_rv8.update_layout(title="12-Week Rolling Portfolio Volatility (Ann. %)",yaxis_title="Vol %")
        st.plotly_chart(fig_rv8,use_container_width=True)
    else:
        st.info("Need ≥2 holdings with 2Y history.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 09 · NEWS & SENTIMENT
# ══════════════════════════════════════════════════════════════════════════════
elif "News" in page:
    st.markdown("<h1 class='pg-title'>News & Sentiment</h1>",unsafe_allow_html=True)
    labels9=[f"{v[0]} ({k.replace('.NS','')})" for k,v in PHARMA.items()]
    sel9=st.selectbox("Company",labels9,key="news9")
    sel_tk9=list(PHARMA.keys())[labels9.index(sel9)]; sel_nm9=PHARMA[sel_tk9][0]
    with st.spinner(""): news9=get_news(sel_nm9)
    if news9:
        pos9=sum(1 for n in news9 if n["sentiment"]=="positive"); neg9=sum(1 for n in news9 if n["sentiment"]=="negative"); neu9=len(news9)-pos9-neg9
        overall9="Bullish" if pos9>neg9 else ("Bearish" if neg9>pos9 else "Neutral"); oclr9=LIME if overall9=="Bullish" else (CRIMSON if overall9=="Bearish" else AMBER)
        c1,c2,c3,c4=st.columns(4)
        for col,(lbl,val,clr) in zip([c1,c2,c3,c4],[("Sentiment",overall9,oclr9),("Positive",str(pos9),LIME),("Negative",str(neg9),CRIMSON),("Neutral",str(neu9),AMBER)]):
            with col: st.markdown(f"""<div class='card'><div class='kpi-val' style='color:{clr};font-size:1.0rem;'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>""",unsafe_allow_html=True)
        st.markdown("<div class='sec-label'>HEADLINES</div>",unsafe_allow_html=True)
        for item9 in news9:
            s9=item9["sentiment"]; clr9=LIME if s9=="positive" else (CRIMSON if s9=="negative" else AMBER); lbl9="↑ Positive" if s9=="positive" else ("↓ Negative" if s9=="negative" else "→ Neutral")
            st.markdown(f"""<div class='card' style='margin-bottom:8px;border-left:3px solid {clr9};'><div style='display:flex;justify-content:space-between;align-items:center;gap:16px;'><div style='font-size:0.85rem;color:{TXT};line-height:1.5;flex:1;'>{item9['title']}</div><div style='font-size:0.72rem;font-weight:700;color:{clr9};white-space:nowrap;'>{lbl9}</div></div></div>""",unsafe_allow_html=True)
    else: st.warning("No news available.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 10 · SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif "Settings" in page:
    st.markdown("<h1 class='pg-title'>Settings</h1>",unsafe_allow_html=True)
    rp10=st.session_state.risk_profile
    t1_10,t2_10,t3_10=st.tabs(["Risk Profile","Capital & Limits","About"])
    with t1_10:
        st.markdown("<div class='sec-label'>RISK TOLERANCE</div>",unsafe_allow_html=True)
        r_score10=st.slider("Risk Tolerance (1=Very Conservative · 10=Aggressive)",1,10,rp10["score"],key="rp_score10")
        horizon10=st.select_slider("Horizon",options=["< 1 Year","1-2 Years","2-3 Years","3-5 Years","5-10 Years","10+ Years"],value=rp10.get("horizon","3-5 Years"),key="rp_horizon10")
        lmap10={(1,3):"Conservative",(4,5):"Moderate Conservative",(6,7):"Moderate",(8,9):"Aggressive",(10,10):"Very Aggressive"}
        label10=next(v for (lo,hi),v in lmap10.items() if lo<=r_score10<=hi)
        _clr_map10={"Conservative":SAPPHIRE,"Moderate Conservative":CYAN,"Moderate":LIME,"Aggressive":AMBER,"Very Aggressive":CRIMSON}
        clr10=_clr_map10.get(label10,LIME)
        st.markdown(f"""<div class='card' style='text-align:center;padding:24px;margin:16px 0;'><div style='font-family:Playfair Display,serif;font-size:1.6rem;font-weight:700;color:{clr10};'>{label10}</div><div style='font-size:0.78rem;color:{TXT3};margin-top:6px;'>Score {r_score10}/10 · Horizon {horizon10}</div></div>""",unsafe_allow_html=True)
        if st.button("Save Risk Profile",key="save_rp10"):
            rp10.update({"score":r_score10,"label":label10,"horizon":horizon10})
            st.session_state.risk_profile=rp10; save_json("risk_profile",rp10); st.success("Saved!")
    with t2_10:
        st.markdown("<div class='sec-label'>CAPITAL & LIMITS</div>",unsafe_allow_html=True)
        cap10=st.number_input("Total Capital (₹)",min_value=10000,max_value=100000000,value=rp10.get("capital",500000),step=10000,key="rp_cap10")
        mdd10=st.slider("Max Drawdown (%)",5,50,rp10.get("max_drawdown",20),key="rp_mdd10")
        stk10=st.slider("Max Single Stock (%)",5,50,rp10.get("single_stock_limit",15),key="rp_stk10")
        if st.button("Save",key="save_lim10"):
            rp10.update({"capital":cap10,"max_drawdown":mdd10,"single_stock_limit":stk10})
            st.session_state.risk_profile=rp10; save_json("risk_profile",rp10); st.success("Saved!")
        st.markdown("<div class='sec-label'>PAPER TRADING</div>",unsafe_allow_html=True)
        pc10=st.session_state.paper_capital
        st.markdown(f"""<div class='card'><div style='display:flex;gap:32px;'><div><div class='kpi-val'>{fmt(pc10['cash'])}</div><div class='kpi-lbl'>Cash</div></div><div><div class='kpi-val'>{fmt(paper_portfolio_value())}</div><div class='kpi-lbl'>Total Value</div></div></div></div>""",unsafe_allow_html=True)
    with t3_10:
        st.markdown(f"""<div class='card' style='padding:28px;'><div style='font-family:Playfair Display,serif;font-size:1.3rem;font-weight:700;color:{TXT};margin-bottom:12px;'>💊 Pharma Invest v3.0</div><div style='font-size:0.84rem;color:{TXT2};line-height:1.8;'>Personal investment intelligence platform for Indian pharma stocks.<br><br><b style='color:{TXT};'>Stack:</b> Streamlit · yfinance · Plotly · Claude AI<br><b style='color:{TXT};'>Storage:</b> Local JSON in <code>.pharma_data/</code><br><br><b style='color:{CRIMSON};'>⚠️ Personal research tool only. Not SEBI-registered. All decisions are your own responsibility.</b></div></div>""",unsafe_allow_html=True)
        st.markdown("<div class='sec-label'>DATA</div>",unsafe_allow_html=True)
        c1_10,c2_10=st.columns(2)
        with c1_10:
            if st.button("Export Portfolio CSV",use_container_width=True):
                pa_ex=portfolio_analytics()
                if pa_ex["rows"]: csv_ex=pd.DataFrame(pa_ex["rows"]).to_csv(index=False); st.download_button("Download",csv_ex,"portfolio.csv","text/csv")
                else: st.warning("No data")
        with c2_10:
            if st.button("Clear Cache",use_container_width=True): st.cache_data.clear(); st.success("Cache cleared")
