# 💊 Pharma Invest
### Personal Investment Intelligence Platform for Indian Pharma Stocks

> A full-stack personal investment platform built on Streamlit — combining live NSE/BSE market data, multi-model AI price forecasting, portfolio management, paper trading, and a Claude-powered investment advisor. Designed for personal use only.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Running the Apps](#running-the-apps)
- [Page-by-Page Guide](#page-by-page-guide)
- [AI Models (Forecasting Engine)](#ai-models-forecasting-engine)
- [AI Advisor (Claude Integration)](#ai-advisor-claude-integration)
- [Data Sources](#data-sources)
- [Local Data Storage](#local-data-storage)
- [Configuration & Settings](#configuration--settings)
- [Known Limitations](#known-limitations)
- [Disclaimer](#disclaimer)

---

## Overview

**Pharma Invest** is a two-file personal investment platform targeting the Indian pharmaceutical sector. It tracks all major NSE/BSE-listed pharma companies in real time, generates multi-model AI price forecasts (Prophet, GPR, MC-GBM, XGBoost, N-BEATS), and provides portfolio management with a Claude-powered AI advisor that understands your specific holdings, risk profile, and investment horizon.

This was built as a **personal research tool** — not as a SEBI-registered advisory service. All investment decisions remain the user's sole responsibility.

---

## Project Structure

```
pharma-invest/
│
├── pharma_invest_app.py        # Main investment platform (10 pages)
├── pharma_stock_tracker.py     # Forecasting engine + market tracker (v2.0)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
└── .pharma_data/               # Auto-created on first run (local persistence)
    ├── portfolio.json          # Your holdings
    ├── watchlist.json          # Watchlist + alert thresholds
    ├── paper_trades.json       # Paper trading history
    ├── paper_capital.json      # Paper trading cash balance
    └── risk_profile.json       # Your risk settings
```

---

## Features

### `pharma_invest_app.py` — Investment Platform

| Page | Description |
|---|---|
| **01 · Dashboard** | Live P&L, index strip, holdings-at-a-glance with AI signals, allocation donut, price alert notifications |
| **02 · Portfolio** | Add/remove/edit holdings, cost-basis tracking, unrealised P&L, treemap by return %, waterfall chart |
| **03 · AI Advisor** | Claude-powered chat advisor with your portfolio, P&L, risk profile, and watchlist as live context |
| **04 · Trade Desk** | Paper trading simulator — BUY/SELL at live prices, position management, trade log, P&L on close |
| **05 · Watchlist** | Track up to N stocks, set price alerts (above/below thresholds), live signal scores with reasoning |
| **06 · Market Overview** | All 26 pharma stocks live with auto-refresh, performance bar chart, live price grid |
| **07 · Stock Deep Dive** | Full quote, AI signal gauge + reasoning, candlestick with BB/MAs, RSI, MACD, return distribution |
| **08 · Risk Analyser** | Portfolio Sharpe ratio, VaR (95%), CVaR, max drawdown, correlation heatmap, limit breach alerts |
| **09 · News & Sentiment** | Google News RSS headlines with keyword-based sentiment classification per stock |
| **10 · Settings** | Risk profile (1–10 scale), capital limits, single-stock concentration limits, CSV export |

### `pharma_stock_tracker.py` — Forecasting Engine

| Feature | Description |
|---|---|
| **Live Tracker** | All pharma stocks with 60s cache, 30s auto-refresh, NSE + BSE |
| **5-Year Forecast** | 6 ML models, 80–200 Monte Carlo paths each, P10/P90 confidence bands |
| **Technical Analysis** | Candlestick + Bollinger Bands + SMA/EMA + MACD + RSI + Volume |
| **Correlation & Risk** | 2Y weekly return correlation matrix, rolling volatility, drawdown chart |
| **Fundamentals** | Valuation scorecard, peer comparison table, P/E vs P/B bubble map |
| **News & Sentiment** | Headline fetcher with sentiment scoring |

---

## Screenshots

> _Run the app locally to view the live interface. Key screens include:_
> - **Dashboard** — portfolio P&L strip + holdings table with colour-coded signals
> - **AI Advisor** — chat interface with full portfolio context
> - **Stock Deep Dive** — signal gauge + candlestick chart + reasoning bullets
> - **Trade Desk** — split BUY/SELL panel with paper P&L preview
> - **Risk Analyser** — correlation heatmap + rolling volatility chart

---

## Installation

### Prerequisites

- Python **3.9 or higher** (3.11 recommended)
- pip 23+
- Internet connection (for yfinance + news)

### Step 1 — Clone or download the project

```bash
git clone https://github.com/yourname/pharma-invest.git
cd pharma-invest
```

Or simply place both `.py` files and `requirements.txt` in a folder.

### Step 2 — Create a virtual environment (recommended)

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on Prophet:** Prophet requires a Stan backend. If the standard install fails, try:
> ```bash
> pip install pystan==2.19.1.1
> pip install prophet
> ```
> Prophet is only required for `pharma_stock_tracker.py` forecasting. The main investment app (`pharma_invest_app.py`) runs without it.

### Step 4 — (Optional) Configure Claude AI API key

The AI Advisor page calls the Anthropic Claude API directly from the browser via `https://api.anthropic.com/v1/messages`. 

When running on **Streamlit Cloud**, the API key is injected automatically via the platform's proxy. When running **locally**, you do not need an API key — the request is made without authentication headers (Claude.ai handles authentication at the infrastructure level when run through the official Streamlit deployment).

If you want to run the AI Advisor with a personal API key in a self-hosted setup, add this to your environment:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

And modify the API call in `pharma_invest_app.py` to include:
```python
headers={"Content-Type": "application/json", "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}
```

---

## Running the Apps

### Main Investment Platform

```bash
streamlit run pharma_invest_app.py
```

Opens at `http://localhost:8501`

### Forecasting & Market Tracker (standalone)

```bash
streamlit run pharma_stock_tracker.py
```

Opens at `http://localhost:8502` (or whichever port is free)

### Run both simultaneously

```bash
streamlit run pharma_invest_app.py --server.port 8501 &
streamlit run pharma_stock_tracker.py --server.port 8502 &
```

---

## Page-by-Page Guide

### 01 · Dashboard
Your command centre. Loads on startup showing:
- **Nifty Pharma / Sensex / Nifty 50** live index strip
- **Portfolio KPIs** — invested, current value, unrealised P&L, today's P&L
- **Holdings table** — each stock with CMP, return %, weight, and AI signal badge
- **Allocation donut** + estimated portfolio trend line (1Y)
- **Alert notifications** — any watchlist thresholds crossed appear here

> Click **⟳ Refresh All** to force-clear the cache and re-fetch all live prices.

### 02 · Portfolio
Add holdings by selecting a stock, entering quantity, average buy price, and date. The system:
- Detects duplicate entries and **averages the cost basis** automatically
- Shows a sortable data table with P&L, return %, weight, and signal
- Renders a **P&L waterfall chart** (sorted losers → gainers)
- Renders a **treemap** coloured by return % for instant visual allocation review

All data is persisted to `.pharma_data/portfolio.json` immediately on save.

### 03 · AI Advisor
A Claude `claude-sonnet-4-20250514` powered chat interface. On every message, the system automatically injects:
- Your full portfolio (all holdings, quantities, avg prices, current P&L, signals)
- Your watchlist
- Your risk profile (score, label, capital, horizon, max drawdown)
- Today's date

**Quick Action buttons** trigger pre-built prompts:
- Portfolio Health Check
- Buy Opportunities
- Risk Assessment
- Rebalancing Advice

Chat history persists within the session (not across restarts).

### 04 · Trade Desk
Paper trading with ₹10,00,000 virtual capital (resettable). Features:
- **BUY panel** — select stock, quantity, see live CMP + order value + AI signal before confirming
- **SELL panel** — only shows stocks you hold, displays avg cost and estimated P&L before confirming
- **Trade log** — last 30 trades with date, action, price, value, P&L on sells
- Cash balance updates in real time after each trade

### 05 · Watchlist
Add stocks with optional price alert thresholds:
- **Alert Above ₹X** — triggers when price crosses above threshold (shown in green 🔔)
- **Alert Below ₹X** — triggers when price drops below threshold (shown in red 🔔)
- Each stock shows an expandable **Signal Reasoning** section with the 5 factors driving the BUY/SELL/HOLD/WATCH call

Alerts are also surfaced on the **Dashboard** and **Sidebar**.

### 06 · Market Overview
Fetches live quotes for all 26 covered pharma companies sequentially with a progress bar. Shows:
- A horizontal **performance bar chart** (today's gainers and losers)
- A **5-column price grid** with symbol, price, day change, company name, and cap tier

Auto-refreshes every 30 seconds if `streamlit-autorefresh` is installed.

### 07 · Stock Deep Dive
Select any stock to see:
- **Hero price card** — live price, change, signal badge, sector classification
- **8 KPI tiles** — day high/low, volume, market cap, P/E, P/B, EPS, ROE
- **Signal gauge (0–100)** — with colour-coded zones and 5 reasoning bullets
- **Three chart tabs:**
  - Candlestick with Bollinger Bands, SMA20/50/200, Volume
  - RSI (14) + MACD with histogram
  - Daily return distribution with mean marker

### 08 · Risk Analyser
Computes risk metrics using 2Y weekly returns of your actual portfolio, weighted by current allocation:

| Metric | Description |
|---|---|
| Portfolio Return | Annualised geometric mean return |
| Ann. Volatility | Annualised standard deviation (√52 × weekly vol) |
| Sharpe Ratio | Return / Volatility (risk-free rate assumed 0 for simplicity) |
| Max Drawdown | Worst peak-to-trough decline in the period |
| VaR 95% (weekly) | 5th percentile of weekly return distribution |
| CVaR 95% | Expected loss in the worst 5% of weeks |

Also runs **limit checks** against your Settings thresholds and flags breaches.

### 09 · News & Sentiment
Fetches Google News RSS for the selected company. Each headline is scored using a keyword set:
- **Positive words:** gain, rise, surge, profit, growth, beat, approval, launch, patent...
- **Negative words:** fall, drop, loss, decline, miss, recall, warning, lawsuit, probe...

Displays headline count by sentiment category + donut chart.

### 10 · Settings
- **Risk Profile** — drag a 1–10 slider; label auto-updates (Conservative → Very Aggressive)
- **Capital & Limits** — set total capital, max drawdown %, max single-stock weight %
- **Paper Trading** — view current cash and total paper portfolio value
- **Export** — download your portfolio as CSV
- All settings persist to `.pharma_data/risk_profile.json`

---

## AI Models (Forecasting Engine)

Used in `pharma_stock_tracker.py`. The 5-year forecast runs 6 models:

### 1. Prophet (Meta)
Additive decomposition: `log(price) = trend + seasonality + ε`. Detects structural breakpoints automatically. Custom annual seasonality for India's February budget cycle. 150 Monte Carlo paths from residual noise. Runs in MAP mode (no MCMC) for speed.

### 2. Gaussian Process Regression (GPR)
Composite kernel: **RBF** (smooth trend) + **ExpSineSquared** (yearly cycle) + **DotProduct** (linear growth) + **WhiteKernel** (observation noise). Sparse approximation on 200 subsampled historical points to avoid O(n³) cost. Uncertainty widens correctly with horizon.

### 3. Monte Carlo Geometric Brownian Motion (MC-GBM)
Solves `dS = μS·dt + σS·dW` (Black-Scholes basis). Extended with:
- **Jump-diffusion** — ~2 Poisson jumps/year of size ~ N(0, 1.5σ)
- **Regime uncertainty** — μ and σ drawn from posterior distributions across 200 paths
- **EWMA volatility** — λ=0.94 (RiskMetrics standard) for current regime estimation

### 4. XGBoost
Gradient-boosted trees trained on 15 engineered features: momentum (5/20/60-day), realised volatility (3 windows), mean returns, price-range position, linear slope (20/60-day), last 2 returns, fraction of positive days. 80 Monte Carlo rollout paths. RobustScaler for outlier handling.

### 5. N-BEATS (Neural Basis Expansion Analysis)
Winner of the M4 forecasting competition (Oreshkin et al., 2019). Two stacks:
- **Trend stack** — polynomial basis (degree 3), doubly-residual learning
- **Seasonal stack** — Fourier basis (6 harmonics, sin + cos)

Fully vectorised in NumPy (no PyTorch/TF required). Full analytical backpropagation with Adam optimiser. 8 training epochs, 100 MC paths.

### 6. Ensemble
Inverse-variance weighted combination: 60% base weight (accuracy ranking) + 40% CI-adaptive weight (inverse of CI width at Y+5). The statistically optimal combination under model independence.

---

## AI Advisor (Claude Integration)

The AI Advisor calls `claude-sonnet-4-20250514` via the Anthropic Messages API at `https://api.anthropic.com/v1/messages`.

**System prompt injects live context:**
```
CURRENT PORTFOLIO:
  Sun Pharmaceutical: 50 shares @ ₹1,820.00, CMP ₹1,947.30, P&L +7.0%, Signal: BUY
  Cipla Ltd: 30 shares @ ₹1,510.00, CMP ₹1,488.20, P&L -1.4%, Signal: HOLD
  ...
Total: invested ₹1,89,500, current ₹2,01,240, return +6.2%

WATCHLIST: Dr. Reddy's, Biocon, Laurus Labs
Risk: Moderate (score 6/10), Capital: ₹5,00,000, Horizon: 3-5 Years, Max drawdown: 20%
```

The advisor is instructed to be specific, actionable, reference actual stock names and prices, keep responses to 200–350 words, and always flag risks.

---

## Data Sources

| Source | Data | Cache TTL |
|---|---|---|
| yfinance (NSE/BSE) | Live quotes, OHLCV history, fundamentals | Quotes: 60s · History: 15min |
| yfinance (Indices) | Nifty Pharma, Sensex, Nifty 50 | 10 min |
| Google News RSS | Headlines for sentiment | 1 hour |
| Anthropic Claude API | AI Advisor responses | No cache (live) |

> **Market hours:** NSE/BSE trade Monday–Friday, 09:15–15:30 IST. Outside hours, yfinance returns the last traded price. The live dot indicator shows the last fetch time, not a guarantee of real-time data.

---

## Local Data Storage

All user data is stored in a `.pharma_data/` directory created automatically in the same folder as the scripts. Files are plain JSON — human-readable and easily backed up.

```
.pharma_data/
├── portfolio.json      # [{ticker, name, qty, avg_price, buy_date, notes}]
├── watchlist.json      # [{ticker, name, alert_above, alert_below}]
├── paper_trades.json   # [{id, ticker, action, qty, price, date, status, pnl}]
├── paper_capital.json  # {cash, initial}
└── risk_profile.json   # {score, label, capital, horizon, max_drawdown, ...}
```

**To back up your data:**
```bash
cp -r .pharma_data/ .pharma_data_backup/
```

**To reset everything:**
```bash
rm -rf .pharma_data/
```

---

## Configuration & Settings

### Covered Pharma Companies (26 total)

| Cap Tier | Companies |
|---|---|
| **Large Cap (11)** | Sun Pharma, Dr. Reddy's, Cipla, Divi's Labs, Mankind, Torrent, Lupin, Aurobindo, Alkem, Biocon, Zydus Lifesciences |
| **Mid Cap (13)** | IPCA, Glenmark, Ajanta, Granules, Natco, Abbott India, Pfizer India, Laurus Labs, Eris, JB Chem, Piramal Pharma, Sanofi India |
| **Small Cap (2)** | Strides Pharma, Caplin Point Lab |

### Signal Engine Thresholds

The buy/sell signal engine uses the following default thresholds (not configurable via UI, but editable in `generate_signal()` in the source):

| Factor | Bullish | Bearish |
|---|---|---|
| RSI | < 30 (oversold) | > 70 (overbought) |
| MA20 vs MA50 | MA20 > MA50 | MA20 < MA50 |
| Price vs SMA200 | Price above | Price below |
| MACD | Above signal line | Below signal line |
| Bollinger | Near lower band | Above upper band |
| P/E Ratio | < 20 | > 45 |
| 52W Position | < 25% of range | > 90% of range |

**Scoring:** Base 50 → add/subtract per factor → clamp to [0,100]
- Score ≥ 65 → **BUY**
- Score ≤ 35 → **SELL**
- Score ≥ 52 → **HOLD**
- Otherwise → **WATCH**

---

## Known Limitations

1. **yfinance reliability** — yfinance scrapes Yahoo Finance and can be rate-limited or return stale data during market hours. For production use, consider the NSE official API or a paid data provider.

2. **Prophet install** — Prophet's dependency on Stan makes it tricky on some systems. If it fails to install, the forecasting engine will still run the other 5 models and produce an ensemble without it.

3. **AI Advisor without API key** — The AI Advisor requires access to the Anthropic API. Running outside of Streamlit Cloud (where the API proxy is handled) requires your own API key configured in the request headers.

4. **News sentiment is keyword-based** — The sentiment classifier uses a static word list, not a trained NLP model. It will misclassify sarcasm, complex headlines, and domain-specific phrasing. Treat it as a rough directional indicator only.

5. **Paper trading uses market price at click time** — There is no order book, bid/ask spread, or slippage simulation. Paper P&L will be optimistic vs real trading.

6. **No intraday data in portfolio** — Portfolio P&L uses daily closing prices from yfinance, not tick-level data. Intraday positions will show yesterday's close until market close.

7. **Single-sector concentration** — The app covers Indian pharma only. The Risk Analyser's sector concentration check will always flag 100% pharma exposure. This is by design.

---

## Disclaimer

> **This platform is built and intended for personal research and education only.**
>
> It is **not** a SEBI-registered Investment Advisor (IA) or Research Analyst (RA) platform. The AI signals, price forecasts, and advisor responses do **not** constitute financial advice, investment recommendations, or solicitation to buy or sell any security.
>
> All investment decisions are solely the responsibility of the user. Past performance of any model, signal, or stock does not guarantee future results. The 5-year ML forecasts carry very wide uncertainty bands — treat them as probabilistic scenarios, not targets.
>
> The developers of this software bear no liability for any financial losses incurred through use of this platform.

---

## Tech Stack

| Component | Technology |
|---|---|
| Frontend / Server | Streamlit 1.35+ |
| Market Data | yfinance 0.2.40+ |
| Data Processing | Pandas 2.0+, NumPy 1.26+ |
| Visualisation | Plotly 5.20+ |
| ML — Trees | XGBoost 2.0+ |
| ML — Gaussian | scikit-learn 1.4+ |
| ML — Forecasting | Prophet 1.1.5+ |
| Statistics | statsmodels 0.14+ |
| AI Advisor | Anthropic Claude (claude-sonnet-4-20250514) |
| News | Google News RSS via requests |
| Auto-refresh | streamlit-autorefresh 1.0.1+ |
| Storage | Local JSON files |
| Fonts | Outfit, JetBrains Mono, Playfair Display (Google Fonts) |

---

*Built with ❤️ for personal pharma investing · v3.0*
