"""Shared constants for the EIA data pipeline."""

# Valid US state names (50 states + DC) as they appear in EIA API responses.
# Used to filter out Census divisions, regional aggregates, and US totals
# from state-level data.
US_STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California",
    "Colorado", "Connecticut", "Delaware", "District of Columbia", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana",
    "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",
    "Wyoming",
}

# The EIA API uses "US-Total", "US-TOTAL", or "US" for national aggregates
US_TOTAL_LABELS = {"US Total", "US-Total", "US-TOTAL", "United States", "US", "U.S.", "U.S. Total"}
