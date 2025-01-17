# main_window.py

```python
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
    QTabWidget,
    QFrame,
    QGroupBox, QComboBox, QCheckBox, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from AutomaticRepoUpdater.git_operations import GitOperations


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.git_operations = GitOperations(
            self.app.settings,
            self.app.logger
        )
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

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.app.settings.last_directory
        )
        if directory:
            self.app.settings.last_directory = directory

    def update_repositories(self):
        directory = self.app.settings.last_directory
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

        self.status_label.setText(
            f"Logs saved to {self.app.logger.log_dir}"
        )

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
                "max_depth",
                "2"
            ))
        )
        depth_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "max_depth", int(x)
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
                "auto_save",
                True
            )
        )
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
        enable_notif.setChecked(
            self.app.settings.get(
                "notifications_enabled",
                True
            )
        )
        enable_notif.toggled.connect(
            lambda x: self.app.settings.set(
                "notifications_enabled", x
            )
        )
        notif_layout.addWidget(enable_notif)

        # Notification sound
        sound_check = QCheckBox("Play notification sound")
        sound_check.setChecked(
            self.app.settings.get(
                "notification_sound",
                True
            )
        )
        sound_check.toggled.connect(
            lambda x: self.app.settings.set(
                "notification_sound", x
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
            self.app.settings.get("log_format", "JSON")
        )
        format_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "log_format", x
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
                "log_retention", "30"
            ))
        )
        retention_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "log_retention", int(x)
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
            self.app.settings.get("schedule_enabled", False)
        )
        enable_schedule.toggled.connect(
            lambda x: self.app.settings.set(
                "schedule_enabled", x
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
                "schedule_hour", "09"
            )).zfill(2)
        )

        minute_combo = QComboBox()
        minute_combo.addItems(
            [f"{i:02d}" for i in range(0, 60, 15)]
        )
        minute_combo.setCurrentText(
            str(self.app.settings.get(
                "schedule_minute", "00"
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
            "schedule_days",
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
                "schedule_notification",
                "5 minutes"
            )
        )
        notif_combo.currentTextChanged.connect(
            lambda x: self.app.settings.set(
                "schedule_notification", x
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

        # Manual schedule update button
        update_schedule_btn = QPushButton(
            "Update Schedule"
        )
        update_schedule_btn.setObjectName(
            "primary-button"
        )
        update_schedule_btn.clicked.connect(
            self._update_schedule
        )
        status_layout.addWidget(
            update_schedule_btn
        )

        layout.addWidget(status_group)

        # Add stretch to push everything to the top
        layout.addStretch()

        # Connect time selection changes
        hour_combo.currentTextChanged.connect(
            lambda x: self._update_schedule_time(
                x, minute_combo.currentText()
            )
        )
        minute_combo.currentTextChanged.connect(
            lambda x: self._update_schedule_time(
                hour_combo.currentText(), x
            )
        )

        return scheduler_widget

    def _update_schedule_days(self, day, checked):
        """Update the scheduled days in settings"""
        current_days = self.app.settings.get("schedule_days", [])
        if checked and day not in current_days:
            current_days.append(day)
        elif not checked and day in current_days:
            current_days.remove(day)
        self.app.settings.set("schedule_days", current_days)
        self._update_schedule()

    def _update_schedule_time(self, hour, minute):
        """Update the scheduled time in settings"""
        self.app.settings.set("schedule_hour", int(hour))
        self.app.settings.set("schedule_minute", int(minute))
        self._update_schedule()

    def _update_schedule(self):
        """Update the schedule based on current settings"""
        try:
            success, message = self.app.scheduler.update_schedule()
            if success:
                self.status_label.setText(message)
                next_run = self.app.scheduler.get_next_run()
                last_run = self.app.scheduler.get_last_run()

                self.next_run_label.setText(
                    "Next scheduled run"
                    f"{next_run if next_run else 'Not scheduled'}"
                )
                self.last_run_label.setText(
                    f"Last run: {last_run if last_run else 'Never'}"
                )
            else:
                QMessageBox.warning(self, "Schedule Update Error", message)
                self.status_label.setText("Failed to update schedule")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Schedule Update Error",
                f"Failed to update schedule: {str(e)}"
            )
            self.status_label.setText("Failed to update schedule")
            next_run = self.app.scheduler.get_next_run()
            last_run = self.app.scheduler.get_last_run()

            self.next_run_label.setText(
                "Next scheduled run: "
                f"{next_run if next_run else 'Not scheduled'}"
            )
            self.last_run_label.setText(
                "Last run: "
                f"{last_run if last_run else 'Never'}"
            )

    def _refresh_logs(self):
        """Refresh the logs display"""
        try:
            logs = self.app.logger.get_recent_logs()
            self.logs_text.clear()

            total_logs = len(logs)
            error_count = sum(
                1 for log in logs if log.get('level') == 'ERROR'
            )
            warning_count = sum(
                1 for log in logs if log.get('level') == 'WARNING'
            )

            for log in logs:
                self._format_and_append_log(log)

            self.total_logs_label.setText(
                f"Total Logs: {total_logs}"
            )
            self.error_count_label.setText(
                f"Errors: {error_count}"
            )
            self.warning_count_label.setText(
                f"Warnings: {warning_count}"
            )
        except Exception as e:
            self.logs_text.setText(f"Error loading logs: {str(e)}")

    def _clear_logs(self):
        """Clear the logs display and optionally the log file"""
        reply = QMessageBox.question(
            self,
            'Clear Logs',
            'Do you want to clear all logs? This cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.app.logger.clear_logs()
                self.logs_text.clear()
                self._refresh_logs()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to clear logs: {str(e)}"
                )

    def _filter_logs(self, filter_type):
        """Filter logs based on selected type"""
        try:
            logs = self.app.logger.get_recent_logs()
            self.logs_text.clear()

            filtered_logs = logs
            if filter_type != "All":
                filtered_logs = [
                    log for log in logs if log.get('level') ==
                    filter_type.upper()
                ]

            for log in filtered_logs:
                self._format_and_append_log(log)
        except Exception as e:
            self.logs_text.setText(f"Error filtering logs: {str(e)}")

    def _format_and_append_log(self, log):
        """Format and append a single log entry to the display"""
        timestamp = log.get('timestamp', '')
        level = log.get('level', 'INFO')
        message = log.get('message', '')

        # Color coding based on log level
        color = {
            'ERROR': '#F56565',
            'WARNING': '#D69E2E',
            'SUCCESS': '#38A169',
            'INFO': self.app.settings.get_theme_colors()['text']
        }.get(level, self.app.settings.get_theme_colors()['text'])

        formatted_log = (
            f'<span style="color: {color}">'
            f'[{timestamp}] {level}: {message}'
            f'</span><br>'
        )
        self.logs_text.insertHtml(formatted_log)


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

```

# themes.py

```python
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class Themes:
    def __init__(self):
        self.current_theme = "light"

        # Light theme colors
        self.light = {
            "window": "#F5F7FA",           # Light gray-blue background
            "text": "#2C3E50",             # Dark blue-gray text
            "primary": "#3498DB",          # Bright blue for primary actions
            "secondary": "#E8EEF2",        # Lighter blue-gray for secondary elements
            "accent": "#2ECC71",           # Green for success/positive actions
            "error": "#E74C3C",            # Red for errors/warnings
            "card_bg": "#FFFFFF",          # White for card backgrounds
            "border": "#CBD5E0",           # Medium gray for borders
            "hover": "#2980B9",            # Darker blue for hover states
            "disabled": "#BDC3C7",         # Gray for disabled elements
            "success": "#27AE60",          # Darker green for success messages
            "warning": "#F39C12"           # Orange for warnings
        }

        # Dark theme colors
        self.dark = {
            "window": "#1A202C",           # Dark blue-gray background
            "text": "#F7FAFC",             # Very light gray text
            "primary": "#4299E1",          # Bright blue for primary actions
            "secondary": "#2D3748",        # Medium gray-blue for secondary elements
            "accent": "#48BB78",           # Green for success/positive actions
            "error": "#F56565",            # Red for errors/warnings
            "card_bg": "#2D3748",          # Slightly lighter background for cards
            "border": "#4A5568",           # Medium gray for borders
            "hover": "#2B6CB0",            # Darker blue for hover states
            "disabled": "#718096",         # Gray for disabled elements
            "success": "#38A169",          # Darker green for success messages
            "warning": "#D69E2E"           # Orange for warnings
        }

    def get_palette(self, theme_name="light"):
        """Create and return a QPalette for the specified theme"""
        colors = self.light if theme_name == "light" else self.dark
        palette = QPalette()

        # Set window and widget colors
        palette.setColor(
            QPalette.ColorRole.Window,
            QColor(colors["window"])
        )
        palette.setColor(
            QPalette.ColorRole.WindowText,
            QColor(colors["text"])
        )
        palette.setColor(
            QPalette.ColorRole.Base,
            QColor(colors["card_bg"])
        )
        palette.setColor(
            QPalette.ColorRole.Text,
            QColor(colors["text"])
        )
        palette.setColor(
            QPalette.ColorRole.Button,
            QColor(colors["secondary"])
        )
        palette.setColor(
            QPalette.ColorRole.ButtonText,
            QColor(colors["text"])
        )
        palette.setColor(
            QPalette.ColorRole.Highlight,
            QColor(colors["primary"])
        )
        palette.setColor(
            QPalette.ColorRole.HighlightedText,
            QColor(colors["window"])
        )

        return palette

    def get_stylesheet(self, theme_name="light"):
        """Return the stylesheet for the specified theme"""
        colors = self.light if theme_name == "light" else self.dark

        return f"""
            QMainWindow {{
                background-color: {colors["window"]};
            }}

            #app-title {{
                color: {colors["text"]};
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }}

            #theme-switch {{
                background-color: {colors["secondary"]};
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
            }}

            #action-card {{
                background-color: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 15px;
            }}

            #primary-button {{
                background-color: {colors["primary"]};
                color: {colors["window"]};
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }}

            #primary-button:hover {{
                background-color: {colors["hover"]};
            }}

            #main-tabs {{
                background-color: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
            }}

            #status-bar {{
                background-color: {colors["card_bg"]};
                border-top: 1px solid {colors["border"]};
                padding: 5px;
            }}

            #status-text {{
                color: {colors["text"]};
            }}

            QTabWidget::pane {{
                border: 1px solid {colors["border"]};
                border-radius: 4px;
            }}

            QTabBar::tab {{
                background-color: {colors["secondary"]};
                color: {colors["text"]};
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}

            QTabBar::tab:selected {{
                background-color: {colors["primary"]};
                color: {colors["window"]}
            }}

            QWidget:disabled {{
                color: {colors["disabled"]};
            }}
            
            QPushButton:hover {{
                background-color: {colors["hover"]};
            }}
            
            QMessageBox {{
                background-color: {colors["window"]};
            }}
            
            QMessageBox QLabel {{
                color: {colors["text"]};
            }}
            
            QToolTip {{
                background-color: {colors["card_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                padding: 5px;
            }}
            
            QScrollBar:vertical {{
                background-color: {colors["window"]};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors["secondary"]};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors["primary"]};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {colors["card_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {colors["primary"]};
            }}
            
            #log-display {{
                background-color: {colors["card_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 10px;
                font-family: monospace;
            }}
            
            QGroupBox {{
                background-color: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 1em;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: {colors["text"]};
            }}

            QLabel#schedule-status-enabled { color: #27AE60; }
            QLabel#schedule-status-disabled { color: #E74C3C; }
            QLabel#schedule-status-pending { color: #F39C12; }
        }

        """

```

# ui.py

```python
import tkinter as tk
from tkinter import ttk


class MainWindow(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.title("Automatic Repo Updater")
        self.geometry("800x600")
        self.configure_theme()

        self.update_button = ttk.Button(
            self, text="Update Repositories", command=self.update_repositories
        )
        self.update_button.pack(pady=20)

        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack()

        self.theme_button = ttk.Button(
            self, text="Toggle Theme", command=self.toggle_theme
        )
        self.theme_button.pack(pady=10)

    def configure_theme(self):
        """Configure the theme based on settings"""
        if self.settings.theme == "dark":
            self.style = ttk.Style(self)
            self.style.theme_use('clam')
            self.style.configure(
                ".",
                background="#222222",
                foreground="white"
            )
            self.style.configure(
                "TButton",
                background="#333333",
                foreground="white"
            )
        else:
            self.style = ttk.Style(self)
            self.style.theme_use('clam')
            self.style.configure(
                ".",
                background="white",
                foreground="black"
            )
            self.style.configure(
                "TButton",
                background="#dddddd",
                foreground="black"
            )

    def toggle_theme(self):
        """Toggle the theme and update the UI"""
        if self.settings.theme == "dark":
            self.settings.theme = "light"
        else:
            self.settings.theme = "dark"
        self.settings.save_settings()
        self.configure_theme()

    def update_repositories(self):
        """Update the repositories and display the status"""
        self.status_label.config(text="Updating...")
        # Add logic to update repositories here
        self.status_label.config(text="Update complete")

```

# __init__.py

```python
# This file ensures the ui directory can be treated as a package.

```

