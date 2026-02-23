"""Export transformed data as JSON files to the site's static data directory."""

import json
from pathlib import Path

SITE_DATA_DIR = Path(__file__).parent.parent.parent / "site" / "static" / "data"


def _round_floats(obj, decimals: int = 1):
    """Recursively round floating-point values to eliminate serialization artifacts.

    Uses 1 decimal for most values, 0 decimals for values > 10000 (large production figures).
    """
    if isinstance(obj, float):
        if abs(obj) > 10000:
            return round(obj, 0)
        return round(obj, decimals)
    if isinstance(obj, dict):
        return {k: _round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(item, decimals) for item in obj]
    return obj


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
    cleaned = _round_floats(data)
    output_path.write_text(json.dumps(cleaned, indent=2, default=str), encoding="utf-8")
    return output_path
