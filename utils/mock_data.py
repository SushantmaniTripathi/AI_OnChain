"""
utils/mock_data.py — Realistic demo data when API keys are not configured.
Lets users explore the full UI without signing up for APIs.
"""
import random
from datetime import datetime, timedelta


def mock_whale_data():
    wallets = [
        {"label": "Jump Trading", "address": "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"},
        {"label": "Alameda (Remnant)", "address": "0x477573f212A7bdD5F7C12889bd1ad0aA44fb82aa"},
        {"label": "Unknown Whale", "address": "0x" + "a1b2c3d4e5f6" * 3 + "a1b2"},
        {"label": "DeFi Fund Alpha", "address": "0x" + "deadbeef1234" * 3 + "dead"},
        {"label": "Unknown Whale", "address": "0x" + "cafe1234abcd" * 3 + "cafe"},
    ]
    movements = []
    for i in range(random.randint(4, 7)):
        w = random.choice(wallets)
        eth_val = round(random.uniform(200, 15000), 2)
        movements.append({
            "wallet":     w["address"],
            "label":      w["label"],
            "value_eth":  eth_val,
            "value_usd":  round(eth_val * 3250, 0),
            "direction":  random.choice(["IN", "OUT", "IN", "IN"]),
            "token":      random.choice(["ETH", "USDC", "WBTC", "ETH", "ETH"]),
            "tx_hash":    "0x" + "".join(random.choices("abcdef0123456789", k=64)),
            "timestamp":  (datetime.utcnow() - timedelta(hours=random.randint(1, 22))).isoformat(),
        })
    return {
        "movements":        movements,
        "total_volume_usd": sum(m["value_usd"] for m in movements),
        "net_flow":         random.choice(["ACCUMULATION", "DISTRIBUTION", "MIXED"]),
        "unique_whales":    len(set(m["wallet"] for m in movements)),
    }


def mock_token_data():
    tokens = [
        {"symbol": "PEPE2", "name": "Pepe 2.0",         "chain": "ethereum", "age_h": 6,  "risk": "MEDIUM"},
        {"symbol": "DOGE3",  "name": "DogeBase",         "chain": "base",     "age_h": 18, "risk": "HIGH"},
        {"symbol": "AIDOG",  "name": "AI Doge",          "chain": "ethereum", "age_h": 31, "risk": "LOW"},
        {"symbol": "SAFEAI", "name": "Safe AI Token",    "chain": "ethereum", "age_h": 3,  "risk": "SCAM"},
        {"symbol": "MOON9",  "name": "MoonShot Nine",    "chain": "bsc",      "age_h": 48, "risk": "HIGH"},
    ]
    trending = []
    for t in random.sample(tokens, k=random.randint(3, 5)):
        volume = round(random.uniform(50_000, 5_000_000), 0)
        trending.append({
            **t,
            "volume_24h_usd":   volume,
            "tx_count_24h":     random.randint(200, 8000),
            "unique_buyers":    random.randint(100, 5000),
            "price_change_pct": round(random.uniform(-20, 400), 2),
            "contract":         "0x" + "".join(random.choices("abcdef0123456789", k=40)),
            "honeypot":         t["risk"] == "SCAM",
            "lp_locked":        t["risk"] not in ("SCAM", "HIGH"),
        })
    return {
        "trending":     trending,
        "scam_count":   sum(1 for t in trending if t["honeypot"]),
        "chains":       list(set(t["chain"] for t in trending)),
    }


def mock_gas_data():
    now = datetime.utcnow()
    history = []
    base = 28.0
    for i in range(7 * 24):
        ts = now - timedelta(hours=7 * 24 - i)
        noise = random.gauss(0, 5)
        spike = 80 if (i % 24 == 14 and random.random() > 0.7) else 0
        history.append({
            "timestamp": ts.isoformat(),
            "gas_gwei":  max(5, round(base + noise + spike, 1)),
        })
    current = round(random.uniform(20, 120), 1)
    mean_7d = sum(h["gas_gwei"] for h in history) / len(history)
    std_7d  = (sum((h["gas_gwei"] - mean_7d) ** 2 for h in history) / len(history)) ** 0.5
    z_score = (current - mean_7d) / std_7d if std_7d else 0

    return {
        "current_gwei":  current,
        "mean_7d_gwei":  round(mean_7d, 1),
        "std_7d":        round(std_7d, 1),
        "z_score":       round(z_score, 2),
        "is_spike":      z_score > 2.0,
        "spike_cause":   random.choice(["NFT Mint Activity", "MEV Bot Surge", "DeFi Protocol Launch", "Normal"]),
        "history":       history[-48:],   # Last 48h for chart
        "safe_window":   "Low activity expected 02:00–06:00 UTC",
    }


def mock_report_summary(whale_data, token_data, gas_data):
    """Pre-built summary for demo mode."""
    flow = whale_data["net_flow"].title()
    scams = token_data["scam_count"]
    gas = gas_data["current_gwei"]
    spike = "spiking" if gas_data["is_spike"] else "normal"

    return f"""📈 **Daily On-Chain Intelligence Report**
*{datetime.utcnow().strftime('%B %d, %Y — %H:%M UTC')}*

---

**🐳 Whale Activity**
Smart money is showing {flow.lower()} patterns across {whale_data['unique_whales']} tracked wallets. Total moved in 24h: **${whale_data['total_volume_usd']:,.0f}**. The dominant flow direction is {flow}, suggesting {'accumulation pressure building' if flow == 'Accumulation' else 'potential distribution ahead — watch for sell pressure'}.

**🔥 Token Trends**
{len(token_data['trending'])} tokens showing unusual growth. {'⚠️ ' + str(scams) + ' honeypot(s) detected — avoid.' if scams else 'No honeypots detected in top movers.'} Strongest momentum seen on {', '.join(set(t['chain'] for t in token_data['trending'][:2]))} chains. New token activity is {'elevated' if len(token_data['trending']) > 3 else 'moderate'}.

**⛽ Gas & Network**
Ethereum gas is currently **{gas} gwei** — {spike} vs 7-day baseline of {gas_data['mean_7d_gwei']} gwei. {'Spike likely driven by: ' + gas_data['spike_cause'] + '.' if gas_data['is_spike'] else 'Network conditions are favorable for transactions.'} Best window for low-cost transactions: {gas_data['safe_window']}.

**💡 Key Takeaways**
1. {'Whales accumulating — bullish short-term signal' if flow == 'Accumulation' else 'Distribution detected — exercise caution on new positions'}
2. {'Avoid flagged tokens: ' + ', '.join(t['symbol'] for t in token_data['trending'] if t['honeypot']) if scams else 'No scam tokens in top movers today'}
3. {'Wait for gas to normalize before large transactions' if gas_data['is_spike'] else 'Good time for on-chain transactions — gas is low'}
"""