import sys
import argparse
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import QApplication
from win10toast import ToastNotifier

from ui.main_window import MainWindow
from utils.settings import Settings
from utils.logger import Logger
from scheduler import Scheduler
# Delay import of GitOperations to avoid circular dependencies or heavy import
# from AutomaticRepoUpdater.git_operations import GitOperations


class AutomaticRepoUpdater:
    """
    Main application class for the Automatic Repository Updater.

    Handles both GUI mode and scheduled background updates.
    """
    def __init__(self) -> None:
        """Initialize the application components and parse arguments."""
        # Parse command line arguments
        self.args = self._parse_arguments()

        # Initialize core components
        self.settings = Settings()
        self.logger = Logger(self.settings)
        self.scheduler = Scheduler(self.settings)
        self.toaster = ToastNotifier()

        # GUI components (only initialized if not a scheduled run)
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None

        if not self.args.scheduled_run:
            self._init_gui()

    def _parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="Automatic Repository Updater Application."
        )
        parser.add_argument(
            '--scheduled-run',
            action='store_true',
            help='Run the scheduled update process without GUI.'
        )
        return parser.parse_args()

    def _init_gui(self) -> None:
        """Initialize the GUI components."""
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self)
        self.logger.log_event("GUI Initialized.", event_type="INFO")

        # Schedule updates if enabled in settings
        if self.settings.get("schedule_enabled", default=False):
            self.scheduler.update_schedule()

    def run(self) -> None:
        """Run the application based on parsed arguments."""
        if self.args.scheduled_run:
            self.logger.log_event("Starting scheduled update run.", event_type="INFO")
            self._run_scheduled_update()
        elif self.app and self.main_window:
            self.logger.log_event("Starting GUI application.", event_type="INFO")
            self.main_window.show()
            sys.exit(self.app.exec())
        else:
            # This case should ideally not be reached if GUI init fails
            self.logger.log_event("Application cannot start: No GUI and not a scheduled run.", event_type="ERROR")
            sys.exit(1)

    def _run_scheduled_update(self) -> None:
        """Execute a scheduled update for repositories in the configured directory."""
        try:
            directory: Optional[str] = self.settings.get("last_directory")
            notifications_enabled: bool = bool(self.settings.get("notifications_enabled", default=True))

            if not directory:
                self.logger.log_event("Scheduled update aborted: No directory configured.", event_type="ERROR")
                self._show_notification("Update Failed", "No directory configured.", level="error")
                return

            self.logger.log_event(f"Scheduled update started for directory: {directory}", event_type="INFO")
            self._show_notification(
                "Starting Update",
                "Scheduled repository update is starting...",
                duration=5
            )

            # Import GitOperations here to keep it scoped to this method
            from AutomaticRepoUpdater.git_operations import GitOperations
            git_ops = GitOperations(self.settings, self.logger)

            # Scan and update repositories
            repos = git_ops.scan_directories(directory)
            self.logger.log_event(f"Found {len(repos)} repositories to check.", event_type="INFO")
            update_count = 0
            error_count = 0

            for repo_path in repos:
                self.logger.log_event(f"Attempting to update {repo_path}", event_type="DEBUG")
                success, message = git_ops.pull_repository(str(repo_path))
                if success:
                    update_count += 1
                    self.logger.log_event(f"Successfully updated {repo_path}: {message}", event_type="INFO")
                else:
                    error_count += 1
                    self.logger.log_event(f"Failed to update {repo_path}: {message}", event_type="ERROR")

            # Show completion notification
            completion_message = f"Update complete: {update_count} successful, {error_count} failed."
            self.logger.log_event(completion_message, event_type="INFO")
            self._show_notification(
                "Update Complete",
                completion_message,
                duration=10
            )

        except ImportError as e:
            self.logger.log_event(f"Failed to import required module for scheduled update: {e}", event_type="ERROR")
            self._show_notification("Update Failed", f"Import error: {e}", level="error")
        except Exception as e:
            self.logger.log_event(f"An unexpected error occurred during scheduled update: {e}", event_type="ERROR")
            self._show_notification("Update Failed", f"Error: {e}", level="error")

    def _show_notification(self, title: str, message: str, duration: int = 10, level: str = "info") -> None:
        """Utility to show toast notifications if enabled."""
        if self.settings.get("notifications_enabled", default=True):
            full_title = f"Automatic Repo Updater - {title}"
            try:
                # Note: win10toast might have issues if run from certain environments
                # Consider adding more robust error handling or alternatives if needed
                self.toaster.show_toast(
                    full_title,
                    msg=message,
                    duration=duration,
                    threaded=True  # Run in a separate thread to not block execution
                )
            except Exception as e:
                self.logger.log_event(f"Failed to show notification: {e}", event_type="WARNING")


if __name__ == "__main__":
    updater = AutomaticRepoUpdater()
    updater.run()