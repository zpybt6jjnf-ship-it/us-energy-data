"""Transform raw EIA retail price data into chart-ready JSON."""

import pandas as pd


SECTOR_MAP = {
    "RES": "Residential",
    "COM": "Commercial",
    "IND": "Industrial",
}


def transform_retail_prices(raw_data: list[dict]) -> dict:
    """Transform raw EIA retail price records into structured output.

    Returns a dict with 'national' and 'by_state' keys,
    each containing chart-ready records.
    """
    df = pd.DataFrame(raw_data)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["price", "period"])
    df["sector"] = df["sectorid"].map(SECTOR_MAP)

    # National averages by sector and year
    national = (
        df.groupby(["period", "sector"])["price"]
        .mean()
        .reset_index()
        .rename(columns={"period": "year"})
        .sort_values(["sector", "year"])
    )

    # State-level data
    by_state = (
        df.groupby(["stateDescription", "period", "sector"])["price"]
        .first()
        .reset_index()
        .rename(columns={"stateDescription": "state", "period": "year"})
        .sort_values(["state", "sector", "year"])
    )

    return {
        "national": national.to_dict(orient="records"),
        "by_state": by_state.to_dict(orient="records"),
        "metadata": {
            "source": "EIA Electricity Retail Sales",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "cents per kWh",
        },
    }
