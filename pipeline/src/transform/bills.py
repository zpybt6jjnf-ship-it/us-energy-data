"""Compute average household electricity bills from residential price data."""

import pandas as pd

CPI_TABLE = {
    2001: 67.1, 2002: 68.2, 2003: 69.7, 2004: 71.6, 2005: 74.0,
    2006: 76.3, 2007: 78.5, 2008: 81.5, 2009: 81.2, 2010: 82.5,
    2011: 85.1, 2012: 86.9, 2013: 88.1, 2014: 89.6, 2015: 89.7,
    2016: 90.8, 2017: 92.7, 2018: 95.0, 2019: 96.7, 2020: 97.9,
    2021: 102.5, 2022: 110.7, 2023: 114.3, 2024: 117.4,
    2025: 120.2, 2026: 122.8,  # BLS projections (~2.4% annual)
}

AVG_MONTHLY_CONSUMPTION_KWH = 900


def transform_bills(national_prices: list[dict]) -> dict:
    """Compute average monthly household electricity bills.

    Args:
        national_prices: Already-transformed national price records with
            keys {year, sector, price}. Price is in cents/kWh.

    Returns:
        Dict with 'national' (list of bill records) and 'metadata'.
    """
    df = pd.DataFrame(national_prices)
    residential = df[df["sector"] == "Residential"].copy()

    records = []
    for _, row in residential.iterrows():
        year = int(row["year"])
        price = float(row["price"])

        # Average monthly bill in nominal dollars
        nominal_bill = round(price * AVG_MONTHLY_CONSUMPTION_KWH / 100, 2)

        # Inflation-adjusted bill in 2024 dollars
        cpi_year = CPI_TABLE.get(year)
        if cpi_year is not None:
            real_bill = round(nominal_bill * (CPI_TABLE[2024] / cpi_year), 2)
        else:
            real_bill = None

        records.append({
            "year": year,
            "nominal_bill": nominal_bill,
            "real_bill": real_bill,
        })

    records.sort(key=lambda r: r["year"])

    return {
        "national": records,
        "metadata": {
            "source": "EIA Electricity Retail Sales + CPI-U",
            "url": "https://www.eia.gov/electricity/data.php",
            "last_updated": pd.Timestamp.now().isoformat(),
            "unit": "dollars per month",
            "notes": (
                "Average monthly bill = avg residential price (cents/kWh) "
                f"x {AVG_MONTHLY_CONSUMPTION_KWH} kWh / 100. "
                "Real values adjusted to 2024 dollars using CPI-U annual averages."
            ),
        },
    }
