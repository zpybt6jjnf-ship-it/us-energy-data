"""Fetch petroleum and natural gas import/export data from EIA API v2."""
import time
import requests

EIA_BASE = "https://api.eia.gov/v2"


def fetch_petroleum_trade(api_key: str) -> list[dict]:
    """Fetch US petroleum imports and exports (crude oil + products), annual."""
    all_data = []

    # Imports
    for product in ["EPC0", "EPP2"]:  # Crude Oil, Finished Products
        resp = requests.get(
            f"{EIA_BASE}/petroleum/move/imp/data",
            params={
                "api_key": api_key,
                "data[]": "value",
                "frequency": "annual",
                "facets[duoarea][]": "NUS-Z00",
                "facets[product][]": product,
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 5000,
            },
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()["response"]["data"]
        for rec in batch:
            rec["direction"] = "imports"
        all_data.extend(batch)
        time.sleep(0.5)

    # Exports
    for product in ["EPC0", "EPP2"]:
        resp = requests.get(
            f"{EIA_BASE}/petroleum/move/exp/data",
            params={
                "api_key": api_key,
                "data[]": "value",
                "frequency": "annual",
                "facets[duoarea][]": "NUS-Z00",
                "facets[product][]": product,
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 5000,
            },
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()["response"]["data"]
        for rec in batch:
            rec["direction"] = "exports"
        all_data.extend(batch)
        time.sleep(0.5)

    return all_data


def fetch_natural_gas_trade(api_key: str) -> list[dict]:
    """Fetch US natural gas imports and exports, annual."""
    resp = requests.get(
        f"{EIA_BASE}/natural-gas/sum/lsum/data",
        params={
            "api_key": api_key,
            "data[]": "value",
            "frequency": "annual",
            "facets[duoarea][]": "NUS-Z00",
            "facets[process][]": ["IM0", "EEX"],
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 5000,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["response"]["data"]
