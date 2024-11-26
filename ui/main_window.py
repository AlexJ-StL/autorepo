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

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Create header with app title and theme toggle
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title_label = QLabel("Automatic Repo Updater")
        title_label.setObjectName("app-title")
        header_layout.addWidget(title_label)

        theme_switch = QPushButton()
        theme_switch.setObjectName("theme-switch")
        theme_switch.clicked.connect(self._toggle_theme)
        header_layout.addWidget(
            theme_switch,
            alignment=Qt.AlignmentFlag.AlignRight
        )
        main_layout.addWidget(header)

        # Action buttons in a card-like container
        action_card = QFrame()
        action_card.setObjectName("action-card")
        action_layout = QHBoxLayout(action_card)

        self.select_dir_button = QPushButton("Select Directory")
        self.select_dir_button.setObjectName("primary-button")
        self.select_dir_button.clicked.connect(self.select_directory)

        self.update_button = QPushButton("Update Repositories")
        self.update_button.setObjectName("primary-button")
        self.update_button.clicked.connect(self.update_repositories)

        action_layout.addWidget(self.select_dir_button)
        action_layout.addWidget(self.update_button)
        main_layout.addWidget(action_card)

        # Tab widget with modern styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("main-tabs")

        # Add tabs
        self.tab_widget.addTab(self._create_status_tab(), "Status")
        self.tab_widget.addTab(self._create_settings_tab(), "Settings")
        self.tab_widget.addTab(self._create_logs_tab(), "Logs")

        main_layout.addWidget(self.tab_widget)

        # Status bar with modern styling
        status_bar = QFrame()
        status_bar.setObjectName("status-bar")
        status_layout = QHBoxLayout(status_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-text")
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_bar)

        # Apply initial theme
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

    def _create_status_tab(self):
        """Create and return the status tab widget"""
        status_widget = QWidget()
        layout = QVBoxLayout(status_widget)
        layout.setSpacing(15)

        status_label = QLabel("Status:")
        layout.addWidget(status_label)

        status_text = QTextEdit()
        status_text.setReadOnly(True)
        layout.addWidget(status_text)

        return status_widget

    def _create_settings_tab(self):
        """Create and return the settings tab widget"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setSpacing(15)

        # Repository Settings Group
        repo_group = QGroupBox("Repository Settings")
        repo_layout = QVBoxLayout(repo_group)
        
        # Max depth setting
        depth_layout = QHBoxLayout()
        depth_label = QLabel("Maximum Repository Depth:")
        depth_combo = QComboBox()
        depth_combo.addItems(["1", "2", "3", "4", "5"])
        depth_combo.setCurrentText(str(self.app.settings.get("max_depth", "2")))
        depth_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set("max_depth", int(x))
        )
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(depth_combo)
        depth_layout.addStretch()
        repo_layout.addLayout(depth_layout)

        # Auto-save setting
        autosave = QCheckBox("Auto-save repository list")
        autosave.setChecked(self.app.settings.get("auto_save", True))
        autosave.toggled.connect(
            lambda x: self.app.settings.set("auto_save", x)
        )
        repo_layout.addWidget(autosave)

        layout.addWidget(repo_group)

        # Notification Settings Group
        notif_group = QGroupBox("Notification Settings")
        notif_layout = QVBoxLayout(notif_group)
        
        # Enable notifications
        enable_notif = QCheckBox("Enable Notifications")
        enable_notif.setChecked(self.app.settings.get("notifications_enabled", True))
        enable_notif.toggled.connect(
            lambda x: self.app.settings.set("notifications_enabled", x)
        )
        notif_layout.addWidget(enable_notif)

        # Notification sound
        sound_check = QCheckBox("Play notification sound")
        sound_check.setChecked(self.app.settings.get("notification_sound", True))
        sound_check.toggled.connect(
            lambda x: self.app.settings.set("notification_sound", x)
        )
        notif_layout.addWidget(sound_check)

        layout.addWidget(notif_group)

        # Logging Settings Group
        log_group = QGroupBox("Logging Settings")
        log_layout = QVBoxLayout(log_group)
        
        # Log format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Log Format:")
        format_combo = QComboBox()
        format_combo.addItems(["JSON", "CSV"])
        format_combo.setCurrentText(self.app.settings.get("log_format", "JSON"))
        format_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set("log_format", x)
        )
        format_layout.addWidget(format_label)
        format_layout.addWidget(format_combo)
        format_layout.addStretch()
        log_layout.addLayout(format_layout)

        # Log retention
        retention_layout = QHBoxLayout()
        retention_label = QLabel("Log Retention (days):")
        retention_combo = QComboBox()
        retention_combo.addItems(["7", "14", "30", "90"])
        retention_combo.setCurrentText(str(self.app.settings.get("log_retention", "30")))
        retention_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set("log_retention", int(x))
        )
        retention_layout.addWidget(retention_label)
        retention_layout.addWidget(retention_combo)
        retention_layout.addStretch()
        log_layout.addLayout(retention_layout)

        layout.addWidget(log_group)

        # Add stretch to push everything to the top
        layout.addStretch()

        return settings_widget

    def _create_logs_tab(self):
        """Create and return the logs tab widget"""
        logs_widget = QWidget()
        layout = QVBoxLayout(logs_widget)
        layout.setSpacing(15)

        logs_label = QLabel("Logs:")
        layout.addWidget(logs_label)

        logs_text = QTextEdit()
        logs_text.setReadOnly(True)
        layout.addWidget(logs_text)

        return logs_widget


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
