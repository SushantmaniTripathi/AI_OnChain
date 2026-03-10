"""
config.py — Central configuration for On-Chain Analyst Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ----------------------------------------------------------------
ETHERSCAN_API_KEY   = os.getenv("ETHERSCAN_API_KEY", "")
FLIPSIDE_API_KEY    = os.getenv("FLIPSIDE_API_KEY", "")
COINGECKO_API_KEY   = os.getenv("COINGECKO_API_KEY", "")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")
DUNE_API_KEY        = os.getenv("DUNE_API_KEY", "")

# --- API Endpoints -----------------------------------------------------------
ETHERSCAN_BASE      = "https://api.etherscan.io/api"
COINGECKO_BASE      = "https://coingecko.com/api/v3"
GOPLUS_BASE         = "https://api.gopluslabs.io/api/v1"
DUNE_BASE           = "https://api.dune.com/api/v1"

# --- Whale Detection Thresholds ----------------------------------------------
WHALE_ETH_THRESHOLD     = 500        # ETH - minimum to flag as whale tx
WHALE_USD_THRESHOLD     = 500_000    # USD - minimum wallet size
WHALE_TX_MIN_VALUE_ETH  = 100        # ETH - minimum single tx to track

# --- Token Trending Config ---------------------------------------------------
TRENDING_MIN_VOLUME_USD     = 50_000   # Minimum 24h volume to consider trending
TRENDING_NEW_TOKEN_HOURS    = 72       # Token age threshold (hours) for "new"
TRENDING_MIN_TX_COUNT       = 200      # Minimum transactions in 24h

# --- Gas Spike Config --------------------------------------------------------
GAS_SPIKE_Z_SCORE_THRESHOLD = 2.0      # Z-score above which gas is "spiking"
GAS_HISTORY_DAYS            = 7        # Days of history for baseline

# --- LLM Config --------------------------------------------------------------
LLM_MODEL               = "llama3-8b-8192"   # Free on Groq
LLM_MAX_TOKENS          = 1024
LLM_TEMPERATURE         = 0.3

# --- Cache Config ------------------------------------------------------------
DB_PATH                 = "data/reports.db"
CACHE_TTL_MINUTES       = 30   # How long to cache API responses

# --- Scheduler ---------------------------------------------------------------
REPORT_HOUR_UTC         = 8    # Run daily at 08:00 UTC
REPORT_MINUTE_UTC       = 0

