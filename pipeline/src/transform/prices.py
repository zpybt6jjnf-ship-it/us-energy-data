"""Transform raw EIA retail price data into chart-ready JSON."""

import logging
import pandas as pd

from ..constants import US_STATES, US_TOTAL_LABELS

logger = logging.getLogger(__name__)

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
    df = df[df["sector"].notna()]

    state_col = "stateDescription"

    # --- National averages: use US Total rows (already a weighted average from EIA) ---
    us_total_df = df[df[state_col].isin(US_TOTAL_LABELS)]
    if us_total_df.empty:
        logger.warning("No US Total rows found in price data; falling back to unweighted state mean")
        us_total_df = df[df[state_col].isin(US_STATES)]

    national = (
        us_total_df.groupby(["period", "sector"])["price"]
        .mean()
        .reset_index()
        .rename(columns={"period": "year"})
        .sort_values(["sector", "year"])
    )

    # --- State-level: filter to valid US states only ---
    by_state = (
        df[df[state_col].isin(US_STATES)]
        .groupby([state_col, "period", "sector"])["price"]
        .first()
        .reset_index()
        .rename(columns={state_col: "state", "period": "year"})
        .sort_values(["state", "sector", "year"])
    )

    n_states = by_state["state"].nunique()
    if n_states != 51:
        logger.warning("Expected 51 state entities (50 + DC), got %d", n_states)

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
