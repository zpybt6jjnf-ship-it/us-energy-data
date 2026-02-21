"""Export transformed data as JSON files to the site's static data directory."""

import json
from pathlib import Path

SITE_DATA_DIR = Path(__file__).parent.parent.parent / "site" / "static" / "data"


def write_json(data: dict | list, *path_parts: str) -> Path:
    """Write data as JSON to the site's static data directory.

    Args:
        data: The data to serialize.
        *path_parts: Path segments relative to the data dir (e.g., 'prices', 'retail-prices.json').

    Returns:
        The path to the written file.
    """
    output_path = SITE_DATA_DIR.joinpath(*path_parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return output_path
