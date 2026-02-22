"""Transform capacity data into year-over-year capacity additions/retirements."""
import pandas as pd


def transform_capacity_changes(capacity_national: list[dict]) -> dict:
    """Compute net capacity change by source and year from existing capacity data.

    Input: capacity-national.json records [{year, source, capacity_mw}]
    Output: [{year, source, net_change_mw}] — year-over-year difference
    """
    df = pd.DataFrame(capacity_national)
    df = df.sort_values(["source", "year"])
    df["net_change_mw"] = df.groupby("source")["capacity_mw"].diff()
    df = df.dropna(subset=["net_change_mw"])
    # Round to whole MW
    df["net_change_mw"] = df["net_change_mw"].round(0)

    return {
        "national": df[["year", "source", "net_change_mw"]].to_dict(orient="records"),
        "metadata": {
            "description": "Net capacity additions by energy source (year-over-year change in installed capacity)",
            "source": "EIA State Electricity Profiles - Generating Capacity",
            "url": "https://www.eia.gov/electricity/state/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "MW (net change)",
        },
    }
