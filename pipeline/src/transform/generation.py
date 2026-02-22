"""Transform raw EIA generation data into chart-ready JSON."""

import logging
import pandas as pd

from ..constants import US_STATES, US_TOTAL_LABELS

logger = logging.getLogger(__name__)

FUEL_MAP = {
    "COL": "Coal",
    "NG": "Natural Gas",
    "NUC": "Nuclear",
    "WND": "Wind",
    "SUN": "Solar",
    "HYC": "Hydro",
    "PET": "Petroleum",
    "OTH": "Other",
    "GEO": "Geothermal",
}


def transform_generation(raw_data: list[dict]) -> dict:
    """Transform raw EIA generation records into structured output."""
    df = pd.DataFrame(raw_data)
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["generation", "period"])
    df["source"] = df["fueltypeid"].map(FUEL_MAP)

    # Log unmapped fuel type IDs
    unmapped = df[df["source"].isna()]["fueltypeid"].unique()
    if len(unmapped) > 0:
        logger.warning("Unmapped fuel type IDs in generation data: %s", unmapped)

    df = df[df["source"].notna()]

    # Filter to sectorid 99 ("All Sectors") to avoid double-counting across
    # producer types (utilities, IPPs, CHP, industrial, etc.)
    if "sectorid" in df.columns:
        sector_99 = df[df["sectorid"].astype(str) == "99"]
        if not sector_99.empty:
            df = sector_99
        else:
            logger.warning("No sectorid=99 rows found; using all rows (may double-count)")

    # Identify state description column
    state_col = "stateDescription"

    # --- National generation: use only US Total rows ---
    us_total_df = df[df[state_col].isin(US_TOTAL_LABELS)]
    if us_total_df.empty:
        logger.warning("No US Total rows found in generation data; falling back to summing state rows")
        state_df = df[df[state_col].isin(US_STATES)]
        us_total_df = state_df

    national = (
        us_total_df.groupby(["period", "source"])["generation"]
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

    # --- State-level generation: filter to valid US states only ---
    by_state = (
        df[df[state_col].isin(US_STATES)]
        .groupby([state_col, "period", "source"])["generation"]
        .sum()
        .reset_index()
        .rename(columns={state_col: "state", "period": "year"})
        .sort_values(["state", "source", "year"])
    )

    # Calculate renewable share by state for latest year
    latest_year = int(by_state["year"].max())
    latest = by_state[by_state["year"] == latest_year].copy()
    renewables = ["Wind", "Solar", "Hydro", "Geothermal"]
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

    # Validation: check national generation is in plausible range
    latest_national = national[national["year"] == latest_year]["generation"].sum()
    latest_twh = latest_national / 1_000  # thousand MWh / 1000 = million MWh = TWh
    if latest_twh < 3000 or latest_twh > 6000:
        logger.warning(
            "National generation for %d is %.0f TWh — outside expected range (3,000-6,000 TWh)",
            latest_year, latest_twh,
        )

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
