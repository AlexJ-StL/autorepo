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

            self.total_logs_label.setText(
                f"Total Logs: {total_logs}"
            )
            self.error_count_label.setText(
                f"Errors: {error_count}"
            )
            self.warning_count_label.setText(
                f"Warnings: {warning_count}"
            )

            for log in logs:
                log_message = (
                    f"[{log.get('timestamp')}] "
                    f"[{log.get('level')}] "
                    f"{log.get('message')}\n"
                )
                self.logs_text.append(log_message)

        except Exception as e:
            self.logs_text.append(f"Error refreshing logs: {e}")

    def _filter_logs(self, filter_level):
        """Filter logs based on the selected level"""
        self.logs_text.clear()
        try:
            logs = self.app.logger.get_recent_logs()
            total_logs = len(logs)
            error_count = sum(
                1 for log in logs if log.get('level') == 'ERROR'
            )
            warning_count = sum(
                1 for log in logs if log.get('level') == 'WARNING'
            )

            self.total_logs_label.setText(
                f"Total Logs: {total_logs}"
            )
            self.error_count_label.setText(
                f"Errors: {error_count}"
            )
            self.warning_count_label.setText(
                f"Warnings: {warning_count}"
            )

            for log in logs:
                if (
                    filter_level == "All"
                    or log.get('level') == filter_level.upper()
                ):
                    log_message = (
                        f"[{log.get('timestamp')}] "
                        f"[{log.get('level')}] "
                        f"{log.get('message')}\n"
                    )
                    self.logs_text.append(log_message)

        except Exception as e:
            self.logs_text.append(f"Error filtering logs: {e}")

    def _apply_theme(self):
        """Apply the current theme to the application"""
        theme = self.app.settings.get("theme", "light")
        if theme == "light":
            self.setStyleSheet(
                """
                /* Light Theme Styles */
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: #333;
                }
                QPushButton {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton#primary-button {
                    background-color: #007bff;
                    color: white;
                }
                QTextEdit {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                }
                QTabWidget::pane {
                    border: 1px solid #ccc;
                    background-color: #fff;
                }
                QTabWidget::tab-bar::tab {
                    background-color: #eee;
                    color: #333;
                    padding: 5px 15px;
                    border-top-left-radius: 3px;
                    border-top-right-radius: 3px;
                    border: 1px solid #ccc;
                    border-bottom: none;
                }
                QTabWidget::tab-bar::tab:selected {
                    background-color: #fff;
                    border-bottom: 1px solid #fff;
                }
                QGroupBox {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    background-color: #f0f0f0;
                }
                QComboBox {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QCheckBox {
                    color: #333;
                }
                #app-title {
                    font-size: 20px;
                    font-weight: bold;
                    color: #333;
                }
                #theme-switch {
                    background-color: #ffca28;
                    color: #333;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                #action-card {
                    background-color: #fff;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                #status-bar {
                    background-color: #e0e0e0;
                    border-top: 1px solid #ccc;
                    padding: 5px;
                }
                #status-text {
                    color: #333;
                    font-style: italic;
                }
                #log-display {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }
                #schedule-status-label {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                """
            )
            theme_switch_text = "Dark Mode"
        else:
            self.setStyleSheet(
                """
                /* Dark Theme Styles */
                QMainWindow {
                    background-color: #333;
                }
                QLabel {
                    color: #eee;
                }
                QPushButton {
                    background-color: #444;
                    color: #eee;
                    border: 1px solid #555;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton#primary-button {
                    background-color: #00aaff;
                    color: #333;
                }
                QTextEdit {
                    background-color: #555;
                    color: #eee;
                    border: 1px solid #666;
                }
                QTabWidget::pane {
                    border: 1px solid #666;
                    background-color: #444;
                }
                QTabWidget::tab-bar::tab {
                    background-color: #555;
                    color: #eee;
                    padding: 5px 15px;
                    border-top-left-radius: 3px;
                    border-top-right-radius: 3px;
                    border: 1px solid #666;
                    border-bottom: none;
                }
                QTabWidget::tab-bar::tab:selected {
                    background-color: #444;
                    border-bottom: 1px solid #444;
                }
                QGroupBox {
                    border: 1px solid #666;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    background-color: #333;
                    color: #eee;
                }
                QComboBox {
                    background-color: #444;
                    color: #eee;
                    border: 1px solid #666;
                    padding: 5px;
                    border-radius: 3px;
                }
                QCheckBox {
                    color: #eee;
                }
                #app-title {
                    font-size: 20px;
                    font-weight: bold;
                    color: #eee;
                }
                #theme-switch {
                    background-color: #ffca28;
                    color: #333;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                #action-card {
                    background-color: #444;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }
                #status-bar {
                    background-color: #555;
                    border-top: 1px solid #666;
                    padding: 5px;
                }
                #status-text {
                    color: #eee;
                    font-style: italic;
                }
                #log-display {
                    background-color: #2b2b2b;
                    border: 1px solid #4d4d4d;
                    color: #f0f0f0;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }
                #schedule-status-label {
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #eee;
                }
                """
            )
            theme_switch_text = "Light Mode"
        self.findChild(QPushButton, "theme-switch").setText(
            theme_switch_text
        )

    def _toggle_theme(self):
        """Toggle the application theme between light and dark."""
        current_theme = self.app.settings.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.app.settings.set("theme", new_theme)
        self._apply_theme()

    def _clear_logs(self):
        """Clear the logs display."""
        self.logs_text.clear()

class UpdateThread(QThread):
    finished = pyqtSignal()
    update_signal = pyqtSignal(str)

    def __init__(self, directory, git_operations):
        super().__init__()
        self.directory = directory
        self.git_operations = git_operations

    def run(self):
        try:
            self.git_operations.update_all_repositories(
                self.directory, update_signal=self.update_signal
            )
        except Exception as e:
            self.update_signal.emit(f"Error during update: {e}")
        finally:
            self.finished.emit()
