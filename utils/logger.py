import json
import csv
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, settings):
        self.settings = settings
        self.log_dir = Path.home() / '.autorepo' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.events = []

    def _get_log_file(self):
        """Get appropriate log file path based on settings"""
        format = self.settings._settings["logging"]["format"]
        if self.settings._settings["logging"]["rolling"]:
            return self.log_dir / f"autorepo_rolling.{format}"
        return (self.log_dir /
                f"autorepo_session_{self.current_session}.{format}")

    def log_event(self, message, event_type="INFO", repo_path=None):
        """Log an event with timestamp and details"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "repository": str(repo_path) if repo_path else None,
            "session": self.current_session
        }
        self.events.append(event)
        self._write_log(event)

    def log_error(self, message, repo_path=None):
        """Convenience method for logging errors"""
        self.log_event(message, "ERROR", repo_path)

    def log_success(self, message, repo_path=None):
        """Convenience method for logging successful operations"""
        self.log_event(message, "SUCCESS", repo_path)

    def _write_log(self, event):
        """Write event to log file in appropriate format"""
        log_file = self._get_log_file()

        if self.settings._settings["logging"]["format"] == "json":
            self._write_json_log(event, log_file)
        else:
            self._write_csv_log(event, log_file)

    def _write_json_log(self, event, log_file):
        """Write log in JSON format"""
        existing_logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    existing_logs = json.load(f)
            except json.JSONDecodeError:
                existing_logs = []

        if not isinstance(existing_logs, list):
            existing_logs = []

        existing_logs.append(event)

        with open(log_file, 'w') as f:
            json.dump(existing_logs, f, indent=2)

    def _write_csv_log(self, event, log_file):
        """Write log in CSV format"""
        fieldnames = ["timestamp", "type", "message", "repository", "session"]

        file_exists = log_file.exists()
        mode = 'a' if file_exists else 'w'

        with open(log_file, mode, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(event)

    def get_session_logs(self):
        """Get all logs for current session"""
        return [event for event in self.events]

    def get_statistics(self):
        """Get statistics for current session"""
        stats = {
            "total_operations": len(self.events),
            "errors": len([e for e in self.events if e["type"] == "ERROR"]),
            "successes": len(
                [e for e in self.events if e["type"] == "SUCCESS"]),
            "start_time": self.events[0]["timestamp"] if self.events else None,
            "end_time": self.events[-1]["timestamp"] if self.events else None
        }
        return stats
