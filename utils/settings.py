import json
import os

class Settings:
    def __init__(self):
        self.settings = {
            # Default schedule settings
            "schedule_enabled": False,
            "schedule_days": ["Mon", "Wed", "Fri"],
            "schedule_hour": 9,
            "schedule_minute": 0,
            "schedule_notification": "5 minutes",
            "notifications_enabled": True,
            "notification_sound": True,
            
            # Default application settings
            "theme": "light",
            "max_depth": 2,
            "auto_save": True,
            "last_directory": "",
            "log_format": "JSON",
            "log_retention": 30
        }
        self.load_settings()

    def get_schedule_settings(self):
        """Return all schedule-related settings as a dict"""
        return {
            "enabled": self.settings.get("schedule_enabled", False),
            "days": self.settings.get("schedule_days", ["Mon", "Wed", "Fri"]),
            "hour": self.settings.get("schedule_hour", 9),
            "minute": self.settings.get("schedule_minute", 0),
            "notification": self.settings.get("schedule_notification", "5 minutes"),
            "notifications_enabled": self.settings.get("notifications_enabled", True),
            "notification_sound": self.settings.get("notification_sound", True)
        }

    def update_schedule_settings(self, schedule_settings: dict):
        """Update schedule settings with validation"""
        # Validate days
        valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        days = schedule_settings.get("days", [])
        self.settings["schedule_days"] = [day for day in days if day in valid_days]

        # Validate hour (0-23)
        hour = schedule_settings.get("hour", 9)
        self.settings["schedule_hour"] = max(0, min(23, int(hour)))

        # Validate minute (0-59)
        minute = schedule_settings.get("minute", 0)
        self.settings["schedule_minute"] = max(0, min(59, int(minute)))

        # Update other schedule settings
        self.settings["schedule_enabled"] = bool(schedule_settings.get("enabled", False))
        self.settings["schedule_notification"] = schedule_settings.get("notification", "5 minutes")
        self.settings["notifications_enabled"] = bool(schedule_settings.get("notifications_enabled", True))
        self.settings["notification_sound"] = bool(schedule_settings.get("notification_sound", True))

        self.save_settings()

    def get_notification_time(self) -> int:
        """Convert notification time setting to minutes, handling custom input"""
        notification_setting = self.settings.get("schedule_notification", "5 minutes")
        try:
            if notification_setting.endswith("minutes"):
                return int(notification_setting.split()[0])
            elif notification_setting.endswith("hours"):
                return int(notification_setting.split()[0]) * 60
            elif notification_setting.isdigit():
                return int(notification_setting)
            else:
                return 5
        except ValueError:
            return 5

    def is_schedule_enabled(self) -> bool:
        """Check if scheduling is enabled"""
        return self.settings.get("schedule_enabled", False)

    def get_schedule_time(self) -> tuple:
        """Return schedule time as (hour, minute)"""
        return (
            self.settings.get("schedule_hour", 9),
            self.settings.get("schedule_minute", 0)
        )

    def get_schedule_days(self) -> list:
        """Return list of scheduled days"""
        return self.settings.get("schedule_days", ["Mon", "Wed", "Fri"])

    def validate_schedule(self) -> tuple[bool, str]:
        """Validate schedule settings"""
        if not self.settings.get("last_directory"):
            return False, "No directory configured for scheduled updates"
        
        if not self.settings.get("schedule_days"):
            return False, "No days selected for scheduled updates"
        
        return True, "Schedule settings are valid"

    def load_settings(self):
        """Load settings from JSON file"""
        settings_path = "settings.json"
        if os.path.exists(settings_path):
            with open(settings_path, "r") as file:
                self.settings.update(json.load(file))

    def save_settings(self):
        """Save settings to JSON file"""
        settings_path = "settings.json"
        with open(settings_path, "w") as file:
            json.dump(self.settings, file, indent=4)

    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()

    def get_theme_colors(self):
        """Return theme colors"""
        if self.settings.get("theme") == "dark":
            return {
                "window": "#1A202C",
                "text": "#F7FAFC",
                "primary": "#4299E1",
                "secondary": "#2D3748",
                "accent": "#48BB78",
                "error": "#F56565",
                "card_bg": "#2D3748",
                "border": "#4A5568",
                "hover": "#2B6CB0",
                "disabled": "#718096",
                "success": "#38A169",
                "warning": "#D69E2E"
            }
        else:
            return {
                "window": "#F5F7FA",
                "text": "#2C3E50",
                "primary": "#3498DB",
                "secondary": "#E8EEF2",
                "accent": "#2ECC71",
                "error": "#E74C3C",
                "card_bg": "#FFFFFF",
                "border": "#CBD5E0",
                "hover": "#2980B9",
                "disabled": "#BDC3C7",
                "success": "#27AE60",
                "warning": "#F39C12"
            }
