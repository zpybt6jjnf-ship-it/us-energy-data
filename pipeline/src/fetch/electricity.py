"""Fetch electricity data from the EIA API v2."""

import time
import requests

EIA_BASE = "https://api.eia.gov/v2"


def fetch_retail_prices(api_key: str) -> list[dict]:
    """Fetch retail electricity prices by state and sector.

    Returns raw records from EIA's electricity/retail-sales endpoint.
    """
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/electricity/retail-sales/data",
            params={
                "api_key": api_key,
                "data[]": "price",
                "facets[sectorid][]": ["RES", "COM", "IND"],
                "frequency": "annual",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": offset,
                "length": 5000,
            },
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()["response"]["data"]
        if not batch:
            break
        all_data.extend(batch)
        offset += 5000
        time.sleep(0.5)  # Respect rate limits

    return all_data


def fetch_demand(api_key: str) -> list[dict]:
    """Fetch electricity retail sales (consumption in MWh) by state and sector."""
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/electricity/retail-sales/data",
            params={
                "api_key": api_key,
                "data[]": "sales",
                "facets[sectorid][]": ["RES", "COM", "IND"],
                "frequency": "annual",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": offset,
                "length": 5000,
            },
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()["response"]["data"]
        if not batch:
            break
        all_data.extend(batch)
        offset += 5000
        time.sleep(0.5)

    return all_data


def fetch_generation_by_source(api_key: str) -> list[dict]:
    """Fetch electricity generation by energy source and state."""
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/electricity/electric-power-operational-data/data",
            params={
                "api_key": api_key,
                "data[]": "generation",
                "facets[fueltypeid][]": [
                    "COL", "NG", "NUC", "WND", "SUN", "HYC", "PET", "OTH", "GEO",
                ],
                "frequency": "annual",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": offset,
                "length": 5000,
            },
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()["response"]["data"]
        if not batch:
            break
        all_data.extend(batch)
        offset += 5000
        time.sleep(0.5)

    return all_data
