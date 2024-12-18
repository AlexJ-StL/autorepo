# test_main_window.py

```python
import pytest
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    return test_app

@pytest.fixture
def main_window(app, qtbot):
    window = MainWindow(app)
    qtbot.addWidget(window)
    return window

def test_window_maximized(main_window):
    assert main_window.isMaximized()

def test_initial_ui_elements(main_window):
    assert main_window.select_dir_button is not None
    assert main_window.update_button is not None
    assert main_window.status_label is not None
    assert main_window.tab_widget is not None

def test_settings_tab_exists(main_window):
    assert main_window.tab_widget.findText("Settings") != -1

def test_logs_tab_exists(main_window):
    assert main_window.tab_widget.findText("Logs") != -1

def test_theme_switching(main_window, qtbot):
    main_window.theme_combo.setCurrentText("Dark")
    assert main_window.app.settings.theme == "dark"
    main_window.theme_combo.setCurrentText("Light")
    assert main_window.app.settings.theme == "light"

def test_log_viewer_refresh(main_window, qtbot):
    main_window.app.logger.log_event("Test event")
    main_window._refresh_logs()
    assert "Test event" in main_window.log_viewer.toPlainText()

```

# __init__.py

```python
# This file ensures the tests directory can be treated as a package.

```

