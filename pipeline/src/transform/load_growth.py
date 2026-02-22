"""Transform demand data into year-over-year load growth metrics."""

import pandas as pd


def transform_load_growth(national_demand: list[dict]) -> dict:
    """Transform national demand records into year-over-year load growth.

    Args:
        national_demand: Already-transformed national demand records
            (list of {year, sector, consumption} dicts from transform_demand).

    Returns a dict with 'national' (list of {year, sector, consumption,
    yoy_change_pct}) and 'metadata'.
    """
    df = pd.DataFrame(national_demand)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["consumption"] = pd.to_numeric(df["consumption"], errors="coerce")
    df = df.dropna(subset=["year", "consumption"])
    df = df.sort_values(["sector", "year"])

    # Calculate year-over-year % change within each sector
    df["yoy_change_pct"] = (
        df.groupby("sector")["consumption"]
        .pct_change() * 100
    ).round(2)

    # Drop the first year for each sector (no prior year to compare)
    df = df.dropna(subset=["yoy_change_pct"])

    return {
        "national": df[["year", "sector", "consumption", "yoy_change_pct"]].to_dict(
            orient="records"
        ),
        "metadata": {
            "description": "Year-over-year percentage change in electricity consumption by sector",
            "source": "EIA Electricity Retail Sales",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "percent change",
        },
    }
