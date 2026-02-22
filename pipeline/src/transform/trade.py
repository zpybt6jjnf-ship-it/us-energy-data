"""Transform petroleum and natural gas trade data into chart-ready JSON."""
import pandas as pd


def transform_trade(petroleum_data: list[dict], gas_data: list[dict]) -> dict:
    """Transform trade data into imports/exports by fuel and year.

    Returns: {national: [{year, fuel, imports, exports, net_imports}], metadata: {...}}
    """
    records = []

    # Process petroleum
    pet_df = pd.DataFrame(petroleum_data)
    pet_df["value"] = pd.to_numeric(pet_df["value"], errors="coerce")
    pet_df["period"] = pd.to_numeric(pet_df["period"], errors="coerce")
    pet_df = pet_df.dropna(subset=["value", "period"])

    # Filter to thousand barrels per day (units contain MBBL/D)
    if "units" in pet_df.columns:
        pet_df = pet_df[pet_df["units"].str.contains("MBBL/D", na=False)]

    # Sum crude + products per year and direction
    pet_agg = (
        pet_df.groupby(["period", "direction"])["value"]
        .sum()
        .reset_index()
    )

    for year in pet_agg["period"].unique():
        year_data = pet_agg[pet_agg["period"] == year]
        imp = year_data[year_data["direction"] == "imports"]["value"].sum()
        exp = year_data[year_data["direction"] == "exports"]["value"].sum()
        records.append({
            "year": int(year),
            "fuel": "Petroleum",
            "imports": round(float(imp), 1),
            "exports": round(float(exp), 1),
            "net_imports": round(float(imp - exp), 1),
            "unit": "thousand barrels/day",
        })

    # Process natural gas
    gas_df = pd.DataFrame(gas_data)
    gas_df["value"] = pd.to_numeric(gas_df["value"], errors="coerce")
    gas_df["period"] = pd.to_numeric(gas_df["period"], errors="coerce")
    gas_df = gas_df.dropna(subset=["value", "period"])

    # Determine direction from process field
    if "process" in gas_df.columns:
        gas_df["direction"] = gas_df["process"].map({"IM0": "imports", "EEX": "exports"})
    elif "process-name" in gas_df.columns:
        gas_df["direction"] = gas_df["process-name"].str.lower()

    gas_agg = (
        gas_df.groupby(["period", "direction"])["value"]
        .sum()
        .reset_index()
    )

    for year in gas_agg["period"].unique():
        year_data = gas_agg[gas_agg["period"] == year]
        imp = year_data[year_data["direction"] == "imports"]["value"].sum()
        exp = year_data[year_data["direction"] == "exports"]["value"].sum()
        records.append({
            "year": int(year),
            "fuel": "Natural Gas",
            "imports": round(float(imp), 1),
            "exports": round(float(exp), 1),
            "net_imports": round(float(imp - exp), 1),
            "unit": "million cubic feet",
        })

    result = sorted(records, key=lambda x: (x["fuel"], x["year"]))

    return {
        "national": result,
        "metadata": {
            "description": "US petroleum and natural gas imports and exports",
            "source": "EIA Petroleum Movement and Natural Gas Summary",
            "url": "https://www.eia.gov/",
            "last_updated": pd.Timestamp.now().isoformat(),
        },
    }
