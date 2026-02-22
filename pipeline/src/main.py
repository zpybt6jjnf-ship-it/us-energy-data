"""Main pipeline entry point. Fetches, transforms, and exports EIA data."""

import logging
import os
import sys
import traceback
from dotenv import load_dotenv

# Configure logging for pipeline warnings (unmapped values, validation failures)
logging.basicConfig(
    level=logging.INFO,
    format="  [%(levelname)s] %(name)s: %(message)s",
)

from .fetch.electricity import fetch_retail_prices, fetch_demand, fetch_generation_by_source
from .fetch.fuels import fetch_coal_production, fetch_natural_gas_production, fetch_crude_oil_production
from .fetch.capacity import fetch_capacity_by_source, fetch_co2_emissions, fetch_fuel_consumption, fetch_battery_storage
from .fetch.census import fetch_state_population
from .fetch.trade import fetch_petroleum_trade, fetch_natural_gas_trade
from .fetch.reliability import fetch_reliability
from .transform.prices import transform_retail_prices
from .transform.demand import transform_demand
from .transform.generation import transform_generation
from .transform.fuels import transform_fuels
from .transform.reliability import transform_reliability
from .transform.capacity import transform_capacity, transform_co2_emissions
from .transform.fuel_consumption import transform_fuel_consumption
from .transform.load_growth import transform_load_growth
from .transform.per_capita import transform_per_capita
from .transform.bills import transform_bills
from .transform.capacity_changes import transform_capacity_changes
from .transform.storage import transform_storage
from .transform.trade import transform_trade
from .export import write_json


def run_stage(name: str, fn) -> bool:
    """Run a pipeline stage with error handling. Returns True on success, False on failure."""
    try:
        fn()
        return True
    except Exception:
        print(f"\n  [WARN] Stage '{name}' failed:")
        traceback.print_exc()
        print(f"  Continuing with remaining stages...\n")
        return False


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("EIA_API_KEY")
    if not api_key:
        print("Error: EIA_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    errors: list[str] = []

    # --- Core Pipelines (these must succeed) ---

    # Prices
    print("Fetching retail electricity prices...")
    raw_prices = fetch_retail_prices(api_key)
    print(f"  Got {len(raw_prices)} records")

    print("Transforming price data...")
    prices = transform_retail_prices(raw_prices)

    print("Exporting price JSON files...")
    write_json(prices["national"], "prices", "retail-prices-national.json")
    write_json(prices["by_state"], "prices", "retail-prices-by-state.json")
    write_json(prices["metadata"], "prices", "metadata.json")

    # Household Electricity Bills (derived from prices)
    def stage_bills():
        print("Transforming household electricity bills...")
        bills = transform_bills(prices["national"])
        print(f"  Got {len(bills['national'])} records")
        write_json(bills["national"], "bills", "household-bills-national.json")
        write_json(bills["metadata"], "bills", "household-bills-metadata.json")

    if not run_stage("bills", stage_bills):
        errors.append("bills")

    # Demand
    print("Fetching electricity demand (consumption)...")
    raw_demand = fetch_demand(api_key)
    print(f"  Got {len(raw_demand)} records")

    print("Transforming demand data...")
    demand = transform_demand(raw_demand)

    print("Exporting demand JSON files...")
    write_json(demand["national"], "demand", "consumption-national.json")
    write_json(demand["by_state"], "demand", "consumption-by-state.json")
    write_json(demand["metadata"], "demand", "metadata.json")

    # Generation
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

    # Fossil Fuels
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

    # Reliability (EIA-861 data download)
    def stage_reliability():
        print("Fetching EIA-861 reliability data (SAIDI/SAIFI)...")
        raw_reliability = fetch_reliability()
        print(f"  Got {len(raw_reliability)} utility-level records")
        print("Transforming reliability data...")
        reliability = transform_reliability(raw_reliability)
        print(f"  National trend: {len(reliability['national'])} years")
        print(f"  State data: {len(reliability['by_state'])} states")
        print("Exporting reliability JSON files...")
        write_json(reliability["national"], "reliability", "saidi-national.json")
        write_json(reliability["by_state"], "reliability", "saidi-by-state.json")
        write_json(reliability["by_state_trend"], "reliability", "saidi-by-state-trend.json")
        write_json(reliability["metadata"], "reliability", "metadata.json")

    if not run_stage("reliability", stage_reliability):
        errors.append("reliability")

    # --- New Pipeline Stages (non-blocking) ---

    # Capacity
    def stage_capacity():
        print("Fetching generating capacity by source...")
        raw_capacity = fetch_capacity_by_source(api_key)
        print(f"  Got {len(raw_capacity)} records")
        print("Transforming capacity data...")
        capacity = transform_capacity(raw_capacity)
        print("Exporting capacity JSON files...")
        write_json(capacity["national"], "generation", "capacity-national.json")
        write_json(capacity["metadata"], "generation", "capacity-metadata.json")

    if not run_stage("capacity", stage_capacity):
        errors.append("capacity")

    # Capacity Additions / Retirements (derived from capacity data)
    def stage_capacity_changes():
        import json
        # Read existing capacity data from the file just written
        cap_path = os.path.join(
            os.path.dirname(__file__),
            '../../site/static/data/generation/capacity-national.json',
        )
        with open(cap_path) as f:
            cap_data = json.load(f)
        print("Transforming capacity additions/retirements...")
        changes = transform_capacity_changes(cap_data)
        print(f"  Got {len(changes['national'])} records")
        write_json(changes["national"], "generation", "capacity-changes-national.json")
        write_json(changes["metadata"], "generation", "capacity-changes-metadata.json")

    if not run_stage("capacity_changes", stage_capacity_changes):
        errors.append("capacity_changes")

    # Battery Storage
    def stage_storage():
        print("Fetching battery storage capacity...")
        raw_storage = fetch_battery_storage(api_key)
        print(f"  Got {len(raw_storage)} records")
        print("Transforming storage data...")
        storage = transform_storage(raw_storage)
        print(f"  Got {len(storage['national'])} storage records")
        write_json(storage["national"], "generation", "storage-national.json")
        write_json(storage["metadata"], "generation", "storage-metadata.json")

    if not run_stage("storage", stage_storage):
        errors.append("storage")

    # CO2 Emissions / Carbon Intensity
    def stage_co2():
        print("Fetching CO2 emissions from electricity generation...")
        raw_co2 = fetch_co2_emissions(api_key)
        print(f"  Got {len(raw_co2)} records")
        print("Transforming carbon intensity data...")
        carbon_intensity = transform_co2_emissions([], raw_co2)
        print("Exporting carbon intensity JSON files...")
        write_json(carbon_intensity["national"], "generation", "carbon-intensity-national.json")
        write_json(carbon_intensity["metadata"], "generation", "carbon-intensity-metadata.json")

    if not run_stage("co2_emissions", stage_co2):
        errors.append("co2_emissions")

    # Fuel Consumption for Electricity Generation
    def stage_fuel_consumption():
        print("Fetching fuel consumption for electricity generation...")
        raw_fuel_consumption = fetch_fuel_consumption(api_key)
        print(f"  Got {len(raw_fuel_consumption)} records")
        print("Transforming fuel consumption data...")
        fc = transform_fuel_consumption(raw_fuel_consumption)
        print(f"  Aggregated to {len(fc['national'])} records")
        print("Exporting fuel consumption JSON files...")
        write_json(fc["national"], "fuels", "fuel-consumption-national.json")
        write_json(fc["metadata"], "fuels", "fuel-consumption-metadata.json")

    if not run_stage("fuel_consumption", stage_fuel_consumption):
        errors.append("fuel_consumption")

    # Petroleum & Natural Gas Trade (Imports/Exports)
    def stage_trade():
        print("Fetching petroleum trade data...")
        raw_pet_trade = fetch_petroleum_trade(api_key)
        print(f"  Got {len(raw_pet_trade)} petroleum trade records")
        print("Fetching natural gas trade data...")
        raw_gas_trade = fetch_natural_gas_trade(api_key)
        print(f"  Got {len(raw_gas_trade)} natural gas trade records")
        print("Transforming trade data...")
        trade = transform_trade(raw_pet_trade, raw_gas_trade)
        print(f"  Got {len(trade['national'])} aggregated records")
        write_json(trade["national"], "fuels", "trade-national.json")
        write_json(trade["metadata"], "fuels", "trade-metadata.json")

    if not run_stage("trade", stage_trade):
        errors.append("trade")

    # Load Growth (derived from demand data, no API fetch)
    def stage_load_growth():
        print("Transforming load growth data...")
        load_growth = transform_load_growth(demand["national"])
        print("Exporting load growth JSON files...")
        write_json(load_growth["national"], "demand", "load-growth-national.json")
        write_json(load_growth["metadata"], "demand", "load-growth-metadata.json")

    if not run_stage("load_growth", stage_load_growth):
        errors.append("load_growth")

    # Per-Capita Consumption
    def stage_per_capita():
        print("Fetching Census population estimates...")
        population = fetch_state_population()
        print(f"  Got {len(population)} state records")
        print("Transforming per-capita consumption data...")
        per_capita = transform_per_capita(demand["by_state"], population)
        print("Exporting per-capita JSON files...")
        write_json(per_capita["by_state"], "demand", "per-capita-by-state.json")
        write_json(per_capita["metadata"], "demand", "per-capita-metadata.json")

    if not run_stage("per_capita", stage_per_capita):
        errors.append("per_capita")

    # --- Summary ---
    if errors:
        print(f"\nDone with {len(errors)} warning(s): {', '.join(errors)} failed.")
        print("Core data (prices, demand, generation, fuels, reliability) exported successfully.")
    else:
        print("\nDone! All data exported to site/static/data/")


if __name__ == "__main__":
    main()
