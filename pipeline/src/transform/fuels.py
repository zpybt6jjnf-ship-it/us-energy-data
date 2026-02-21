"""Transform raw EIA fossil fuel production data into chart-ready JSON."""

import pandas as pd

# Map uppercase state names to title case
US_STATES = {
    "ALABAMA": "Alabama", "ALASKA": "Alaska", "ARIZONA": "Arizona", "ARKANSAS": "Arkansas",
    "CALIFORNIA": "California", "COLORADO": "Colorado", "CONNECTICUT": "Connecticut",
    "DELAWARE": "Delaware", "FLORIDA": "Florida", "GEORGIA": "Georgia", "HAWAII": "Hawaii",
    "IDAHO": "Idaho", "ILLINOIS": "Illinois", "INDIANA": "Indiana", "IOWA": "Iowa",
    "KANSAS": "Kansas", "KENTUCKY": "Kentucky", "LOUISIANA": "Louisiana", "MAINE": "Maine",
    "MARYLAND": "Maryland", "MASSACHUSETTS": "Massachusetts", "MICHIGAN": "Michigan",
    "MINNESOTA": "Minnesota", "MISSISSIPPI": "Mississippi", "MISSOURI": "Missouri",
    "MONTANA": "Montana", "NEBRASKA": "Nebraska", "NEVADA": "Nevada",
    "NEW HAMPSHIRE": "New Hampshire", "NEW JERSEY": "New Jersey", "NEW MEXICO": "New Mexico",
    "NEW YORK": "New York", "NORTH CAROLINA": "North Carolina", "NORTH DAKOTA": "North Dakota",
    "OHIO": "Ohio", "OKLAHOMA": "Oklahoma", "OREGON": "Oregon", "PENNSYLVANIA": "Pennsylvania",
    "RHODE ISLAND": "Rhode Island", "SOUTH CAROLINA": "South Carolina",
    "SOUTH DAKOTA": "South Dakota", "TENNESSEE": "Tennessee", "TEXAS": "Texas",
    "UTAH": "Utah", "VERMONT": "Vermont", "VIRGINIA": "Virginia", "WASHINGTON": "Washington",
    "WEST VIRGINIA": "West Virginia", "WISCONSIN": "Wisconsin", "WYOMING": "Wyoming",
}

# State abbreviation to name mapping for petroleum data (USA-XX format)
STATE_ABBR = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


def _normalize_state_name(name: str) -> str | None:
    """Normalize a state name to title case. Returns None for non-state entries."""
    if not name or not isinstance(name, str):
        return None
    name = name.strip()
    # Handle "USA-XX" format from petroleum data
    if name.startswith("USA-"):
        abbr = name[4:]
        return STATE_ABBR.get(abbr)
    # Handle uppercase names from natural gas data
    upper = name.upper()
    if upper in US_STATES:
        return US_STATES[upper]
    # Handle title case already
    if name in US_STATES.values():
        return name
    return None


def _clean_coal(raw: list[dict]) -> pd.DataFrame:
    """Clean coal mine production data."""
    df = pd.DataFrame(raw)
    if df.empty:
        return pd.DataFrame(columns=["state", "year", "fuel", "production", "unit"])
    df["production"] = pd.to_numeric(df.get("production", pd.Series()), errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["production", "period"])

    # Find the state column
    state_col = None
    for col in ["mine-state-name", "stateDescription", "mine_state_name"]:
        if col in df.columns:
            state_col = col
            break
    if state_col is None:
        for col in df.columns:
            if "state" in col.lower() and "id" not in col.lower():
                state_col = col
                break
    if state_col is None:
        return pd.DataFrame(columns=["state", "year", "fuel", "production", "unit"])

    df["_state"] = df[state_col].apply(_normalize_state_name)
    df = df.dropna(subset=["_state"])

    grouped = (
        df.groupby(["_state", "period"])["production"]
        .sum()
        .reset_index()
        .rename(columns={"_state": "state", "period": "year"})
    )
    grouped["fuel"] = "Coal"
    grouped["unit"] = "short tons"
    return grouped


def _clean_natural_gas(raw: list[dict]) -> pd.DataFrame:
    """Clean natural gas marketed production data."""
    df = pd.DataFrame(raw)
    if df.empty:
        return pd.DataFrame(columns=["state", "year", "fuel", "production", "unit"])
    df["value"] = pd.to_numeric(df.get("value", pd.Series()), errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["value", "period"])

    state_col = "area-name" if "area-name" in df.columns else "stateDescription"
    df["_state"] = df[state_col].apply(_normalize_state_name)
    df = df.dropna(subset=["_state"])

    grouped = (
        df.groupby(["_state", "period"])["value"]
        .sum()
        .reset_index()
        .rename(columns={"_state": "state", "period": "year", "value": "production"})
    )
    grouped["fuel"] = "Natural Gas"
    grouped["unit"] = "million cubic feet"
    return grouped


def _clean_crude_oil(raw: list[dict]) -> pd.DataFrame:
    """Clean crude oil field production data."""
    df = pd.DataFrame(raw)
    if df.empty:
        return pd.DataFrame(columns=["state", "year", "fuel", "production", "unit"])
    df["value"] = pd.to_numeric(df.get("value", pd.Series()), errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df = df.dropna(subset=["value", "period"])

    state_col = "area-name" if "area-name" in df.columns else "stateDescription"
    df["_state"] = df[state_col].apply(_normalize_state_name)
    df = df.dropna(subset=["_state"])

    # Filter to absolute production (MBBL), not rates (MBBL/D)
    if "units" in df.columns:
        df = df[df["units"] == "MBBL"]

    grouped = (
        df.groupby(["_state", "period"])["value"]
        .sum()
        .reset_index()
        .rename(columns={"_state": "state", "period": "year", "value": "production"})
    )
    grouped["fuel"] = "Crude Oil"
    grouped["unit"] = "thousand barrels"
    return grouped


def transform_fuels(raw_coal: list[dict], raw_gas: list[dict], raw_oil: list[dict]) -> dict:
    """Transform raw fuel production records into structured output."""
    coal = _clean_coal(raw_coal)
    gas = _clean_natural_gas(raw_gas)
    oil = _clean_crude_oil(raw_oil)

    combined = pd.concat([coal, gas, oil], ignore_index=True)

    # National totals by fuel and year
    national = (
        combined.groupby(["year", "fuel"])["production"]
        .sum()
        .reset_index()
        .sort_values(["fuel", "year"])
    )

    # State-level
    by_state = combined.sort_values(["state", "fuel", "year"])

    return {
        "national": national.to_dict(orient="records"),
        "by_state": by_state[["state", "year", "fuel", "production", "unit"]].to_dict(orient="records"),
        "metadata": {
            "source": "EIA Coal, Natural Gas, and Petroleum Data",
            "url": "https://www.eia.gov/",
            "last_updated": pd.Timestamp.now().isoformat(),
            "fuels": {
                "Coal": "short tons",
                "Natural Gas": "million cubic feet",
                "Crude Oil": "thousand barrels",
            },
        },
    }
