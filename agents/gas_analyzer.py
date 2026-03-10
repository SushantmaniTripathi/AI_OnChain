"""
agents/gas_analyzer.py — Monitors Ethereum gas and detects anomalies.

Data Sources:
  - Etherscan Gas Tracker API (free)
  - Dune Analytics (free): historical gas + MEV stats
  - Statistical z-score spike detection (scikit-learn / numpy)
"""
import logging
import numpy as np
import requests
from datetime import datetime, timedelta
from config import (
    ETHERSCAN_API_KEY, ETHERSCAN_BASE, DUNE_API_KEY, DUNE_BASE,
    GAS_SPIKE_Z_SCORE_THRESHOLD, GAS_HISTORY_DAYS
)
from utils.http_client import fetch
from utils.mock_data import mock_gas_data

logger = logging.getLogger(__name__)


def fetch_current_gas() -> dict:
    """Fetch current gas oracle from Etherscan."""
    if not ETHERSCAN_API_KEY:
        return {}
    try:
        resp = fetch(
            ETHERSCAN_BASE,
            params={
                "module": "gastracker",
                "action": "gasoracle",
                "apikey": ETHERSCAN_API_KEY,
            },
            cache_key="etherscan_gas_oracle",
        )
        result = resp.get("result", {})
        return {
            "safe_gwei":     float(result.get("SafeGasPrice", 0)),
            "propose_gwei":  float(result.get("ProposeGasPrice", 0)),
            "fast_gwei":     float(result.get("FastGasPrice", 0)),
            "base_fee":      float(result.get("suggestBaseFee", 0)),
        }
    except Exception as e:
        logger.warning(f"Gas oracle fetch failed: {e}")
        return {}


def fetch_dune_gas_history() -> list:
    """Fetch historical gas data from Dune Analytics."""
    if not DUNE_API_KEY or not DUNE_BASE:
        logger.info("DUNE_API_KEY or DUNE_BASE not set, cannot fetch historical gas data.")
        return []

    try:
        # Replace YOUR_DUNE_QUERY_ID with an actual query ID from your Dune account
        # that returns historical gas prices (e.g., daily average gwei for the last 7 days).
        query_id = "YOUR_DUNE_QUERY_ID" 
        
        # Step 1: Execute the query
        execute_url = f"{DUNE_BASE}/query/{query_id}/execute"
        headers = {"X-Dune-Api-Key": DUNE_API_KEY}
        
        execute_resp = requests.post(execute_url, headers=headers)
        execute_resp.raise_for_status()
        job_id = execute_resp.json().get("execution_id")

        if not job_id:
            logger.warning("Failed to execute Dune query, no execution_id received.")
            return []

        # Step 2: Poll for results
        results_url = f"{DUNE_BASE}/query/{job_id}/results"
        for _ in range(10): # Poll up to 10 times
            time.sleep(5) # Wait 5 seconds between polls
            results_resp = requests.get(results_url, headers=headers)
            results_resp.raise_for_status()
            results_data = results_resp.json()
            
            if results_data.get("state") == "QUERY_STATE_COMPLETED":
                rows = results_data.get("result", {}).get("rows", [])
                historical_data = []
                for row in rows:
                    # Assuming your Dune query returns 'day' (date string) and 'avg_gwei'
                    historical_data.append({
                        "day": row.get("day"),
                        "avg_gwei": row.get("avg_gwei")
                    })
                logger.info("Successfully fetched historical gas data from Dune Analytics.")
                return historical_data
            elif results_data.get("state") == "QUERY_STATE_FAILED":
                logger.warning(f"Dune query failed: {results_data.get('error')}")
                return []
        
        logger.warning("Dune query timed out.")
        return []

    except Exception as e:
        logger.warning(f"Dune historical gas fetch failed: {e}")
        return []


def run(network: str, timeframe: str) -> dict:
    """Main entry point for the gas analyzer agent."""
    gas = fetch_current_gas()
    history = fetch_dune_gas_history()
    
    if not gas and not history:
        logger.info("No live gas data found, using mock data.")
        return mock_gas_data()

    # Extract gwei values from history for statistical analysis
    historical_gwei_values = [item["avg_gwei"] for item in history]
    
    mean_7d_gwei = np.mean(historical_gwei_values) if historical_gwei_values else 0.0
    std_7d = np.std(historical_gwei_values) if historical_gwei_values else 0.0
    
    current_gwei = gas.get("propose_gwei", 0.0)
    z_score = 0.0
    is_spike = False
    spike_cause = "Normal"
    safe_window = "Low activity expected soon"

    if std_7d > 0 and current_gwei > 0:
        z_score = (current_gwei - mean_7d_gwei) / std_7d
        if z_score >= GAS_SPIKE_Z_SCORE_THRESHOLD:
            is_spike = True
            spike_cause = "Significant increase in gas price"
            safe_window = "High activity, consider waiting for lower gas prices"
        elif z_score <= -GAS_SPIKE_Z_SCORE_THRESHOLD:
            spike_cause = "Significant decrease in gas price"
            safe_window = "Good time for transactions, gas prices are low"
    
    return {
        "current_gwei":  current_gwei,
        "mean_7d_gwei":  round(mean_7d_gwei, 2),
        "std_7d":        round(std_7d, 2),
        "z_score":       round(z_score, 2),
        "is_spike":      is_spike,
        "spike_cause":   spike_cause,
        "history":       history,
        "safe_window":   safe_window,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))