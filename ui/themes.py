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
        """
