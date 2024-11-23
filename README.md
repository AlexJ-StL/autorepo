# AutoRepo - Automatic Repository Updater

## Description
AutoRepo is a Python-based application that provides automated Git repository management with scheduling capabilities. It allows users to:
- Scan directories recursively for Git repositories (up to configurable depth)
- Schedule automatic updates at specific times and days
- Pull updates from remote repositories safely (without pushing)
- Monitor repository status through a modern PyQt6-based GUI interface
- Handle dirty repositories gracefully with configurable error handling
- Log all operations with detailed tracking in JSON or CSV format

## Installation & Setup

### Prerequisites
- Python 3.13 or higher
- Poetry package manager
- Windows OS (required for scheduler functionality)
- Git installed and configured

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/yourusername/autorepo.git
cd autorepo
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Run the application:
```bash
poetry run python main.py
```

## Features

### GUI Interface
- Simple and intuitive PyQt6-based interface
- Directory selection for repository scanning
- Real-time status updates during operations
- Multi-threaded repository updates to maintain responsiveness

### Git Operations
- Safe repository pulling (prevents accidental pushes)
- Dirty repository detection and handling
- Configurable scan depth for repository discovery
- Detailed operation logging

### Scheduling
- Windows Task Scheduler integration
- Configurable update times and days
- Enable/disable scheduling through settings
- Immediate manual updates when needed

### Logging System
- Detailed operation tracking
- Multiple format support (JSON/CSV)
- Rolling or session-based log files
- Operation statistics and error tracking

## Directory Structure
```
autorepo/
├── AutomaticRepoUpdater/
│   └── git_operations.py      # Git repository management
├── main.py                    # Application entry point
├── README.md
├── scheduler.py               # Windows task scheduling
├── ui/
│   ├── __init__.py
│   ├── main_window.py        # PyQt6 main interface
│   └── ui.py                 # Additional UI components
└── utils/
    ├── __init__.py
    ├── logger.py             # Logging functionality
    └── settings.py           # Configuration management
```

## Configuration
The application stores its configuration in `~/.autorepo/settings.json` and includes:
- Theme preferences (light/dark)
- Last used directory
- Scheduling settings
- Error handling preferences
- Logging configuration

## Changelog

### Version 0.1.0 (2024-11-21)
- Initial release
- PyQt6-based GUI implementation
- Git repository scanning and updating
- Windows Task Scheduler integration
- JSON/CSV logging system
- Settings management
- Dark/Light theme support
- Multi-threaded repository updates

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
