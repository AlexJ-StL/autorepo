# ui/themes.py

def get_theme_colors(theme_name: str):
    """
    Returns theme color dictionary based on theme name.
    """
    themes = {
        "dark": {
            "window": "#1A202C",
            "text": "#F7FAFC",
            "primary": "#4299E1",
            "secondary": "#2D3748",
            "accent": "#48BB78",
            "error": "#F56565",
            "card_bg": "#2D3748",
            "border": "#4A5568",
            "hover": "#2B6CB0",
            "disabled": "#718096",
            "success": "#38A169",
            "warning": "#D69E2E"
        },
        "light": {
            "window": "#F5F7FA",
            "text": "#2C3E50",
            "primary": "#3498DB",
            "secondary": "#E8EEF2",
            "accent": "#2ECC71",
            "error": "#E74C3C",
            "card_bg": "#FFFFFF",
            "border": "#CBD5E0",
            "hover": "#2980B9",
            "disabled": "#BDC3C7",
            "success": "#27AE60",
            "warning": "#F39C12"
        }
    }
    return themes.get(theme_name, themes["light"]) # Default to light theme
