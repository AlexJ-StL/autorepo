"""
Main window module for the Git automation application.
Handles the primary user interface components
and window management using PyQt6.
"""

import sys # Keep sys import for QApplication
import logging # Import logging for use in MainWindow

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QTabWidget,
    QFrame,
    QGroupBox, QComboBox, QCheckBox, QTextEdit,
    QSystemTrayIcon # Import QSystemTrayIcon
)
from PyQt6.QtGui import QIcon # Import QIcon
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from AutomaticRepoUpdater.git_operations import GitOperations
from ui.themes import get_theme_colors # Import get_theme_colors

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        # Use the logger instance from the app
        self.logger = logging.getLogger(__name__)
        self.git_operations = GitOperations(
            self.app.settings,
            self.logger # Pass the standard logger
        )
        self.init_ui()
        self._init_tray_icon() # Initialize system tray icon

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
        self.tab_widget.addTab(
            self._create_status_tab(),
            "Status"
        )
        self.tab_widget.addTab(
            self._create_settings_tab(),
            "Settings"
        )
        self.tab_widget.addTab(
            self._create_logs_tab(),
            "Logs"
        )
        self.tab_widget.addTab(
            self._create_scheduler_tab(),
            "Schedule"
        )

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

    def _init_tray_icon(self):
        """Initializes the system tray icon for notifications."""
        # You might need an application icon file (e.g., .ico, .png)
        # For now, using a generic icon or handling potential errors
        try:
            # Replace 'app_icon.png' with the actual path to your application icon
            icon_path = "app_icon.png" # Placeholder
            if not Path(icon_path).exists():
                # Fallback or handle missing icon
                self.logger.warning(f"Application icon not found at {icon_path}. Tray icon may not display correctly.")
                # Use a standard icon or None
                self.tray_icon = QSystemTrayIcon(self) # No icon provided
            else:
                self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)

            self.tray_icon.setToolTip("Automatic Repo Updater")
            self.tray_icon.show()
        except Exception as e:
            self.logger.error(f"Failed to initialize system tray icon: {e}")
            self.tray_icon = None # Ensure tray_icon is None if initialization fails


    def show_notification(self, title: str, message: str, level: str = "info") -> None:
        """
        Shows a desktop notification using QSystemTrayIcon.
        Level parameter is for logging purposes, QSystemTrayIcon.showMessage doesn't use it directly.
        """
        if self.app.settings.get("notifications.enabled", default=True) and self.tray_icon:
            try:
                # QSystemTrayIcon.showMessage(title, message, icon=NoIcon, msecs=10000)
                # icon can be QSystemTrayIcon.Information, Warning, Critical, NoIcon
                # Mapping level to QSystemTrayIcon icon type (basic mapping)
                icon_type = QSystemTrayIcon.Information
                if level == "warning":
                    icon_type = QSystemTrayIcon.Warning
                elif level == "error":
                    icon_type = QSystemTrayIcon.Critical

                self.tray_icon.showMessage(
                    f"Automatic Repo Updater - {title}",
                    message,
                    icon=icon_type,
                    msecs=10000 # Duration in milliseconds (10 seconds)
                )
                self.logger.info(f"Notification shown: {title} - {message}")
            except Exception as e:
                self.logger.error(f"Failed to show notification via QSystemTrayIcon: {e}")
        elif not self.app.settings.get("notifications.enabled", default=True):
            self.logger.info("Notification not shown: Notifications are disabled in settings.")
        else:
            self.logger.warning("Notification not shown: System tray icon is not available.")


    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.app.settings.get("application.last_directory", "") # Use nested key
        )
        if directory:
            self.app.settings.set("application.last_directory", directory) # Use nested key

    def update_repositories(self):
        directory = self.app.settings.get("application.last_directory", "") # Use nested key
        if not directory:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a directory."
            )
            return

        self.status_label.setText("Updating...")
        self.update_thread = UpdateThread(
            directory, self.git_operations
        )
        self.update_thread.finished.connect(self.update_finished)
        self.update_thread.update_signal.connect(self.update_status)
        self.update_thread.start()

        # Assuming logger has a way to get log file path, update this line
        # self.status_label.setText(
        #     f"Logs saved to {self.app.logger.log_dir}"
        # )
        self.status_label.setText("Update started. Check logs tab for details.")


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
        depth_label = QLabel(
            "Maximum Repository Depth:"
        )
        depth_combo = QComboBox()
        depth_combo.addItems(
            ["1", "2", "3", "4", "5"]
        )
        depth_combo.setCurrentText(
            str(self.app.settings.get(
                "application.max_depth", # Use nested key
                "2"
            ))
        )
        depth_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "application.max_depth", int(x) # Use nested key
            )
        )
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(depth_combo)
        depth_layout.addStretch()
        repo_layout.addLayout(depth_layout)

        # Auto-save setting
        autosave = QCheckBox("Auto-save repository list")
        autosave.setChecked(
            self.app.settings.get(
                "application.auto_save", # Use nested key
                True
            )
        )
        autosave.toggled.connect(
            lambda x: self.app.settings.set("application.auto_save", x) # Use nested key
        )
        repo_layout.addWidget(autosave)

        layout.addWidget(repo_group)

        # Notification Settings Group
        notif_group = QGroupBox("Notification Settings")
        notif_layout = QVBoxLayout(notif_group)

        # Enable notifications
        enable_notif = QCheckBox("Enable Notifications")
        enable_notif.setChecked(
            self.app.settings.get(
                "notifications.enabled", # Use nested key
                True
            )
        )
        enable_notif.toggled.connect(
            lambda x: self.app.settings.set(
                "notifications.enabled", x # Use nested key
            )
        )
        notif_layout.addWidget(enable_notif)

        # Notification sound
        sound_check = QCheckBox("Play notification sound")
        sound_check.setChecked(
            self.app.settings.get(
                "notifications.sound", # Use nested key
                True
            )
        )
        sound_check.toggled.connect(
            lambda x: self.app.settings.set(
                "notifications.sound", x # Use nested key
            )
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
        format_combo.setCurrentText(
            self.app.settings.get("application.log_format", "JSON") # Use nested key
        )
        format_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "application.log_format", x # Use nested key
            )
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
        retention_combo.setCurrentText(
            str(self.app.settings.get(
                "application.log_retention", "30" # Use nested key
            ))
        )
        retention_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "application.log_retention", int(x) # Use nested key
            )
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

        # Controls section
        controls_group = QGroupBox("Log Controls")
        controls_layout = QHBoxLayout(controls_group)

        # Refresh button
        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.setObjectName("primary-button")
        refresh_btn.clicked.connect(self._refresh_logs)

        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.setObjectName("primary-button")
        clear_btn.clicked.connect(self._clear_logs)

        # Filter dropdown
        filter_combo = QComboBox()
        filter_combo.addItems([
            "All",
            "Info",
            "Warning",
            "Error",
            "Success"
        ])
        filter_combo.currentTextChanged.connect(
            self._filter_logs
        )

        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(filter_combo)
        controls_layout.addStretch()

        layout.addWidget(controls_group)

        # Log display
        log_display_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_display_group)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setObjectName("log-display")
        log_layout.addWidget(self.logs_text)

        # Statistics section
        stats_layout = QHBoxLayout()
        self.total_logs_label = QLabel("Total Logs: 0")
        self.error_count_label = QLabel("Errors: 0")
        self.warning_count_label = QLabel("Warnings: 0")
        stats_layout.addWidget(self.total_logs_label)
        stats_layout.addWidget(self.error_count_label)
        stats_layout.addWidget(self.warning_count_label)
        stats_layout.addStretch()
        log_layout.addLayout(stats_layout)

        layout.addWidget(log_display_group)

        # Add the helper methods
        self._refresh_logs()

        return logs_widget

    def _create_scheduler_tab(self):
        """Create and return the scheduler tab widget"""
        scheduler_widget = QWidget()
        layout = QVBoxLayout(scheduler_widget)
        layout.setSpacing(15)

        # Enable Scheduling Group
        schedule_group = QGroupBox("Schedule Settings")
        schedule_layout = QVBoxLayout(schedule_group)

        # Enable scheduling checkbox
        enable_schedule = QCheckBox("Enable Scheduled Updates")
        enable_schedule.setChecked(
            self.app.settings.get("schedule.enabled", False) # Use nested key
        )
        enable_schedule.toggled.connect(
            lambda x: self.app.settings.set(
                "schedule.enabled", x # Use nested key
            )
        )
        schedule_layout.addWidget(enable_schedule)

        # Time selection
        time_layout = QHBoxLayout()
        time_label = QLabel("Update Time:")
        hour_combo = QComboBox()
        hour_combo.addItems([f"{i:02d}" for i in range(24)])
        hour_combo.setCurrentText(
            str(self.app.settings.get(
                "schedule.hour", "09" # Use nested key
            )).zfill(2)
        )

        minute_combo = QComboBox()
        minute_combo.addItems(
            [f"{i:02d}" for i in range(0, 60, 15)]
        )
        minute_combo.setCurrentText(
            str(self.app.settings.get(
                "schedule.minute", "00" # Use nested key
            )).zfill(2)
        )

        time_layout.addWidget(time_label)
        time_layout.addWidget(hour_combo)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(minute_combo)
        time_layout.addStretch()
        schedule_layout.addLayout(time_layout)

        # Days selection
        days_layout = QHBoxLayout()
        days_label = QLabel("Run on days:")
        days_layout.addWidget(days_label)

        days = [
            'Mon',
            'Tue',
            'Wed',
            'Thu',
            'Fri',
            'Sat',
            'Sun'
        ]
        self.day_checkboxes = {}
        saved_days = self.app.settings.get(
            "schedule.days", # Use nested key
            ["Mon", "Wed", "Fri"]
        )

        for day in days:
            checkbox = QCheckBox(day)
            checkbox.setChecked(day in saved_days)
            checkbox.toggled.connect(
                lambda x,
                d=day: self._update_schedule_days(d, x)
            )
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)

        schedule_layout.addLayout(days_layout)

        # Notification preferences
        notif_layout = QHBoxLayout()
        notif_label = QLabel("Notification before update:")
        notif_combo = QComboBox()
        notif_combo.setEditable(True)
        notif_combo.addItems([
            "1 minute",
            "5 minutes",
            "15 minutes",
            "30 minutes",
            "1 hour",
            "2 hours"
        ])
        notif_combo.setCurrentText(
            self.app.settings.get(
                "schedule.notification_time", # Use nested key (renamed)
                "5 minutes"
            )
        )
        notif_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "schedule.notification_time", x # Use nested key (renamed)
            )
        )
        notif_layout.addWidget(notif_label)
        notif_layout.addWidget(notif_combo)
        notif_layout.addStretch()
        schedule_layout.addLayout(notif_layout)

        # Add the schedule group to main layout
        layout.addWidget(schedule_group)

        # Current Schedule Status Group
        status_group = QGroupBox("Schedule Status")
        status_layout = QVBoxLayout(status_group)

        self.next_run_label = QLabel(
            "Next scheduled run: Not scheduled"
        )
        self.next_run_label.setObjectName(
            "schedule-status-label"
        )
        status_layout.addWidget(
            self.next_run_label
        )

        self.last_run_label = QLabel(
            "Last run: Never"
        )
        self.last_run_label.setObjectName(
            "schedule-status-label"
        )
        status_layout.addWidget(
            self.last_run_label
        )

        # Add the status group to main layout
        layout.addWidget(status_group)

        # Add stretch to push everything to the top
        layout.addStretch()

        return scheduler_widget

    def _update_schedule_days(self, day, checked):
        """Update the list of scheduled days in settings."""
        current_days = self.app.settings.get("schedule.days", []) # Use nested key
        if checked and day not in current_days:
            current_days.append(day)
        elif not checked and day in current_days:
            current_days.remove(day)
        self.app.settings.set("schedule.days", current_days) # Use nested key

    def _update_schedule_time(self, hour, minute):
        """Update the scheduled hour and minute in settings."""
        self.app.settings.set("schedule.hour", int(hour)) # Use nested key
        self.app.settings.set("schedule.minute", int(minute)) # Use nested key

    def _update_schedule(self):
        """Update the scheduler based on current settings."""
        # This method would likely call a method on the scheduler instance
        # to reconfigure the scheduled task based on the updated settings.
        # Example: self.app.scheduler.configure_task()
        self.logger.info("Schedule settings updated. Scheduler needs to be reconfigured.")
        # Placeholder: In a real app, you'd call a method on self.app.scheduler
        # self.app.scheduler.update_schedule_from_settings() # Assuming such a method exists

    def _refresh_logs(self):
        """Refresh the logs displayed in the logs tab."""
        # This method needs to read the log file and display its content.
        # Since we switched to standard logging, we need to read the log file directly.
        log_file_path = Path.home() / '.autorepo' / 'logs' / 'autorepo.log'
        log_content = ""
        if log_file_path.exists():
            try:
                with open(log_file_path, 'r') as f:
                    log_content = f.read()
            except Exception as e:
                self.logger.error(f"Failed to read log file: {e}")
                log_content = f"Error reading log file: {e}"

        self.logs_text.setText(log_content)
        # Update statistics - this would require parsing the log file content
        # For now, just clear them or show placeholders
        self.total_logs_label.setText("Total Logs: N/A")
        self.error_count_label.setText("Errors: N/A")
        self.warning_count_label.setText("Warnings: N/A")


    def _clear_logs(self):
        """Clear the log file and the displayed logs."""
        log_file_path = Path.home() / '.autorepo' / 'logs' / 'autorepo.log'
        if log_file_path.exists():
            try:
                with open(log_file_path, 'w') as f:
                    f.write("") # Clear the file
                self.logger.info("Log file cleared.")
            except Exception as e:
                self.logger.error(f"Failed to clear log file: {e}")

        self.logs_text.clear()
        self.total_logs_label.setText("Total Logs: 0")
        self.error_count_label.setText("Errors: 0")
        self.warning_count_label.setText("Warnings: 0")


    def _filter_logs(self, filter_level):
        """Filter the displayed logs by level."""
        # This method would require reading the log file and filtering its content
        # based on the selected level before displaying it.
        # Since the current log format is simple text, this would involve
        # parsing each line.
        self.logger.info(f"Log filter set to: {filter_level}. Filtering not fully implemented for current log format.")
        # Re-implement filtering logic here based on the text in self.logs_text
        # or by re-reading and parsing the log file.


    def _apply_theme(self):
        """Apply the selected theme to the application."""
        theme_name = self.app.settings.get("application.theme", "light") # Use nested key
        colors = get_theme_colors(theme_name)
        # Apply stylesheet based on colors
        stylesheet = f"""
            QMainWindow {{
                background-color: {colors['window']};
                color: {colors['text']};
            }}
            QLabel {{
                color: {colors['text']};
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {colors['hover']};
            }}
            QPushButton#theme-switch {{
                background-color: transparent;
                color: {colors['text']};
                padding: 5px;
            }}
            QPushButton#theme-switch:hover {{
                background-color: {colors['secondary']};
            }}
            QFrame#action-card, QGroupBox {{
                background-color: {colors['card_bg']};
                border: 1px solid {colors['border']};
                border-radius: 5px;
                padding: 15px;
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                background-color: {colors['card_bg']};
            }}
            QTabWidget::tab-bar {{
                left: 5px; /* move to the right by 5px */
            }}
            QTabBar::tab {{
                background: {colors['secondary']};
                color: {colors['text']};
                padding: 10px;
                border: 1px solid {colors['border']};
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {colors['card_bg']};
                border-bottom-color: {colors['card_bg']}; /* same as pane color */
            }}
            QTabBar::tab:hover {{
                background: {colors['hover']};
                color: white;
            }}
            QTextEdit {{
                background-color: {colors['secondary']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 5px;
                padding: 10px;
            }}
            QComboBox {{
                background-color: {colors['secondary']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 5px;
                padding: 5px;
            }}
            QCheckBox {{
                color: {colors['text']};
            }}
            QFrame#status-bar {{
                background-color: {colors['secondary']};
                color: {colors['text']};
                border-top: 1px solid {colors['border']};
                padding: 5px;
            }}
            QLabel#app-title {{
                font-size: 24px;
                font-weight: bold;
                color: {colors['primary']};
            }}
            QLabel#schedule-status-label {{
                font-weight: bold;
            }}
        """
        self.setStyleSheet(stylesheet)

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.app.settings.get("application.theme", "light") # Use nested key
        new_theme = "dark" if current_theme == "light" else "light"
        self.app.settings.set("application.theme", new_theme) # Use nested key
        self._apply_theme()


class UpdateThread(QThread):
    finished = pyqtSignal()
    update_signal = pyqtSignal(str) # Signal to update status label

    def __init__(self, directory, git_operations):
        super().__init__()
        self.directory = directory
        self.git_operations = git_operations
        self.logger = logging.getLogger(__name__) # Get logger for the thread

    def run(self):
        self.update_signal.emit(f"Scanning {self.directory}...")
        repos = self.git_operations.scan_directories(self.directory)
        self.update_signal.emit(f"Found {len(repos)} repositories. Updating...")

        update_count = 0
        error_count = 0

        for repo_path in repos:
            self.update_signal.emit(f"Updating {repo_path}...")
            success, message = self.git_operations.pull_repository(str(repo_path))
            if success:
                update_count += 1
                self.logger.info(f"Successfully updated {repo_path}: {message}")
            else:
                error_count += 1
                self.logger.error(f"Failed to update {repo_path}: {message}")

        completion_message = f"Update complete: {update_count} successful, {error_count} failed."
        self.update_signal.emit(completion_message)
        self.logger.info(completion_message)

        self.finished.emit()

# Note: The original _clear_logs and _filter_logs methods in MainWindow
# need to be updated to work with the standard logging file format.
# The current implementation in this file is a basic placeholder.
