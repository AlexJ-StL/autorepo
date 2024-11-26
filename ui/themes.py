from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class Themes:
    def __init__(self):
        self.current_theme = "light"

        # Light theme colors
        self.light = {
            "window": "#FFFFFF",
            "text": "#2C3E50",
            "primary": "#3498DB",
            "secondary": "#E0E0E0",
            "accent": "#2ECC71",
            "error": "#E74C3C",
            "card_bg": "#F8F9FA",
            "border": "#DEE2E6"
        }

        # Dark theme colors
        self.dark = {
            "window": "#1A1A1A",
            "text": "#ECEFF4",
            "primary": "#5E81AC",
            "secondary": "#4C566A",
            "accent": "#A3BE8C",
            "error": "#BF616A",
            "card_bg": "#2E3440",
            "border": "#3B4252"
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
            Palette.ColorRole.Button,
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
                background-color: {colors["accent"]};
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
            }}"""
