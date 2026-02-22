"""Fetch EIA-861 reliability data (SAIDI/SAIFI) from downloadable ZIP files.

The EIA API v2 does not expose reliability metrics. Instead, we download
annual EIA-861 ZIP files containing Reliability_YYYY.xlsx workbooks and
parse utility-level data from the 'Reliability_States' sheet.

Data available: 2013-2024 (reliability reporting started with the 2013 survey).
"""

import io
import time
import zipfile
from datetime import datetime

import pandas as pd
import requests

# URL patterns — try current first, then archive
CURRENT_URL = "https://www.eia.gov/electricity/data/eia861/zip/f861{year}.zip"
ARCHIVE_URL = "https://www.eia.gov/electricity/data/eia861/archive/zip/f861{year}.zip"

# Canonical column names assigned by position (column names vary across years)
UTILITY_COLUMNS = [
    "data_year", "utility_number", "utility_name", "state", "ownership",
    # IEEE Standard — All Events (With Major Event Days)
    "ieee_saidi_with_med", "ieee_saifi_with_med", "ieee_caidi_with_med",
    # IEEE Standard — Without Major Event Days
    "ieee_saidi_no_med", "ieee_saifi_no_med", "ieee_caidi_no_med",
    # IEEE Standard — Loss of Supply Removed (With MED)
    "ieee_saidi_los", "ieee_saifi_los", "ieee_caidi_los",
    # IEEE metadata
    "ieee_customers", "ieee_highest_voltage", "ieee_auto_recorded",
    # Other Standard — All Events (With MED)
    "other_saidi_with_med", "other_saifi_with_med", "other_caidi_with_med",
    # Other Standard — Without Major Event Days
    "other_saidi_no_med", "other_saifi_no_med", "other_caidi_no_med",
    # Other metadata
    "other_customers", "other_inactive_included", "other_momentary",
    "other_highest_voltage", "other_auto_recorded",
]

# Years with EIA-861 reliability data (dynamically extends to current year)
RELIABILITY_YEARS = range(2013, datetime.now().year + 1)

# Numeric columns that should be coerced to float
NUMERIC_COLS = [
    "ieee_saidi_with_med", "ieee_saifi_with_med", "ieee_caidi_with_med",
    "ieee_saidi_no_med", "ieee_saifi_no_med", "ieee_caidi_no_med",
    "ieee_saidi_los", "ieee_saifi_los", "ieee_caidi_los",
    "ieee_customers",
    "other_saidi_with_med", "other_saifi_with_med", "other_caidi_with_med",
    "other_saidi_no_med", "other_saifi_no_med", "other_caidi_no_med",
    "other_customers",
]


def _download_zip(year: int) -> bytes:
    """Download the EIA-861 ZIP for a given year. Tries current URL first, then archive."""
    for url_template in [CURRENT_URL, ARCHIVE_URL]:
        url = url_template.format(year=year)
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                content_type = resp.headers.get("Content-Type", "")
                # EIA returns HTML (not a ZIP) for non-archive URLs of older years
                if "text/html" in content_type:
                    continue
                return resp.content
        except requests.RequestException:
            continue
    raise RuntimeError(f"Could not download EIA-861 data for {year}")


def _find_reliability_file(zf: zipfile.ZipFile, year: int) -> str:
    """Find the reliability file inside the ZIP (name varies slightly by year)."""
    for name in zf.namelist():
        lower = name.lower()
        if "reliability" in lower and lower.endswith(".xlsx"):
            return name
    raise FileNotFoundError(f"No Reliability XLSX found in ZIP for {year}")


def _parse_reliability_xlsx(data: bytes, year: int) -> pd.DataFrame:
    """Parse utility-level reliability data from the XLSX file inside a ZIP."""
    zf = zipfile.ZipFile(io.BytesIO(data))
    xlsx_name = _find_reliability_file(zf, year)

    with zf.open(xlsx_name) as f:
        xlsx_bytes = f.read()

    # Read the Reliability_States sheet (first sheet), skip merged header rows
    df = pd.read_excel(
        io.BytesIO(xlsx_bytes),
        sheet_name=0,  # Reliability_States is always the first sheet
        skiprows=2,    # Skip merged header row + sub-header row
        header=None,
        engine="openpyxl",
    )

    # The 2019 file has an extra "Short Form" column at position 5.
    # Detect and drop it so positions align with UTILITY_COLUMNS.
    if len(df.columns) == 29:
        df = df.drop(columns=[df.columns[5]])
        df.columns = range(len(df.columns))  # Reset to integer index

    # Assign canonical column names (trim to available columns)
    n_cols = min(len(UTILITY_COLUMNS), len(df.columns))
    df = df.iloc[:, :n_cols]
    df.columns = UTILITY_COLUMNS[:n_cols]

    # Replace "." (EIA's missing value marker) with NaN
    df = df.replace(".", pd.NA)

    # Coerce numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure data_year is set
    if "data_year" in df.columns:
        df["data_year"] = pd.to_numeric(df["data_year"], errors="coerce").fillna(year).astype(int)
    else:
        df["data_year"] = year

    return df


def fetch_reliability(years: range | list[int] | None = None) -> pd.DataFrame:
    """Download and parse EIA-861 reliability data for all available years.

    Returns a DataFrame of utility-level records with canonical column names.
    """
    if years is None:
        years = RELIABILITY_YEARS

    frames: list[pd.DataFrame] = []

    for year in years:
        print(f"  Downloading EIA-861 for {year}...")
        try:
            zip_data = _download_zip(year)
            df = _parse_reliability_xlsx(zip_data, year)
            frames.append(df)
            print(f"    {len(df)} utility records")
        except Exception as e:
            print(f"    [WARN] Skipping {year}: {e}")
        time.sleep(0.3)  # Be polite to EIA servers

    if not frames:
        raise RuntimeError("No EIA-861 reliability data could be fetched")

    return pd.concat(frames, ignore_index=True)
