from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class Themes:
    @staticmethod
    def get_light_theme():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#3498db"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        palette.setColor(QPalette.ColorRole.Base, QColor("white"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#ecf0f1"))
        return palette

    @staticmethod
    def get_dark_theme():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ecf0f1"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#3498db"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#34495e"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2c3e50"))
        return palette
