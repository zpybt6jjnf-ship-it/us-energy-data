"""Transform demand and population data into per-capita electricity consumption."""

import pandas as pd


def transform_per_capita(demand_by_state: list[dict], population: list[dict]) -> dict:
    """Calculate per-capita electricity consumption by state.

    Args:
        demand_by_state: State-level demand records (list of {state, year, sector,
            consumption} dicts from transform_demand).
        population: Population records (list of {state, year, population} dicts
            from fetch_state_population).

    Returns a dict with 'by_state' (list of {state, year, per_capita_kwh})
    and 'metadata'.
    """
    demand_df = pd.DataFrame(demand_by_state)
    pop_df = pd.DataFrame(population)

    demand_df["year"] = pd.to_numeric(demand_df["year"], errors="coerce")
    demand_df["consumption"] = pd.to_numeric(demand_df["consumption"], errors="coerce")
    demand_df = demand_df.dropna(subset=["year", "consumption"])

    # Sum consumption across all sectors for each state and year
    state_totals = (
        demand_df.groupby(["state", "year"])["consumption"]
        .sum()
        .reset_index()
    )

    # Merge with population data
    merged = state_totals.merge(pop_df[["state", "population"]], on="state", how="inner")

    # Calculate per-capita consumption
    # Consumption is in million kWh; convert to kWh then divide by population
    merged["per_capita_kwh"] = (
        (merged["consumption"] * 1_000_000) / merged["population"]
    ).round(2)

    merged = merged.sort_values(["state", "year"])

    return {
        "by_state": merged[["state", "year", "per_capita_kwh"]].to_dict(orient="records"),
        "metadata": {
            "description": "Per-capita electricity consumption by state",
            "source": "EIA Electricity Retail Sales + U.S. Census Bureau Population Estimates",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "kWh per person",
        },
    }
