"""Main pipeline entry point. Fetches, transforms, and exports EIA data."""

import os
import sys
from dotenv import load_dotenv

from .fetch.electricity import fetch_retail_prices, fetch_demand, fetch_generation_by_source
from .fetch.fuels import fetch_coal_production, fetch_natural_gas_production, fetch_crude_oil_production
from .transform.prices import transform_retail_prices
from .transform.demand import transform_demand
from .transform.generation import transform_generation
from .transform.fuels import transform_fuels
from .transform.reliability import transform_reliability
from .export import write_json


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("EIA_API_KEY")
    if not api_key:
        print("Error: EIA_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    # --- Prices ---
    print("Fetching retail electricity prices...")
    raw_prices = fetch_retail_prices(api_key)
    print(f"  Got {len(raw_prices)} records")

    print("Transforming price data...")
    prices = transform_retail_prices(raw_prices)

    print("Exporting price JSON files...")
    write_json(prices["national"], "prices", "retail-prices-national.json")
    write_json(prices["by_state"], "prices", "retail-prices-by-state.json")
    write_json(prices["metadata"], "prices", "metadata.json")

    # --- Demand ---
    print("Fetching electricity demand (consumption)...")
    raw_demand = fetch_demand(api_key)
    print(f"  Got {len(raw_demand)} records")

    print("Transforming demand data...")
    demand = transform_demand(raw_demand)

    print("Exporting demand JSON files...")
    write_json(demand["national"], "demand", "consumption-national.json")
    write_json(demand["by_state"], "demand", "consumption-by-state.json")
    write_json(demand["metadata"], "demand", "metadata.json")

    # --- Generation ---
    print("Fetching electricity generation by source...")
    raw_generation = fetch_generation_by_source(api_key)
    print(f"  Got {len(raw_generation)} records")

    print("Transforming generation data...")
    generation = transform_generation(raw_generation)

    print("Exporting generation JSON files...")
    write_json(generation["national"], "generation", "generation-national.json")
    write_json(generation["by_state"], "generation", "generation-by-state.json")
    write_json(generation["renewable_share"], "generation", "renewable-share-by-state.json")
    write_json(generation["metadata"], "generation", "metadata.json")

    # --- Fossil Fuels ---
    print("Fetching coal production...")
    raw_coal = fetch_coal_production(api_key)
    print(f"  Got {len(raw_coal)} records")

    print("Fetching natural gas production...")
    raw_gas = fetch_natural_gas_production(api_key)
    print(f"  Got {len(raw_gas)} records")

    print("Fetching crude oil production...")
    raw_oil = fetch_crude_oil_production(api_key)
    print(f"  Got {len(raw_oil)} records")

    print("Transforming fuels data...")
    fuels = transform_fuels(raw_coal, raw_gas, raw_oil)

    print("Exporting fuels JSON files...")
    write_json(fuels["national"], "fuels", "production-national.json")
    write_json(fuels["by_state"], "fuels", "production-by-state.json")
    write_json(fuels["metadata"], "fuels", "metadata.json")

    # --- Reliability (sample data, no API fetch) ---
    print("Generating reliability sample data...")
    reliability = transform_reliability()

    print("Exporting reliability JSON files...")
    write_json(reliability["national"], "reliability", "saidi-national.json")
    write_json(reliability["by_state"], "reliability", "saidi-by-state.json")
    write_json(reliability["metadata"], "reliability", "metadata.json")

    print("Done! All data exported to site/static/data/")


if __name__ == "__main__":
    main()
