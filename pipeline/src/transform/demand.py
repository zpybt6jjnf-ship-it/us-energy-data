"""Transform raw EIA retail sales (consumption) data into chart-ready JSON."""

import logging
import pandas as pd

from ..constants import US_STATES, US_TOTAL_LABELS

logger = logging.getLogger(__name__)

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

    state_col = "stateDescription"

    # --- National totals: use US Total rows if available, else sum valid states ---
    us_total_df = df[df[state_col].isin(US_TOTAL_LABELS)]
    if us_total_df.empty:
        logger.warning("No US Total rows found in demand data; falling back to summing state rows")
        us_total_df = df[df[state_col].isin(US_STATES)]

    national = (
        us_total_df.groupby(["period", "sector"])["sales"]
        .sum()
        .reset_index()
        .rename(columns={"period": "year", "sales": "consumption"})
        .sort_values(["sector", "year"])
    )

    # --- State-level: filter to valid US states only ---
    by_state = (
        df[df[state_col].isin(US_STATES)]
        .groupby([state_col, "period", "sector"])["sales"]
        .sum()
        .reset_index()
        .rename(columns={
            state_col: "state",
            "period": "year",
            "sales": "consumption",
        })
        .sort_values(["state", "sector", "year"])
    )

    # Validation: check national consumption is plausible
    latest_year = int(national["year"].max())
    latest_total = national[national["year"] == latest_year]["consumption"].sum()
    latest_twh = latest_total / 1_000  # million kWh / 1000 = billion kWh = TWh
    if latest_twh < 3000 or latest_twh > 5000:
        logger.warning(
            "National consumption for %d is %.0f TWh — outside expected range (3,000-5,000 TWh)",
            latest_year, latest_twh,
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
