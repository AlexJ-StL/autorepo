import json
from pathlib import Path


class Settings:
    def __init__(self):
        self.settings_file = Path.home() / '.autorepo' / 'settings.json'
        self.default_settings = {
            "theme": "light",
            "last_directory": str(Path.home()),
            "saved_repositories": [],
            "schedule": {
                "enabled": False,
                "time": "09:00",
                "days": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                ]
            },
            "error_handling": {
                "auto_stash": False,
                "skip_dirty_repos": True,
                "show_notifications": True
            },
            "logging": {
                "format": "json",  # or "csv"
                "rolling": True    # False for per-session
            }
        }
        self._settings = self.load_settings()

    def load_settings(self):
        """Load settings from file or create with defaults"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    # Getter/setter properties for common settings
    @property
    def theme(self):
        return self._settings.get("theme", "light")

    @theme.setter
    def theme(self, value):
        self._settings["theme"] = value
        self.save_settings()

    @property
    def last_directory(self):
        return self._settings.get("last_directory", str(Path.home()))

    @last_directory.setter
    def last_directory(self, value):
        self._settings["last_directory"] = str(value)
        self.save_settings()

    def add_saved_repository(self, repo_path):
        """Add a repository to saved list"""
        if repo_path not in self._settings["saved_repositories"]:
            self._settings["saved_repositories"].append(repo_path)
            self.save_settings()

    def remove_saved_repository(self, repo_path):
        """Remove a repository from saved list"""
        if repo_path in self._settings["saved_repositories"]:
            self._settings["saved_repositories"].remove(repo_path)
            self.save_settings()

    def get_schedule_settings(self):
        """Get schedule settings"""
        return self._settings.get(
            "schedule",
            self.default_settings["schedule"]
        )

    def update_schedule_settings(self, enabled, time_str, days):
        """Update schedule settings"""
        self._settings["schedule"] = {
            "enabled": enabled,
            "time": time_str,
            "days": days
        }
        self.save_settings()

    def get_error_handling(self):
        """Get error handling preferences"""
        return self._settings.get(
            "error_handling",
            self.default_settings["error_handling"]
        )

    def update_error_handling(self, **kwargs):
        """Update error handling settings"""
        self._settings["error_handling"].update(kwargs)
        self.save_settings()
