"""Transform raw EIA generation data into chart-ready JSON."""

import pandas as pd


FUEL_MAP = {
    "COL": "Coal",
    "NG": "Natural Gas",
    "NUC": "Nuclear",
    "WND": "Wind",
    "SUN": "Solar",
    "HYC": "Hydro",
    "PET": "Petroleum",
    "OTH": "Other",
}


def transform_generation(raw_data: list[dict]) -> dict:
    """Transform raw EIA generation records into structured output."""
    df = pd.DataFrame(raw_data)
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["generation", "period"])
    df["source"] = df["fueltypeid"].map(FUEL_MAP)
    df = df[df["source"].notna()]

    # National generation by source and year (thousand MWh)
    national = (
        df.groupby(["period", "source"])["generation"]
        .sum()
        .reset_index()
        .rename(columns={"period": "year"})
        .sort_values(["source", "year"])
    )

    # Calculate % shares per year
    year_totals = national.groupby("year")["generation"].sum().reset_index()
    year_totals.columns = ["year", "total"]
    national = national.merge(year_totals, on="year")
    national["share"] = (national["generation"] / national["total"] * 100).round(2)
    national = national.drop(columns=["total"])

    # State-level generation by source and year
    by_state = (
        df.groupby(["stateDescription", "period", "source"])["generation"]
        .sum()
        .reset_index()
        .rename(columns={"stateDescription": "state", "period": "year"})
        .sort_values(["state", "source", "year"])
    )

    # Calculate renewable share by state for latest year
    latest_year = int(by_state["year"].max())
    latest = by_state[by_state["year"] == latest_year].copy()
    renewables = ["Wind", "Solar", "Hydro"]
    state_totals = latest.groupby("state")["generation"].sum().reset_index()
    state_totals.columns = ["state", "total"]
    renewable_totals = (
        latest[latest["source"].isin(renewables)]
        .groupby("state")["generation"]
        .sum()
        .reset_index()
    )
    renewable_totals.columns = ["state", "renewable"]
    renewable_share = state_totals.merge(renewable_totals, on="state", how="left")
    renewable_share["renewable"] = renewable_share["renewable"].fillna(0)
    renewable_share["renewable_share"] = (
        renewable_share["renewable"] / renewable_share["total"] * 100
    ).round(2)

    return {
        "national": national.to_dict(orient="records"),
        "by_state": by_state.to_dict(orient="records"),
        "renewable_share": renewable_share[["state", "renewable_share"]].to_dict(orient="records"),
        "metadata": {
            "source": "EIA Electric Power Operational Data",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "thousand MWh",
            "latest_year": latest_year,
        },
    }
