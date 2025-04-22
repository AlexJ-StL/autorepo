import sys
import argparse
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import QApplication
# Removed desktop_notifier import

from ui.main_window import MainWindow
from utils.settings import Settings
import logging
from utils.logger import setup_logging, get_logger
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
        # Logger is now configured using standard logging in utils.logger
        self.logger = get_logger(__name__) # Get a logger instance for this module
        self.scheduler = Scheduler(self.settings)
        # Toaster is replaced by plyer.notification

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
        self.logger.info("GUI Initialized.")

        # Schedule updates if enabled in settings
        # Schedule updates if enabled in settings
        if self.settings.get("schedule.enabled", default=False):
            self.scheduler.update_schedule()

    def run(self) -> None:
        """Run the application based on parsed arguments."""
        if self.args.scheduled_run:
            self.logger.info("Starting scheduled update run.")
            self._run_scheduled_update()
        elif self.app and self.main_window:
            self.logger.info("Starting GUI application.")
            self.main_window.show()
            sys.exit(self.app.exec())
        else:
            # This case should ideally not be reached if GUI init fails
            self.logger.error("Application cannot start: No GUI and not a scheduled run.")
            sys.exit(1)


    def _run_scheduled_update(self) -> None:
        """Execute a scheduled update for repositories in the configured directory."""
        try:
            # Fetch directory from settings
            directory: Optional[str] = self.settings.get("application.last_directory")

            # === VITAL CHECK ===
            # Check if directory is None or empty string
            if not directory:
                self.logger.error("Scheduled update aborted: No directory configured.")
                # (Optional notification code here...)
                if self.main_window:
                    self.main_window.show_notification(
                        "Update Failed", "No directory configured.", level="error"
                    )
                else:
                    # Log that UI isn't available if it's not initialized
                    self.logger.warning("Cannot show notification: MainWindow is not available.")

                # EXIT the function here if the directory is invalid.
                # This tells the type checker that the code below
                # will NOT execute if 'directory' is None or "".
                return
            # ====================

            # If the code reaches this point, 'directory' MUST be a non-empty string.
            # The type checker should now be satisfied.

            self.logger.info(f"Scheduled update started for directory: {directory}")
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification(
                    "Starting Update",
                    "Scheduled repository update is starting...",
                ) # Duration is handled within MainWindow.show_notification

            # Import GitOperations here to keep it scoped to this method
            # Ensure this import path is correct for your project structure
            from AutomaticRepoUpdater.git_operations import GitOperations
            git_ops = GitOperations(self.settings, self.logger)

            # Scan and update repositories
            repos = git_ops.scan_directories(directory) # 'directory' is now known to be 'str'
            self.logger.info(f"Found {len(repos)} repositories to check.")
            update_count = 0
            error_count = 0

            for repo_path in repos:
                self.logger.debug(f"Attempting to update {repo_path}")
                success, message = git_ops.pull_repository(str(repo_path))
                if success:
                    update_count += 1
                    self.logger.info(f"Successfully updated {repo_path}: {message}")
                else:
                    error_count += 1
                    self.logger.error(f"Failed to update {repo_path}: {message}")

            # Show completion notification
            completion_message = f"Update complete: {update_count} successful, {error_count} failed."
            self.logger.info(completion_message)
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification(
                    "Update Complete",
                    completion_message,
                ) # Duration is handled within MainWindow.show_notification

        except ImportError as e:
            self.logger.error(f"Failed to import required module for scheduled update: {e}")
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification("Update Failed", f"Import error: {e}", level="error")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during scheduled update: {e}", exc_info=True)
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification("Update Failed", f"Error: {e}", level="error")
        try:
            directory: Optional[str] = self.settings.get("application.last_directory")
            notifications_enabled: bool = bool(
                self.settings.get("notifications.enabled", default=True)
            )

            directory = self.settings.get("repository_directory")
            if directory is None or directory == "":
                self.logger.error(
                    "Scheduled update aborted: No directory configured."
                )
                if self.main_window:
                    self.main_window.show_notification(
                        "Update Failed",
                        "No directory configured.",
                        level="error"
                    )
                return # Exit the function if directory is not configured

            self.logger.info(f"Scheduled update started for directory: {directory}")
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification(
                    "Starting Update",
                    "Scheduled repository update is starting...",
                ) # Duration is handled within MainWindow.show_notification
            else: # Add else for the UI check to log warning if UI is not available
                self.logger.warning("Cannot show notification: MainWindow is not available.")

            # Import GitOperations here to keep it scoped to this method
            from AutomaticRepoUpdater.git_operations import GitOperations
            git_ops = GitOperations(self.settings, self.logger)

            # Scan and update repositories
            repos = git_ops.scan_directories(directory)
            self.logger.info(f"Found {len(repos)} repositories to check.")
            update_count = 0
            error_count = 0

            for repo_path in repos:
                self.logger.debug(f"Attempting to update {repo_path}")
                success, message = git_ops.pull_repository(str(repo_path))
                if success:
                    update_count += 1
                    self.logger.info(f"Successfully updated {repo_path}: {message}")
                else:
                    error_count += 1
                    self.logger.error(f"Failed to update {repo_path}: {message}")

            # Show completion notification
            completion_message = f"Update complete: {update_count} successful, {error_count} failed."
            self.logger.info(completion_message)
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification(
                    "Update Complete",
                    completion_message,
                ) # Duration is handled within MainWindow.show_notification

        except ImportError as e:
            self.logger.error(f"Failed to import required module for scheduled update: {e}")
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification("Update Failed", f"Import error: {e}", level="error")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during scheduled update: {e}", exc_info=True)
            if self.main_window: # Only show GUI notifications if GUI is initialized
                self.main_window.show_notification("Update Failed", f"Error: {e}", level="error")

if __name__ == "__main__":
    updater = AutomaticRepoUpdater()
    updater.run()
