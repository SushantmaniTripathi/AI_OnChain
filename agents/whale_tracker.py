"""
agents/whale_tracker.py — Detects large wallet movements on Ethereum.

Data Sources:
  - Etherscan API (free): large ETH transfers
  - Flipside Crypto (free): multi-chain whale queries

Falls back to mock data when API keys are not set.
"""
import logging
from datetime import datetime, timedelta
from config import (
    ETHERSCAN_API_KEY, ETHERSCAN_BASE,
    WHALE_ETH_THRESHOLD, WHALE_TX_MIN_VALUE_ETH,
    COINGECKO_API_KEY, COINGECKO_BASE
)
from utils.http_client import fetch
from utils.mock_data import mock_whale_data

logger = logging.getLogger(__name__)

# Known labeled wallets (expand this dict over time)
KNOWN_WALLETS = {
    "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance Hot Wallet",
    "0x477573f212a7bdd5f7c12889bd1ad0aa44fb82aa": "Binance Cold Wallet",
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance Exchange",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance 10",
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance 14",
    "0x56eddb7aa87536c09ccc2793473599fd21a8b17f": "Binance 15",
    "0x9696f59e4d72e237be84ffd425dcad154bf96976": "Bitfinex",
    "0x742d35cc6634c0532925a3b844bc454e4438f44e": "Coinbase Prime",
    "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase 2",
    "0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740": "Coinbase 3",
}


def _label_wallet(address: str) -> str:
    return KNOWN_WALLETS.get(address.lower(), "Unknown Whale")


def fetch_large_eth_transfers(network: str, timeframe: str, whale_threshold: int, target_wallet: str) -> list:
    """
    Fetch large ETH transfers from Etherscan.
    Returns list of transfer dicts.
    """
    if not ETHERSCAN_API_KEY:
        return []

    try:
        # Get latest block number
        block_resp = fetch(
            ETHERSCAN_BASE,
            params={"module": "proxy", "action": "eth_blockNumber",
                    "apikey": ETHERSCAN_API_KEY},
            cache_key="etherscan_latest_block"
        )
        latest_block = int(block_resp.get("result", "0x0"), 16)
        # Calculate start_block based on timeframe
        time_delta_hours = {
            "1h": 1, "6h": 6, "24h": 24, "7d": 7 * 24
        }.get(timeframe, 24)
        
        # Approximate blocks per hour for Ethereum (adjust for other networks if needed)
        blocks_per_hour = 450 
        blocks_to_fetch = time_delta_hours * blocks_per_hour
        
        start_block = max(0, latest_block - blocks_to_fetch)

        # Fetch internal transactions above threshold
        resp = fetch(
            ETHERSCAN_BASE,
            params={
                "module":     "account",
                "action":     "txlist",
                "startblock": start_block,
                "endblock":   latest_block,
                "sort":       "desc",
                "apikey":     ETHERSCAN_API_KEY,
                "address":    target_wallet if target_wallet else None # Filter by target wallet if provided
            },
            cache_key=f"etherscan_txlist_{start_block}_{target_wallet}"
        )

        txs = resp.get("result", [])
        if not isinstance(txs, list):
            return []

        large_txs = []
        for tx in txs[:500]: # Limit to first 500 transactions for performance
            try:
                eth_val = int(tx.get("value", "0")) / 1e18
                if eth_val >= whale_threshold: # Use dynamic whale_threshold
                    # Further filter by target_wallet if it wasn't filtered by API
                    if target_wallet and not (tx["from"].lower() == target_wallet.lower() or tx["to"].lower() == target_wallet.lower()):
                        continue
                    
                    large_txs.append({
                        "tx_hash":    tx["hash"],
                        "wallet":     tx["from"],
                        "to":         tx["to"],
                        "label":      _label_wallet(tx["from"]),
                        "value_eth":  round(eth_val, 4),
                        "value_usd":  round(eth_val * _get_eth_price(), 0),
                        "direction":  "OUT", # Simplified, could be IN/OUT based on target_wallet
                        "token":      "ETH",
                        "timestamp":  datetime.utcfromtimestamp(
                            int(tx.get("timeStamp", 0))
                        ).isoformat(),
                    })
            except (ValueError, KeyError):
                continue
        return large_txs
    except Exception as e:
        logger.warning(f"Etherscan fetch failed: {e}")
        return []


def _get_eth_price() -> float:
    """Get current ETH price for USD conversion from CoinGecko."""
    if not COINGECKO_API_KEY:
        logger.info("COINGECKO_API_KEY not set, using mock ETH price.")
        return 3250.0

    try:
        resp = fetch(
            f"{COINGECKO_BASE}/simple/price",
            params={"ids": "ethereum", "vs_currencies": "usd"},
            headers={"x-cg-pro-api-key": COINGECKO_API_KEY},
            cache_key="coingecko_eth_price"
        )
        return resp.get("ethereum", {}).get("usd", 3250.0)
    except Exception as e:
        logger.warning(f"CoinGecko ETH price fetch failed: {e}, using mock price.")
        return 3250.0


def run(network: str, timeframe: str, whale_threshold: int, target_wallet: str) -> dict:
    """Main entry point for the whale agent."""
    movements = fetch_large_eth_transfers(network, timeframe, whale_threshold, target_wallet)
    
    if not movements:
        logger.info("No live whale data found, using mock data.")
        return mock_whale_data()
        
    return {
        "movements":        movements,
        "total_volume_usd": sum(m["value_usd"] for m in movements),
        "net_flow":         "MIXED",
        "unique_whales":    len(set(m["wallet"] for m in movements)),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))