import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.settings import Settings
from utils.logger import Logger
from scheduler import Scheduler
from datetime import datetime
from win10toast import ToastNotifier
import argparse

class AutomaticRepoUpdater:
    def __init__(self):
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--scheduled-run', action='store_true', 
                          help='Run scheduled update')
        self.args = parser.parse_args()

        # Initialize core components
        self.settings = Settings()
        self.logger = Logger(self.settings)
        self.scheduler = Scheduler(self.settings)
        self.toaster = ToastNotifier()

        # Only create GUI if not running scheduled update
        if not self.args.scheduled_run:
            self.app = QApplication(sys.argv)
            self.main_window = MainWindow(self)

            # Schedule updates if enabled in settings
            if self.settings.get("schedule_enabled", False):
                self.scheduler.update_schedule()

    def run(self):
        """Run the application"""
        if self.args.scheduled_run:
            self._run_scheduled_update()
        else:
            self.main_window.show()
            sys.exit(self.app.exec())

    def _run_scheduled_update(self):
        """Execute a scheduled update"""
        try:
            # Show notification before starting
            if self.settings.get("notifications_enabled", True):
                self.toaster.show_toast(
                    "Automatic Repo Updater",
                    "Starting scheduled repository update...",
                    duration=5,
                    threaded=True
                )

            # Get the last directory from settings
            directory = self.settings.get("last_directory")
            if not directory:
                self.logger.error("No directory configured for scheduled update")
                return

            # Initialize git operations
            from AutomaticRepoUpdater.git_operations import GitOperations
            git_ops = GitOperations(self.settings, self.logger)

            # Scan and update repositories
            repos = git_ops.scan_directories(directory)
            update_count = 0
            error_count = 0

            for repo in repos:
                success, message = git_ops.pull_repository(repo)
                if success:
                    update_count += 1
                else:
                    error_count += 1
                    self.logger.error(f"Failed to update {repo}: {message}")

            # Show completion notification
            if self.settings.get("notifications_enabled", True):
                self.toaster.show_toast(
                    "Automatic Repo Updater",
                    f"Update complete: {update_count} successful, {error_count} failed",
                    duration=10,
                    threaded=True
                )

        except Exception as e:
            self.logger.error(f"Scheduled update failed: {str(e)}")
            if self.settings.get("notifications_enabled", True):
                self.toaster.show_toast(
                    "Automatic Repo Updater",
                    f"Update failed: {str(e)}",
                    duration=10,
                    threaded=True
                )

if __name__ == "__main__":
    app = AutomaticRepoUpdater()
    app.run()
