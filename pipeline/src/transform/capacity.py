"""Transform raw EIA capacity and CO2 emissions data into chart-ready JSON."""

import logging
import pandas as pd

from ..constants import US_STATES, US_TOTAL_LABELS

logger = logging.getLogger(__name__)

SOURCE_MAP = {
    "COL": "Coal",
    "NG": "Natural Gas",
    "NUC": "Nuclear",
    "WND": "Wind",
    "SUN": "Solar",
    "HYC": "Hydro",
    "PET": "Petroleum",
    "WAT": "Hydro",
    "OTH": "Other",
    "GEO": "Geothermal",
    "BIT": "Coal",
    "SUB": "Coal",
    "LIG": "Coal",
    "DFO": "Petroleum",
    "RFO": "Petroleum",
    "WO": "Petroleum",
    "PC": "Petroleum",
    "BA": "Battery Storage",
    "BAT": "Battery Storage",
    "SOL": "Solar",
    "SOLPV": "Solar",
    "SOLTH": "Solar",
    "HPS": "Hydro",  # Hydroelectric Pumped Storage
    "NGCC": "Natural Gas",  # Natural Gas Combined Cycle
    "NGGT": "Natural Gas",  # Natural Gas Gas Turbine
    "NGIC": "Natural Gas",  # Natural Gas Internal Combustion
    "NGST": "Natural Gas",  # Natural Gas Steam Turbine
    "NGOTH": "Natural Gas",  # Natural Gas Other
    "OBM": "Other",  # Other Biomass
    "OT": "Other",  # Other
    "OOG": "Other",  # Other Gases
    "WOO": "Other",  # Wood and Wood-derived Fuels
    "PETGT": "Petroleum",  # Petroleum Gas Turbine
    "PETIC": "Petroleum",  # Petroleum Internal Combustion
    "PETOTH": "Petroleum",  # Petroleum Other
    "PETST": "Petroleum",  # Petroleum Steam Turbine
    "ALL": None,  # Skip "All" aggregate rows
    # state-electricity-profiles/capability endpoint codes (full names)
    "Coal": "Coal",
    "Hydroelectric Conventional": "Hydro",
    "Natural Gas": "Natural Gas",
    "Nuclear": "Nuclear",
    "Other": "Other",
    "Other Biomass": "Other",
    "Other Gases": "Natural Gas",
    "Other Renewables": "Other",
    "Petroleum": "Petroleum",
    "Pumped Storage": "Hydro",
    "Solar Thermal and Photovoltaic": "Solar",
    "Wind": "Wind",
    "Wood and Wood Derived Fuels": "Other",
    "All Sources": None,  # Skip total row
    "Geothermal": "Geothermal",
}


def transform_capacity(raw_data: list[dict]) -> dict:
    """Transform raw EIA capacity records into structured output.

    Returns a dict with 'national' (list of {year, source, capacity_mw})
    and 'metadata'.
    """
    df = pd.DataFrame(raw_data)

    # Detect capacity column
    cap_col = None
    for col in ["capability", "nameplate-capacity-mw", "net-summer-capacity-mw"]:
        if col in df.columns:
            cap_col = col
            break
    if cap_col is None:
        raise ValueError(f"No capacity column found. Columns: {list(df.columns)}")

    df[cap_col] = pd.to_numeric(df[cap_col], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=[cap_col, "period"])

    # Map energy source codes/names to readable names
    source_col = None
    for col in ["energysourceid", "energySourceDescription", "energy_source_code",
                 "energy-source-code", "energySourceCode", "fueltypeid"]:
        if col in df.columns:
            source_col = col
            break
    if source_col is None:
        for col in df.columns:
            if "source" in col.lower() or "fuel" in col.lower() or "energy" in col.lower():
                source_col = col
                break

    # Aggregate codes that duplicate their subtypes (e.g. NG = NGCC + NGGT + NGIC + NGST).
    # The EIA capability endpoint returns both levels — keep only the subtypes to avoid
    # double-counting.
    AGGREGATE_CODES = {"NG", "PET", "SOL"}

    if source_col is not None:
        # Drop aggregate rows when subtypes exist in the same (period, state) group
        has_subtypes = set()
        subtype_prefixes = {"NG": "NG", "PET": "PET", "SOL": "SOL"}
        for code in df[source_col].unique():
            for agg, prefix in subtype_prefixes.items():
                if code != agg and isinstance(code, str) and code.startswith(prefix):
                    has_subtypes.add(agg)

        if has_subtypes:
            pre_len = len(df)
            df = df[~df[source_col].isin(has_subtypes)]
            dropped = pre_len - len(df)
            if dropped > 0:
                logger.info(
                    "Dropped %d aggregate rows (%s) to avoid double-counting with subtypes",
                    dropped, has_subtypes,
                )

        df["source"] = df[source_col].map(SOURCE_MAP)
        # Log unmapped source codes
        unmapped = df[df["source"].isna() & df[source_col].notna()][source_col].unique()
        if len(unmapped) > 0:
            logger.warning("Unmapped energy source codes in capacity data: %s", unmapped)
    else:
        df["source"] = "Unknown"

    df = df[df["source"].notna()]

    # --- Filter to valid US states only (exclude Census divisions, US total) ---
    state_col = None
    for col in ["stateDescription", "stateId", "location"]:
        if col in df.columns:
            state_col = col
            break

    if state_col:
        # For stateId/location, we need the 2-letter codes
        if state_col in ("stateId", "location"):
            from ..transform.reliability import STATE_ABBR_TO_NAME
            valid_ids = set(STATE_ABBR_TO_NAME.keys())
            state_df = df[df[state_col].isin(valid_ids)]
        else:
            state_df = df[df[state_col].isin(US_STATES)]

        if state_df.empty:
            logger.warning("No valid state rows found in capacity data; using all rows")
            state_df = df
    else:
        state_df = df

    # National capacity by source and year (sum across valid states)
    national = (
        state_df.groupby(["period", "source"])[cap_col]
        .sum()
        .reset_index()
        .rename(columns={"period": "year", cap_col: "capacity_mw"})
        .sort_values(["source", "year"])
    )

    # Validation
    latest_year = int(national["year"].max())
    latest_total_gw = national[national["year"] == latest_year]["capacity_mw"].sum() / 1000
    if latest_total_gw < 1000 or latest_total_gw > 2000:
        logger.warning(
            "National capacity for %d is %.0f GW — outside expected range (1,000-2,000 GW)",
            latest_year, latest_total_gw,
        )

    return {
        "national": national.to_dict(orient="records"),
        "metadata": {
            "description": "Installed net summer generating capacity by energy source",
            "source": "EIA Operating Generator Capacity",
            "url": "https://www.eia.gov/electricity/data/eia860/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "MW",
        },
    }


def transform_co2_emissions(raw_generation: list[dict], raw_co2: list[dict]) -> dict:
    """Transform raw EIA generation and CO2 data into carbon intensity metrics.

    Args:
        raw_generation: Raw generation records (unused, kept for API compat).
        raw_co2: Raw CO2 emissions records (from emissions-by-state-by-fuel endpoint).

    Returns a dict with 'national' (list of {year, co2_emissions, carbon_intensity_lbs_per_mwh})
    and 'metadata'.
    """
    co2_df = pd.DataFrame(raw_co2)
    co2_df["co2-thousand-metric-tons"] = pd.to_numeric(
        co2_df.get("co2-thousand-metric-tons", pd.Series()), errors="coerce"
    )
    co2_df["co2-rate-lbs-mwh"] = pd.to_numeric(
        co2_df.get("co2-rate-lbs-mwh", pd.Series()), errors="coerce"
    )
    co2_df["period"] = pd.to_numeric(co2_df["period"], errors="coerce")
    co2_df = co2_df.dropna(subset=["co2-thousand-metric-tons", "period"])

    # Get fuel column
    fuel_col = None
    for col in ["fuelid", "fuelId", "fuel_id"]:
        if col in co2_df.columns:
            fuel_col = col
            break

    # Filter to "ALL" fuel rows (total across all fuels) to avoid double-counting
    if fuel_col:
        total_rows = co2_df[co2_df[fuel_col].isin(["ALL", "TOT", "Total"])]
        if len(total_rows) > 0:
            co2_df = total_rows

    # --- Filter to valid US states only (exclude Census divisions) ---
    state_col = None
    for col in ["stateDescription", "stateId", "location"]:
        if col in co2_df.columns:
            state_col = col
            break

    if state_col:
        # Check for US Total rows first
        us_total_df = co2_df[co2_df[state_col].isin(US_TOTAL_LABELS)]
        if not us_total_df.empty:
            # Use US Total directly for national CO2 rate
            co2_national = (
                us_total_df.groupby("period")
                .agg({"co2-thousand-metric-tons": "sum", "co2-rate-lbs-mwh": "mean"})
                .reset_index()
            )
        else:
            # Filter to valid states and compute generation-weighted average
            state_df = co2_df[co2_df[state_col].isin(US_STATES)]
            if state_df.empty:
                state_df = co2_df  # fallback

            # For CO2 rate, compute weighted average using CO2 total as proxy for generation
            def _weighted_rate(group):
                mask = group["co2-rate-lbs-mwh"].notna() & group["co2-thousand-metric-tons"].notna()
                g = group[mask]
                if g.empty:
                    return pd.Series({
                        "co2-thousand-metric-tons": group["co2-thousand-metric-tons"].sum(),
                        "co2-rate-lbs-mwh": group["co2-rate-lbs-mwh"].mean(),
                    })
                weights = g["co2-thousand-metric-tons"]
                total_weight = weights.sum()
                if total_weight == 0:
                    return pd.Series({
                        "co2-thousand-metric-tons": 0,
                        "co2-rate-lbs-mwh": g["co2-rate-lbs-mwh"].mean(),
                    })
                weighted_rate = (g["co2-rate-lbs-mwh"] * weights).sum() / total_weight
                return pd.Series({
                    "co2-thousand-metric-tons": total_weight,
                    "co2-rate-lbs-mwh": weighted_rate,
                })

            co2_national = (
                state_df.groupby("period")
                .apply(_weighted_rate, include_groups=False)
                .reset_index()
            )
    else:
        # No state column — aggregate all rows
        co2_national = (
            co2_df.groupby("period")
            .agg({"co2-thousand-metric-tons": "sum", "co2-rate-lbs-mwh": "mean"})
            .reset_index()
        )

    co2_national = co2_national.rename(columns={
        "period": "year",
        "co2-thousand-metric-tons": "co2_thousand_metric_tons",
        "co2-rate-lbs-mwh": "co2_rate_lbs_per_mwh",
    })

    # Convert lbs/MWh to kg/MWh for easier interpretation
    co2_national["carbon_intensity_kg_per_mwh"] = (
        co2_national["co2_rate_lbs_per_mwh"] * 0.453592
    ).round(2)

    co2_national = co2_national.sort_values("year")

    return {
        "national": co2_national[
            ["year", "co2_thousand_metric_tons", "co2_rate_lbs_per_mwh", "carbon_intensity_kg_per_mwh"]
        ].to_dict(orient="records"),
        "metadata": {
            "description": "Carbon intensity of electricity generation (CO2 emissions per MWh)",
            "source": "EIA State Electricity Profiles - Emissions by State by Fuel",
            "url": "https://www.eia.gov/electricity/state/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "kg CO2 per MWh (also lbs CO2 per MWh)",
        },
    }
