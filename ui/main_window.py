"""
Main window module for the Git automation application.
Handles the primary user interface components
and window management using PyQt6.
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from utils.git_operations import GitOperations


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.git_operations = GitOperations(self.app.settings,
                                            self.app.logger)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Automatic Repo Updater")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.select_dir_button = QPushButton("Select Directory")
        self.select_dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_button)

        self.update_button = QPushButton("Update Repositories")
        self.update_button.clicked.connect(self.update_repositories)
        layout.addWidget(self.update_button)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.app.settings.last_directory
        )
        if directory:
            self.app.settings.last_directory = directory

    def update_repositories(self):
        directory = self.app.settings.last_directory
        if not directory:
            QMessageBox.warning(self, "Warning", "Please select a directory.")
            return

        self.status_label.setText("Updating...")
        self.update_thread = UpdateThread(directory, self.git_operations)
        self.update_thread.finished.connect(self.update_finished)
        self.update_thread.update_signal.connect(self.update_status)
        self.update_thread.start()

    def update_finished(self):
        self.status_label.setText("Update complete")

    def update_status(self, message):
        self.status_label.setText(message)


class UpdateThread(QThread):
    finished = pyqtSignal()
    update_signal = pyqtSignal(str)

    def __init__(self, directory, git_operations):
        super().__init__()
        self.directory = directory
        self.git_operations = git_operations

    def run(self):
        repos = self.git_operations.scan_directories(self.directory)
        for repo in repos:
            self.update_signal.emit(f"Updating {repo}...")
            self.git_operations.pull_repository(repo)
        self.finished.emit()
