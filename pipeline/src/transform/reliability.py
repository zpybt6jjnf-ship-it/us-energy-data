"""Transform EIA-861 utility-level reliability data into chart-ready JSON.

Aggregates utility-level SAIDI/SAIFI to state and national level using
customer-weighted averages. Coalesces IEEE Standard and Other Standard
reporting (utilities use one or the other).
"""

import pandas as pd
import numpy as np

# State abbreviation → FIPS code mapping
STATE_ABBR_TO_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
    "CO": "08", "CT": "09", "DE": "10", "DC": "11", "FL": "12",
    "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18",
    "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23",
    "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
    "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38",
    "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
    "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
    "VT": "50", "VA": "51", "WA": "53", "WV": "54", "WI": "55",
    "WY": "56",
}

STATE_ABBR_TO_NAME = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


def _coalesce_standards(df: pd.DataFrame) -> pd.DataFrame:
    """Coalesce IEEE and Other standard values into unified columns.

    Most utilities report under one standard or the other. We prefer IEEE
    when available, falling back to Other.
    """
    df = df.copy()
    df["saidi"] = df["ieee_saidi_with_med"].fillna(df["other_saidi_with_med"])
    df["saifi"] = df["ieee_saifi_with_med"].fillna(df["other_saifi_with_med"])
    df["caidi"] = df["ieee_caidi_with_med"].fillna(df["other_caidi_with_med"])
    df["saidi_no_med"] = df["ieee_saidi_no_med"].fillna(df["other_saidi_no_med"])
    df["saifi_no_med"] = df["ieee_saifi_no_med"].fillna(df["other_saifi_no_med"])
    df["customers"] = df["ieee_customers"].fillna(df["other_customers"])
    return df


def _weighted_avg(group: pd.DataFrame, value_col: str, weight_col: str = "customers") -> float:
    """Customer-weighted average, ignoring rows with missing values or zero customers."""
    mask = group[value_col].notna() & group[weight_col].notna() & (group[weight_col] > 0)
    subset = group[mask]
    if subset.empty:
        return np.nan
    total_weight = subset[weight_col].sum()
    if total_weight == 0:
        return np.nan
    return (subset[value_col] * subset[weight_col]).sum() / total_weight


def transform_reliability(raw_df: pd.DataFrame) -> dict:
    """Transform utility-level EIA-861 data into national trend + state-level aggregates.

    Args:
        raw_df: DataFrame from fetch_reliability() with canonical column names.

    Returns:
        dict with keys: national, by_state, by_state_trend, metadata
    """
    df = _coalesce_standards(raw_df)

    # Filter to rows that have at least SAIDI and customers
    df = df[df["saidi"].notna() & df["customers"].notna() & (df["customers"] > 0)].copy()

    # --- National trend (customer-weighted average per year) ---
    national_records = []
    for year, group in df.groupby("data_year"):
        saidi = _weighted_avg(group, "saidi")
        saifi = _weighted_avg(group, "saifi")
        saidi_no_med = _weighted_avg(group, "saidi_no_med")
        saifi_no_med = _weighted_avg(group, "saifi_no_med")
        total_customers = group["customers"].sum()
        n_utilities = len(group)

        national_records.append({
            "year": int(year),
            "saidi": round(saidi, 1) if not np.isnan(saidi) else None,
            "saifi": round(saifi, 2) if not np.isnan(saifi) else None,
            "saidi_no_med": round(saidi_no_med, 1) if not np.isnan(saidi_no_med) else None,
            "saifi_no_med": round(saifi_no_med, 2) if not np.isnan(saifi_no_med) else None,
            "customers": int(total_customers),
            "utilities": n_utilities,
        })

    national_records.sort(key=lambda r: r["year"])

    # --- State-level aggregates (latest year per state) ---
    latest_year = df["data_year"].max()
    latest_df = df[df["data_year"] == latest_year]

    state_records = []
    for state_abbr, group in latest_df.groupby("state"):
        if state_abbr not in STATE_ABBR_TO_FIPS:
            continue  # Skip territories

        saidi = _weighted_avg(group, "saidi")
        saifi = _weighted_avg(group, "saifi")
        saidi_no_med = _weighted_avg(group, "saidi_no_med")
        saifi_no_med = _weighted_avg(group, "saifi_no_med")
        total_customers = group["customers"].sum()

        if np.isnan(saidi):
            continue

        state_records.append({
            "state": STATE_ABBR_TO_NAME.get(state_abbr, state_abbr),
            "stateAbbr": state_abbr,
            "fips": STATE_ABBR_TO_FIPS[state_abbr],
            "saidi": round(saidi, 1),
            "saifi": round(saifi, 2) if not np.isnan(saifi) else None,
            "saidi_no_med": round(saidi_no_med, 1) if not np.isnan(saidi_no_med) else None,
            "saifi_no_med": round(saifi_no_med, 2) if not np.isnan(saifi_no_med) else None,
            "customers": int(total_customers),
            "year": int(latest_year),
        })

    state_records.sort(key=lambda r: r["state"])

    # --- State-level trend (for potential future use) ---
    state_trend_records = []
    for (year, state_abbr), group in df.groupby(["data_year", "state"]):
        if state_abbr not in STATE_ABBR_TO_FIPS:
            continue

        saidi = _weighted_avg(group, "saidi")
        saifi = _weighted_avg(group, "saifi")
        saidi_no_med = _weighted_avg(group, "saidi_no_med")
        saifi_no_med = _weighted_avg(group, "saifi_no_med")
        if np.isnan(saidi):
            continue

        state_trend_records.append({
            "year": int(year),
            "stateAbbr": state_abbr,
            "fips": STATE_ABBR_TO_FIPS[state_abbr],
            "saidi": round(saidi, 1),
            "saifi": round(saifi, 2) if not np.isnan(saifi) else None,
            "saidi_no_med": round(saidi_no_med, 1) if not np.isnan(saidi_no_med) else None,
            "saifi_no_med": round(saifi_no_med, 2) if not np.isnan(saifi_no_med) else None,
        })

    state_trend_records.sort(key=lambda r: (r["year"], r["stateAbbr"]))

    return {
        "national": national_records,
        "by_state": state_records,
        "by_state_trend": state_trend_records,
        "metadata": {
            "source": "EIA-861 Annual Electric Power Industry Report — Reliability",
            "url": "https://www.eia.gov/electricity/data/eia861/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "minutes per customer per year (SAIDI)",
            "years": f"2013-{int(latest_year)}",
            "methodology": "Customer-weighted average of utility-level SAIDI/SAIFI. "
                           "IEEE Standard preferred, with Other Standard as fallback. "
                           "With Major Event Days (MED) variant shown by default.",
        },
    }
