# AutoRepo - Automatic Repository Updater

## Description
AutoRepo is a Python-based application designed for Windows that automates the process of updating local Git repositories. It features a user-friendly GUI built with PyQt6, allowing users to:
- Scan specified directories recursively for Git repositories (up to a configurable depth).
- Schedule automatic repository updates using the Windows Task Scheduler at specific times and on chosen days.
- Safely pull updates from remote repositories, preventing accidental pushes.
- Monitor the status of repositories and update operations through the GUI.
- Configure various settings like theme (light/dark), scan depth, logging preferences, and scheduling options.
- View detailed logs of all operations within the application, with options for filtering and clearing.

## Installation & Setup

### Prerequisites
- **Python:** Version 3.13 or higher.
- **uv:** A fast Python package installer and resolver. ([Installation Guide](https://github.com/astral-sh/uv#installation))
- **Git:** Must be installed and accessible in your system's PATH. ([Download Git](https://git-scm.com/downloads))
- **Operating System:** Windows (required for the scheduling feature which utilizes Windows Task Scheduler).

### Installation Steps
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AlexJ-StL/autorepo.git
    cd autorepo
    ```

2.  **Create and activate a virtual environment (Recommended):**
    *Using `uv`:*
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows Git Bash or Linux/macOS
    # or
    .\.venv\Scripts\activate  # On Windows Command Prompt or PowerShell
    ```
    *Alternatively, using Python's built-in `venv`:*
    ```bash
    python -m venv .venv
    # Activate as shown above
    ```

3.  **Install dependencies using uv:**
    *Option A: Using `pyproject.toml` (if dependencies are fully listed there)*
    ```bash
    uv pip install .
    # For development dependencies (if defined in pyproject.toml)
    # uv pip install ".[dev]"
    ```
    *Option B: Using `requirements.txt` (if present)*
    ```bash
    uv pip install -r requirements.txt
    # For development dependencies (if in requirements-dev.txt)
    # uv pip install -r requirements-dev.txt
    ```
    *Choose the option that matches how your dependencies are managed.*

4.  **Run the application:**
    ```bash
    python main.py
    ```
    *(Or, if using uv's run command)*
    ```bash
    uv run python main.py
    ```

## Features

### GUI Interface (PyQt6)
-   **Modern UI:** Clean and intuitive interface built with PyQt6.
-   **Tabs:** Organized sections for Status, Settings, Logs, and Scheduling.
-   **Theme Support:** Toggle between Light and Dark themes.
-   **Directory Selection:** Easily select the root directory for repository scanning.
-   **Real-time Feedback:** Status bar provides updates on ongoing operations.
-   **Responsive:** Multi-threaded updates ensure the UI remains responsive.

### Git Operations (`AutomaticRepoUpdater/git_operations.py`)
-   **Repository Scanning:** Recursively finds Git repositories within the selected directory up to a specified depth.
-   **Safe Pulling:** Fetches and merges updates (`git pull`) without pushing changes.
-   **Dirty Repository Handling:** Detects repositories with uncommitted changes and logs warnings (configurable behavior planned).
-   **Logging:** Records detailed information about scan and update operations.

### Scheduling (`scheduler.py`)
-   **Windows Task Scheduler:** Integrates directly with the Windows Task Scheduler for reliable background updates.
-   **Configurable Schedule:** Set specific times (hour/minute) and days of the week for updates via the UI.
-   **Enable/Disable:** Easily toggle the scheduled task on or off.
-   **Notifications:** Uses `win10toast` to provide notifications for scheduled runs (start/completion/failure).

### Logging System (`utils/logger.py`)
-   **Detailed Tracking:** Logs events with timestamps, levels (INFO, ERROR, WARNING), and messages.
-   **Configurable Format:** Choose between JSON or CSV log formats via settings.
-   **Log Retention:** Set the number of days logs should be kept (configurable).
-   **In-App Viewer:** Dedicated "Logs" tab displays recent logs with filtering (All, Info, Warning, Error, Success) and clearing capabilities.

### Configuration (`utils/settings.py`, `settings.json`)
-   **Persistent Settings:** Configuration is saved in `settings.json` in the project root directory.
-   **UI Controls:** Most settings are configurable through the "Settings" tab in the GUI.
-   **Key Settings:** Theme, max repository scan depth, auto-save preference, last selected directory, log format, log retention, schedule details (enabled, days, time), notification preferences.

## Directory Structure

```
autorepo/
├── __pycache__/
│   └── scheduler.cpython-313.pyc
├── AutomaticRepoUpdater/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-311.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── git_operations.cpython-311.pyc
│   │   └── git_operations.cpython-313.pyc
│   ├── git_operations.py
│   └── src/
│       └── AutomaticRepoUpdater.md
├── autorepo-cline_task_dec-20-2024_9-21-34-am.md
├── Autorepo_directory_tree-L3.txt
├── cline_task_dec-20-2024_12-42-12-pm.md
├── LICENSE
├── llm-prompting-notepad.txt
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── scheduler.py
├── settings.json
├── src/
│   ├── autorepo.md
│   └── custom_instructions.txt
├── tests/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-311.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── test_main_window.cpython-311-pytest-8.3.3.pyc
│   │   ├── test_main_window.cpython-311-pytest-8.3.4.pyc
│   │   ├── test_main_window.cpython-313-pytest-8.3.4.pyc
│   │   └── test_main_window.cpython-313-pytest-8.3.5.pyc
│   ├── src/
│   │   └── tests.md
│   └── test_main_window.py
├── ui/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-311.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── main_window.cpython-311.pyc
│   │   ├── main_window.cpython-313.pyc
│   │   ├── themes.cpython-311.pyc
│   │   └── themes.cpython-313.pyc
│   ├── main_window.py
│   ├── src/
│   │   └── ui.md
│   ├── themes.py
│   └── ui.py
├── utils/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-311.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── logger.cpython-311.pyc
│   │   ├── logger.cpython-313.pyc
│   │   ├── settings.cpython-311.pyc
│   │   └── settings.cpython-313.pyc
│   ├── logger.py
│   ├── settings.py
│   └── src/
│       └── utils.md
└── uv.lock
```

## Configuration
The application stores its configuration in `settings.json` located in the project's root directory. Key configurable options include:
-   `theme`: "light" or "dark" UI theme.
-   `max_depth`: Maximum depth to scan for repositories.
-   `auto_save`: Boolean, currently related to repository list saving (may need review).
-   `last_directory`: The last directory selected for scanning.
-   `log_format`: "JSON" or "CSV".
-   `log_retention`: Number of days to keep log files.
-   `schedule_enabled`: Boolean, enables/disables the scheduled task.
-   `schedule_days`: List of days (e.g., ["Mon", "Wed", "Fri"]) for the task to run.
-   `schedule_hour`: Hour (0-23) for the task to run.
-   `schedule_minute`: Minute (0-59) for the task to run.
-   `schedule_notification`: Time before update to show notification (e.g., "5 minutes").
-   `notifications_enabled`: Boolean, enables/disables Windows toast notifications.
-   `notification_sound`: Boolean, enables/disables sound for notifications.

## Changelog

### Version 0.2.0 (2024-12-20)
-   Initialized Git repository and added `.gitignore`.
-   Updated project version to 0.2.0 in `pyproject.toml`.
-   Updated `README.md` significantly to reflect current features, installation steps (using `uv`), configuration, and directory structure.
-   Corrected previous `AttributeError` issues (`_toggle_theme`, `_clear_logs`, `last_directory` access).

### Version 0.1.0 (2024-11-21)
-   Initial release.
-   PyQt6-based GUI implementation.
-   Core Git repository scanning and updating functionality.
-   Basic Windows Task Scheduler integration.
-   JSON/CSV logging system.
-   Settings management (`settings.json`).
-   Dark/Light theme support.
-   Multi-threaded repository updates.

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.