"""
utils/http_client.py — Rate-limited HTTP client with cache support
"""
import time
import requests
import logging
from utils.database import cache_get, cache_set


def fetch(url: str, params: dict = None, headers: dict = None,
          use_cache: bool = True, cache_key: str = None,
          retries: int = 3, backoff: float = 1.5) -> dict:
    """
    GET request with optional SQLite caching and exponential backoff retry.
    """
    key = cache_key or f"{url}:{str(sorted((params or {}).items()))}"

    if use_cache:
        cached = cache_get(key)
        if cached is not None:
            return cached

    last_exc = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if use_cache:
                cache_set(key, data)
            return data
        except requests.RequestException as e:
            last_exc = e
            time.sleep(backoff ** attempt)

    raise RuntimeError(f"HTTP request failed after {retries} attempts: {last_exc}")


def post(url: str, payload: dict, headers: dict = None,
         retries: int = 3, backoff: float = 1.5) -> dict:
    """POST request with retry."""
    last_exc = None
    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            last_exc = e
            time.sleep(backoff ** attempt)
    raise RuntimeError(f"POST failed after {retries} attempts: {last_exc}")

