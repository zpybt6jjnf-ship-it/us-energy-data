"""Transform raw EIA retail sales (consumption) data into chart-ready JSON."""

import pandas as pd


SECTOR_MAP = {
    "RES": "Residential",
    "COM": "Commercial",
    "IND": "Industrial",
}


def transform_demand(raw_data: list[dict]) -> dict:
    """Transform raw EIA consumption records into structured output."""
    df = pd.DataFrame(raw_data)
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["sales", "period"])
    df["sector"] = df["sectorid"].map(SECTOR_MAP)
    df = df[df["sector"].notna()]

    # National totals by sector and year (sales in million kWh)
    national = (
        df.groupby(["period", "sector"])["sales"]
        .sum()
        .reset_index()
        .rename(columns={"period": "year", "sales": "consumption"})
        .sort_values(["sector", "year"])
    )

    # State-level by sector and year
    by_state = (
        df.groupby(["stateDescription", "period", "sector"])["sales"]
        .sum()
        .reset_index()
        .rename(columns={
            "stateDescription": "state",
            "period": "year",
            "sales": "consumption",
        })
        .sort_values(["state", "sector", "year"])
    )

    return {
        "national": national.to_dict(orient="records"),
        "by_state": by_state.to_dict(orient="records"),
        "metadata": {
            "source": "EIA Electricity Retail Sales",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "million kWh",
        },
    }
