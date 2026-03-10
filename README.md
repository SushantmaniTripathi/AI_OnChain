# 📊 AI On-Chain Data Analyst Agent

An autonomous AI agent that monitors blockchain activity, detects whale movements, surfaces trending tokens, and delivers daily crypto intelligence reports — **entirely with free APIs**.

---

## ✨ Features

| Module | What it does |
|--------|-------------|
| 🐋 **Whale Tracker** | Detects large wallet movements (Etherscan + Dune) |
| 🔥 **Token Scanner** | Spots trending tokens + honeypot detection (CoinGecko + GoPlus) |
| ⛽ **Gas Analyzer** | Z-score based spike detection with cause inference |
| 🤖 **AI Report** | LLM-generated daily briefing (Groq / Llama 3 — free) |
| 🕐 **History** | SQLite-backed report archive with risk trend charts |
| ⏰ **Scheduler** | Optional daily auto-run at 08:00 UTC |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <your-repo>
cd onchain_analyst
pip install -r requirements.txt
```

### 2. Set up API keys (all free)

```bash
cp .env.example .env
# Edit .env with your keys
```

| API | Sign up | Free limit |
|-----|---------|-----------|
| **Groq** (LLM) | https://console.groq.com | 14,400 req/day |
| **Etherscan** | https://etherscan.io/apis | 100K req/day |
| **Dune Analytics** | https://dune.com/settings/api | 2,500 credits/mo |
| **Flipside Crypto** | https://flipsidecrypto.xyz/api | Unlimited (rate limited) |
| **CoinGecko** | No key needed | 30 req/min |
| **GoPlus Security** | No key needed | 20 req/sec |

### 3. Run the dashboard

```bash
streamlit run app.py
```

### 4. Or run CLI report only

```bash
python orchestrator.py
```

---

## 🏗️ Project Structure

```
onchain_analyst/
├── app.py                    # Streamlit dashboard (main UI)
├── orchestrator.py           # Coordinates all agents
├── config.py                 # API keys, thresholds, constants
├── requirements.txt
├── .env.example              # Copy to .env and fill in keys
│
├── agents/
│   ├── whale_tracker.py      # Whale wallet detection
│   ├── token_trending.py     # Token scanner + risk scoring
│   ├── gas_analyzer.py       # Gas spike detection (z-score)
│   └── report_synthesizer.py # LLM report generation (Groq)
│
├── utils/
│   ├── database.py           # SQLite cache + report storage
│   ├── http_client.py        # Cached HTTP with retry
│   └── mock_data.py          # Demo data when no API keys set
│
└── data/
    └── reports.db            # Auto-created SQLite database
```

---

## 🎭 Demo Mode

No API keys? No problem. The app runs in **Demo Mode** automatically, using realistic simulated blockchain data. You'll see the full UI and experience the complete feature set. Add API keys when ready to switch to live data.

---

## ⚙️ Configuration

Edit `config.py` to tune:

```python
WHALE_ETH_THRESHOLD     = 500        # Min ETH to flag as whale tx
GAS_SPIKE_Z_SCORE_THRESHOLD = 2.0   # Spike sensitivity
REPORT_HOUR_UTC         = 8          # Daily auto-run time
LLM_MODEL               = "llama3-8b-8192"  # Groq model
```

---

## 🔧 Customization

### Add a new chain (e.g., Solana)
1. Create `agents/solana_whale_tracker.py`
2. Use Flipside's Solana SQL tables
3. Add to `orchestrator.py` parallel execution block

### Add Telegram delivery
```python
# In orchestrator.py after save_report()
import requests
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
requests.post(TELEGRAM_URL, json={"chat_id": TELEGRAM_CHAT_ID, "text": report["summary"], "parse_mode": "Markdown"})
```

### Deploy free on Streamlit Cloud
1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo → `app.py`
4. Add secrets in Streamlit Cloud dashboard

---

## 📊 Architecture

```
Streamlit UI
     ↓
Orchestrator (orchestrator.py)
     ↓ (parallel)
┌────────────┬──────────────┬─────────────┐
│ Whale      │ Token        │ Gas         │
│ Tracker    │ Trending     │ Analyzer    │
│            │              │             │
│ Etherscan  │ CoinGecko    │ Etherscan   │
│ Dune API   │ GoPlus API   │ Dune API    │
└────────────┴──────────────┴─────────────┘
     ↓
Report Synthesizer (Groq / Llama 3)
     ↓
SQLite Cache + Report Storage
```

---

## 💡 Monetization Ideas

- **Telegram Bot** — send daily reports to paid subscribers ($5–15/mo)
- **Premium Tier** — real-time alerts for whale movements above threshold
- **API Access** — sell JSON report data to other devs
- **White-label** — customize for DAOs or trading desks

---

## 🔒 Security Notes

- Never commit your `.env` file
- API keys are loaded from environment variables only
- SQLite database is local — no user data leaves your machine
- GoPlus and CoinGecko work without authentication

---

## 📄 License

MIT — use freely, build on it, ship it.
