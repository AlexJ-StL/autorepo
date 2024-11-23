# AutoRepo - Automatic Repository Updater

## Description
AutoRepo is a Python-based application that provides automated Git repository management with scheduling capabilities. It allows users to:
- Scan directories for Git repositories
- Schedule automatic updates
- Pull updates from remote repositories
- Monitor repository status through a GUI interface
- Log all operations with detailed tracking

## Installation & Setup

### Prerequisites
- Python 3.13 or higher
- Poetry package manager
- Windows OS (for scheduler functionality)

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

## Directory Structure
```
autorepo/
├── AutomaticRepoUpdater/
│   └── git_operations.py
├── main.py
├── README.md
├── scheduler.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   └── ui.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── settings.py
```

## Changelog

### Version 0.1.0 (2024-11-21)
- Initial release
- Basic GUI implementation with PyQt6
- Git repository scanning and updating
- Scheduling functionality
- Logging system
- Settings management
- Dark/Light theme support

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