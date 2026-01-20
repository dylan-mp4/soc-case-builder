"""
Configuration manager for SOC Case Builder.
Handles loading, saving, and migrating settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

# Get the directory where this file is located
CONFIG_DIR = Path(__file__).parent.parent / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
DEFAULTS_FILE = CONFIG_DIR / "defaults.json"

# Legacy settings locations (for migration)
LEGACY_SETTINGS_DIR = Path(__file__).parent.parent.parent  # src/ directory
LEGACY_SETTINGS_FILE = LEGACY_SETTINGS_DIR / "settings.json"
LEGACY_CLIENTS_FILE = LEGACY_SETTINGS_DIR.parent / "clients.csv"
LEGACY_ENTITIES_FILE = LEGACY_SETTINGS_DIR / "entities.json"
LEGACY_CUSTOM_DICT_FILE = LEGACY_SETTINGS_DIR.parent / "custom_dict.txt"


def load_defaults() -> Dict[str, Any]:
    """Load default settings from defaults.json."""
    if DEFAULTS_FILE.exists():
        try:
            with open(DEFAULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading defaults: {e}")
            return {}
    return {}


def load_settings() -> Dict[str, Any]:
    """
    Load settings from settings.json.
    If file doesn't exist, loads defaults and performs migration if needed.
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return load_defaults()
    else:
        # Perform migration from legacy settings if they exist
        settings = migrate_legacy_settings()
        save_settings(settings)
        return settings


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Save settings to settings.json.
    Returns True if successful, False otherwise.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def migrate_legacy_settings() -> Dict[str, Any]:
    """
    Migrate settings from old PyQt6 structure to new flat JSON structure.
    Returns merged settings dict.
    """
    settings = load_defaults()

    # Migrate from old settings.json
    if LEGACY_SETTINGS_FILE.exists():
        try:
            with open(LEGACY_SETTINGS_FILE, "r", encoding="utf-8") as f:
                legacy = json.load(f)
                # Copy over known keys (skip theme-related keys)
                if "entity_ttl_days" in legacy:
                    settings["entity_ttl_days"] = legacy["entity_ttl_days"]
        except Exception as e:
            print(f"Error migrating legacy settings.json: {e}")

    # Migrate from clients.csv
    if LEGACY_CLIENTS_FILE.exists():
        try:
            with open(LEGACY_CLIENTS_FILE, "r", encoding="utf-8") as f:
                clients = [line.strip() for line in f.readlines() if line.strip()]
                if clients:
                    settings["clients"] = clients
        except Exception as e:
            print(f"Error migrating legacy clients.csv: {e}")

    # Migrate from entities.json
    if LEGACY_ENTITIES_FILE.exists():
        try:
            with open(LEGACY_ENTITIES_FILE, "r", encoding="utf-8") as f:
                entities = json.load(f)
                if isinstance(entities, list):
                    settings["entities"] = entities
        except Exception as e:
            print(f"Error migrating legacy entities.json: {e}")

    # Migrate from custom_dict.txt
    if LEGACY_CUSTOM_DICT_FILE.exists():
        try:
            with open(LEGACY_CUSTOM_DICT_FILE, "r", encoding="utf-8") as f:
                custom_dict = [line.strip() for line in f.readlines() if line.strip()]
                if custom_dict:
                    settings["custom_dict"] = custom_dict
        except Exception as e:
            print(f"Error migrating legacy custom_dict.txt: {e}")

    # Mark as migrated (no longer first time)
    settings["first_time"] = False

    return settings


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value."""
    settings = load_settings()
    return settings.get(key, default)


def set_setting(key: str, value: Any) -> bool:
    """
    Set a specific setting value and save to file.
    Returns True if successful, False otherwise.
    """
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


def update_settings(updates: Dict[str, Any]) -> bool:
    """
    Update multiple settings at once and save to file.
    Returns True if successful, False otherwise.
    """
    settings = load_settings()
    settings.update(updates)
    return save_settings(settings)
