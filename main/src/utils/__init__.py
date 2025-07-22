import json
from typing import Any


def load_config(config_path: str = "config/config.json") -> dict:
    """Load configuration from a JSON file and return as a dictionary."""
    with open(config_path, "r") as f:
        return json.load(f)


def get_config_value(config: dict, section: str, key: str, default: Any = None) -> Any:
    """Retrieve a value from the loaded config."""
    return config.get(section, {}).get(key, default)
