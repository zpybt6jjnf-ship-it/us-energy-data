"""Transform raw EIA capacity and CO2 emissions data into chart-ready JSON."""

import pandas as pd


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
    # state-electricity-profiles/capability endpoint codes
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
}


def transform_capacity(raw_data: list[dict]) -> dict:
    """Transform raw EIA capacity records into structured output.

    Returns a dict with 'national' (list of {year, source, capacity_mw})
    and 'metadata'.
    """
    df = pd.DataFrame(raw_data)

    # Detect capacity column: "capability" (state-profiles) or "nameplate-capacity-mw" (generator inventory)
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

    if source_col is not None:
        df["source"] = df[source_col].map(SOURCE_MAP)
    else:
        df["source"] = "Unknown"

    df = df[df["source"].notna()]

    # National capacity by source and year
    national = (
        df.groupby(["period", "source"])[cap_col]
        .sum()
        .reset_index()
        .rename(columns={"period": "year", cap_col: "capacity_mw"})
        .sort_values(["source", "year"])
    )

    return {
        "national": national.to_dict(orient="records"),
        "metadata": {
            "description": "Installed nameplate generating capacity by energy source",
            "source": "EIA Operating Generator Capacity",
            "url": "https://www.eia.gov/electricity/data/eia860/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "MW",
        },
    }


def transform_co2_emissions(raw_generation: list[dict], raw_co2: list[dict]) -> dict:
    """Transform raw EIA generation and CO2 data into carbon intensity metrics.

    Args:
        raw_generation: Raw generation records (from fetch_generation_by_source).
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

    # Aggregate all fuels per year for national total
    if fuel_col:
        # Filter to "ALL" or "TOT" if available, otherwise sum all fuels
        total_rows = co2_df[co2_df[fuel_col].isin(["ALL", "TOT", "Total"])]
        if len(total_rows) > 0:
            co2_df = total_rows
        else:
            # Sum across fuels — but only count each state once
            pass

    # National: sum CO2 across states, weighted-average rate
    co2_national = (
        co2_df.groupby("period")
        .agg({"co2-thousand-metric-tons": "sum", "co2-rate-lbs-mwh": "mean"})
        .reset_index()
        .rename(columns={
            "period": "year",
            "co2-thousand-metric-tons": "co2_thousand_metric_tons",
            "co2-rate-lbs-mwh": "co2_rate_lbs_per_mwh",
        })
    )

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
