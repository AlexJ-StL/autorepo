"""
Main window module for the Git automation application.
Handles the primary user interface components
and window management using PyQt6.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QTabWidget,
    QFrame,
    QGroupBox, QComboBox, QCheckBox, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal
from AutomaticRepoUpdater.git_operations import GitOperations
import json
from .themes import Themes


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.git_operations = GitOperations(self.app.settings,
                                            self.app.logger)
        self.init_ui()

    def init_ui(self):
        self.showMaximized()
        self.setWindowTitle("Automatic Repo Updater")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
    
        main_layout = QVBoxLayout(self.central_widget)
    
        toolbar_layout = QHBoxLayout()
    
        left_buttons = QFrame()
        left_layout = QHBoxLayout(left_buttons)
    
        self.select_dir_button = QPushButton("Select Directory")
        self.select_dir_button.clicked.connect(self.select_directory)
        self.update_button = QPushButton("Update Repositories")
        self.update_button.clicked.connect(self.update_repositories)
    
        left_layout.addWidget(self.select_dir_button)
        left_layout.addWidget(self.update_button)
    
        toolbar_layout.addWidget(left_buttons)
        toolbar_layout.addStretch()  
    
        main_layout.addLayout(toolbar_layout)
    
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
    
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        settings_widget = self._create_settings_tab()
        self.tab_widget.addTab(settings_widget, "Settings")
        
        logs_widget = self._create_logs_tab()
        self.tab_widget.addTab(logs_widget, "Logs")
        
        self._apply_theme()

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

        self.status_label.setText(f"Logs saved to {self.app.logger.log_dir}")

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
