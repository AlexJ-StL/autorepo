import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.settings import Settings
from utils.logger import Logger

class AutomaticRepoUpdater:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.settings = Settings()
        self.logger = Logger()
        self.main_window = MainWindow(self)

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = AutomaticRepoUpdater()
    app.run()
