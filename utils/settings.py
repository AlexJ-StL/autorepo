import json
import os
from typing import Any, Dict, List, Optional

class Settings:
    def __init__(self):
        self._settings: Dict[str, Any] = {
            "schedule": {
                "enabled": False,
                "days": ["Mon", "Wed", "Fri"],
                "hour": 9,
                "minute": 0,
                "notification_time": "5 minutes", # Renamed for clarity
            },
            "notifications": {
                "enabled": True,
                "sound": True,
            },
            "application": {
                "theme": "light",
                "max_depth": 2,
                "auto_save": True,
                "last_directory": "",
                "log_format": "JSON", # Note: This setting is now ignored by the standard logging setup
                "log_retention": 30 # Note: This setting is now ignored by the standard logging setup
            }
        }
        self._settings_path = "settings.json"
        self.load_settings()

    def _get_nested_value(self, keys: List[str], data: Dict[str, Any], default: Any = None) -> Any:
        """Helper to get a value from a nested dictionary using a list of keys."""
        if not keys:
            return data

        current_key = keys[0]
        if current_key in data:
            if len(keys) == 1:
                return data[current_key]
            elif isinstance(data[current_key], dict):
                return self._get_nested_value(keys[1:], data[current_key], default)
        return default

    def _set_nested_value(self, keys: List[str], data: Dict[str, Any], value: Any) -> None:
        """Helper to set a value in a nested dictionary using a list of keys."""
        if not keys:
            return

        current_key = keys[0]
        if len(keys) == 1:
            data[current_key] = value
        elif current_key in data and isinstance(data[current_key], dict):
            self._set_nested_value(keys[1:], data[current_key], value)
        else:
            # Create nested dictionaries if they don't exist
            data[current_key] = {}
            self._set_nested_value(keys[1:], data[current_key], value)


    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self._settings_path):
            try:
                with open(self._settings_path, "r") as file:
                    loaded_settings = json.load(file)
                    # Simple update for top-level keys, could be improved for deep merge
                    self._settings.update(loaded_settings)
            except json.JSONDecodeError:
                # Handle corrupted settings file
                print(f"Warning: Could not decode settings.json. Using default settings.")
            except Exception as e:
                print(f"Error loading settings: {e}")


    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self._settings_path, "w") as file:
                json.dump(self._settings, file, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation for nested keys (e.g., "schedule.enabled").
        """
        keys = key.split('.')
        return self._get_nested_value(keys, self._settings, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value using dot notation for nested keys (e.g., "schedule.enabled").
        Saves settings after setting the value.
        """
        keys = key.split('.')
        self._set_nested_value(keys, self._settings, value)
        self.save_settings()

    # Removed redundant methods:
    # get_schedule_settings, update_schedule_settings, get_notification_time,
    # is_schedule_enabled, get_schedule_time, get_schedule_days, validate_schedule,
    # get_theme_colors (moved to ui/themes.py)
