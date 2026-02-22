"""Transform raw EIA fuel consumption for electricity generation into chart-ready JSON."""

import pandas as pd

FUEL_MAP = {
    "COL": "Coal",
    "NG": "Natural Gas",
    "PET": "Petroleum",
    "NUC": "Nuclear",
    "ALL": None,  # Skip totals
    "OTH": "Other",
    "SUN": "Solar",
    "WND": "Wind",
    "HYC": "Hydro",
    "GEO": "Geothermal",
    "WWW": "Wood",
    "WAS": "Waste",
    "OOG": "Other Gas",
}


def transform_fuel_consumption(raw_data: list[dict]) -> dict:
    """Transform raw EIA fuel consumption records into national summary.

    Aggregates by year and fuel type (national total only).
    Returns a dict with 'national' (list of {year, fuel, consumption, units})
    and 'metadata'.
    """
    df = pd.DataFrame(raw_data)

    df["consumption-for-eg"] = pd.to_numeric(
        df.get("consumption-for-eg", pd.Series()), errors="coerce"
    )
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["consumption-for-eg", "period"])

    # Filter to national (location = 'US') or state totals
    if "location" in df.columns:
        df = df[df["location"] == "US"]

    # Filter to total sector (all sectors)
    if "sectorid" in df.columns:
        # sectorid 99 or 98 is usually "all sectors" in EIA data
        total_sectors = df[df["sectorid"].isin(["98", "99"])]
        if len(total_sectors) > 0:
            df = total_sectors

    # Map fuel type
    if "fueltypeid" in df.columns:
        df["fuel"] = df["fueltypeid"].map(FUEL_MAP)
    elif "fuelTypeDescription" in df.columns:
        df["fuel"] = df["fuelTypeDescription"]
    else:
        df["fuel"] = "Unknown"

    # Drop total rows and unmapped fuels
    df = df[df["fuel"].notna()]

    # Keep only major fossil fuels for the chart
    major_fuels = ["Coal", "Natural Gas", "Petroleum"]
    df = df[df["fuel"].isin(major_fuels)]

    # Aggregate by year and fuel
    national = (
        df.groupby(["period", "fuel"])["consumption-for-eg"]
        .sum()
        .reset_index()
        .rename(columns={
            "period": "year",
            "consumption-for-eg": "consumption",
        })
        .sort_values(["fuel", "year"])
    )

    return {
        "national": national.to_dict(orient="records"),
        "metadata": {
            "description": "Fuel consumption for electricity generation by fuel type (national total)",
            "source": "EIA Electric Power Operational Data",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "thousand physical units (varies by fuel)",
        },
    }
