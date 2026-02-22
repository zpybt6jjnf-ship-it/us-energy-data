"""Transform raw EIA battery storage data into chart-ready JSON."""
import pandas as pd


def transform_storage(raw_data: list[dict]) -> dict:
    """Transform battery storage capability records into national time series.

    Input: raw records from EIA capability endpoint filtered to BAT source.
    Output: dict with 'national' [{year, capacity_mw}] and 'metadata'.
    """
    df = pd.DataFrame(raw_data)
    df["capability"] = pd.to_numeric(df["capability"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["capability", "period"])
    result = df[["period"]].rename(columns={"period": "year"}).copy()
    result["capacity_mw"] = df["capability"].values
    result = result.sort_values("year")

    return {
        "national": result.to_dict(orient="records"),
        "metadata": {
            "description": "US battery energy storage capacity deployment",
            "source": "EIA State Electricity Profiles - Generating Capacity",
            "url": "https://www.eia.gov/electricity/state/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "MW",
        },
    }
