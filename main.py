import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.settings import Settings
from utils.logger import Logger
from scheduler import Scheduler
from datetime import datetime


class AutomaticRepoUpdater:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.settings = Settings()
        self.logger = Logger(self.settings)
        self.scheduler = Scheduler(self.settings)
        self.main_window = MainWindow(self)

        # Schedule updates if enabled in settings
        if self.settings.get_schedule_settings()['enabled']:
            self.schedule_updates()

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())

    def schedule_updates(self):
        """Schedule repository updates using the scheduler"""
        schedule_settings = self.settings.get_schedule_settings()
        trigger_time = datetime.strptime(
            schedule_settings['time'], '%H:%M'
        ).time()
        trigger_days = [
            self.get_day_index(day) for day in schedule_settings['days']
        ]
        self.scheduler.create_task(
            'Automatic Repo Updater',
            sys.argv[0],  # Path to the main script
            trigger_time,
            trigger_days
        )

    def get_day_index(self, day_name):
        """Get the index of the day in the week (0 for Monday, 6 for Sunday)"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday", "Sunday"]
        return days.index(day_name)


if __name__ == "__main__":
    app = AutomaticRepoUpdater()
    app.run()
