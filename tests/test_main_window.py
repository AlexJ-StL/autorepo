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
