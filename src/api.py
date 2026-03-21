"""
Ergast API wrapper functions.
All responses are cached as JSON under data/raw/ to avoid redundant calls.
"""

import json
import time
from pathlib import Path

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
CACHE_DIR = Path(__file__).parent.parent / "data" / "raw"
REQUEST_DELAY = 1.0  # seconds between requests to respect rate limits
MAX_RETRIES = 8


def _cache_path(endpoint: str) -> Path:
    safe = endpoint.strip("/").replace("/", "_")
    return CACHE_DIR / f"{safe}.json"


def get(endpoint: str, params: dict = None) -> dict:
    """
    Fetch an Ergast API endpoint, returning cached JSON if available.
    endpoint: e.g. '/2023/pit_stops.json'
    """
    cache = _cache_path(endpoint)
    if cache.exists():
        with open(cache) as f:
            return json.load(f)

    url = f"{BASE_URL}{endpoint}"
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=60)
        except requests.exceptions.Timeout:
            wait = 2 ** attempt * 3
            print(f"  Timeout, retrying in {wait}s...")
            time.sleep(wait)
            continue
        if response.status_code == 429:
            wait = 10 * (attempt + 1)  # 10, 20, 30, 40 ... seconds
            print(f"  Rate limited, retrying in {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        data = response.json()
        if "MRData" not in data:
            # Throttled response with 200 status — treat as rate limit
            wait = 10 * (attempt + 1)
            print(f"  Rate limited, retrying in {wait}s...")
            time.sleep(wait)
            continue
        break
    else:
        raise RuntimeError(f"Max retries exceeded for {endpoint}")

    cache.parent.mkdir(parents=True, exist_ok=True)
    with open(cache, "w") as f:
        json.dump(data, f)  # only valid MRData responses reach here

    time.sleep(REQUEST_DELAY)
    return data


def get_paginated(endpoint: str, limit: int = 100) -> list:
    """
    Fetch all pages of a paginated Ergast endpoint.
    Returns the combined list of result objects.
    """
    offset = 0
    results = []

    while True:
        # Build a cache key that includes pagination params
        paged_endpoint = f"{endpoint}?limit={limit}&offset={offset}"
        data = get(paged_endpoint)

        table = data.get("MRData", {})
        total = int(table.get("total", 0))

        # Extract the first list value inside MRData (e.g. RaceTable > Races)
        inner = _extract_inner(table)
        results.extend(inner)

        # Use actual items returned to advance offset (API may cap limit)
        actual_limit = int(table.get("limit", limit))
        offset += actual_limit
        if offset >= total or not inner:
            break

    return results


def _extract_inner(table: dict) -> list:
    """Pull the nested list out of an MRData response."""
    for key, val in table.items():
        if isinstance(val, dict):
            for inner_key, inner_val in val.items():
                if isinstance(inner_val, list):
                    return inner_val
    return []


def get_races(season: int) -> list:
    return get_paginated(f"/{season}/races.json")


def get_results(season: int) -> list:
    return get_paginated(f"/{season}/results.json")


def get_pit_stops(season: int, round_num: int) -> list:
    return get_paginated(f"/{season}/{round_num}/pitstops.json")


def get_lap_times(season: int, round_num: int) -> list:
    return get_paginated(f"/{season}/{round_num}/laps.json")


def get_drivers(season: int) -> list:
    return get_paginated(f"/{season}/drivers.json")
