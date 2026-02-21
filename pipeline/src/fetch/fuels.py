"""Fetch fossil fuel production data from the EIA API v2."""

import time
import requests

EIA_BASE = "https://api.eia.gov/v2"


def fetch_coal_production(api_key: str) -> list[dict]:
    """Fetch annual coal mine production by state."""
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/coal/mine-production/data",
            params={
                "api_key": api_key,
                "data[]": "production",
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


def fetch_natural_gas_production(api_key: str) -> list[dict]:
    """Fetch annual marketed natural gas production by state."""
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/natural-gas/prod/whv/data",
            params={
                "api_key": api_key,
                "data[]": "value",
                "facets[process][]": "VGM",
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


def fetch_crude_oil_production(api_key: str) -> list[dict]:
    """Fetch annual crude oil field production by state."""
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/petroleum/crd/crpdn/data",
            params={
                "api_key": api_key,
                "data[]": "value",
                "facets[process][]": "FPF",
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
