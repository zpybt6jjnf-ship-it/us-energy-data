"""Fetch capacity, CO2 emissions, and fuel consumption data from the EIA API v2."""

import time
import requests

EIA_BASE = "https://api.eia.gov/v2"


def fetch_capacity_by_source(api_key: str) -> list[dict]:
    """Fetch generating capacity by energy source and state (annual).

    Uses state-electricity-profiles/capability endpoint which provides
    net summer capacity (MW) by state, energy source, and sector.
    Filters to TOT (all sectors) to get total capacity.
    """
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/electricity/state-electricity-profiles/capability/data",
            params={
                "api_key": api_key,
                "data[]": "capability",
                "frequency": "annual",
                "facets[producertypeid][]": "TOT",  # All sectors combined
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


def fetch_co2_emissions(api_key: str) -> list[dict]:
    """Fetch CO2 emissions from electricity generation by state and fuel.

    Uses state-electricity-profiles/emissions-by-state-by-fuel endpoint.
    Returns records with CO2 total (thousand metric tons) and rate (lbs/MWh).
    """
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/electricity/state-electricity-profiles/emissions-by-state-by-fuel/data",
            params={
                "api_key": api_key,
                "data[]": ["co2-thousand-metric-tons", "co2-rate-lbs-mwh"],
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


def fetch_fuel_consumption(api_key: str) -> list[dict]:
    """Fetch fuel consumption for electricity generation by fuel type.

    Returns raw records from EIA's electric power operational data endpoint.
    """
    all_data: list[dict] = []
    offset = 0

    while True:
        resp = requests.get(
            f"{EIA_BASE}/electricity/electric-power-operational-data/data",
            params={
                "api_key": api_key,
                "data[]": "consumption-for-eg",
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


def fetch_battery_storage(api_key: str) -> list[dict]:
    """Fetch battery storage capacity from capability endpoint."""
    resp = requests.get(
        f"{EIA_BASE}/electricity/state-electricity-profiles/capability/data",
        params={
            "api_key": api_key,
            "data[]": "capability",
            "frequency": "annual",
            "facets[energysourceid][]": "BAT",
            "facets[producertypeid][]": "TOT",
            "facets[stateId][]": "US",
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "length": 50,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["response"]["data"]
