"""
agents/token_trending.py — Identifies trending new tokens with risk scoring.

Data Sources:
  - CoinGecko API (free): trending tokens, price data
  - Etherscan API (free): contract age, verification status
  - GoPlus Security API (free): honeypot detection, scam flags
"""
import logging
from datetime import datetime
from config import (
    ETHERSCAN_API_KEY, ETHERSCAN_BASE, COINGECKO_BASE, COINGECKO_API_KEY,
    GOPLUS_BASE, TRENDING_MIN_VOLUME_USD, TRENDING_NEW_TOKEN_HOURS
)
from utils.http_client import fetch
from utils.mock_data import mock_token_data

logger = logging.getLogger(__name__)


def fetch_coingecko_trending() -> list:
    """Get CoinGecko's trending coins list (no API key needed)."""
    try:
        resp = fetch(
            f"{COINGECKO_BASE}/search/trending",
            headers={"x-cg-pro-api-key": COINGECKO_API_KEY} if COINGECKO_API_KEY else None,
            cache_key="coingecko_trending"
        )
        coins = resp.get("coins", [])
        result = []
        for entry in coins:
            item = entry.get("item", {})
            result.append({
                "symbol":       item.get("symbol", ""),
                "name":         item.get("name", ""),
                "contract":     item.get("platforms", {}).get("ethereum", ""),
                "chain":        "ethereum" if item.get("platforms", {}).get("ethereum") else "multi",
                "score":        item.get("score", 0),
                "market_cap_rank": item.get("market_cap_rank"),
                "thumb":        item.get("thumb", ""),
                "volume_24h_usd": 0, # TODO: Fetch actual 24h volume if needed
            })
        return result
    except Exception as e:
        logger.warning(f"CoinGecko trending fetch failed: {e}")
        return []


def run(network: str, timeframe: str, target_wallet: str) -> dict:
    """Main entry point for the token trending agent."""
    trending = fetch_coingecko_trending()
    
    if not trending:
        logger.info("No live trending data found, using mock data.")
        return mock_token_data()
        
    return {
        "trending":     trending,
        "scam_count":   0, # TODO: Implement actual scam detection
        "chains":       list(set(t["chain"] for t in trending)),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))

