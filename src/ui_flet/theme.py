"""
Dark theme color scheme for SOC Case Builder Flet UI.
All colors are defined in hex format.
"""

# Primary colors
PRIMARY_BG = "#1e1e1e"  # Main background
SECONDARY_BG = "#2d2d2d"  # Secondary background (cards, panels)
TERTIARY_BG = "#3d3d3d"  # Tertiary background (hover states)

# Text colors
PRIMARY_TEXT = "#e0e0e0"  # Main text
SECONDARY_TEXT = "#b0b0b0"  # Secondary/muted text
TERTIARY_TEXT = "#808080"  # Tertiary/disabled text

# Accent colors
PRIMARY_ACCENT = "#007acc"  # Blue accent (buttons, links)
SECONDARY_ACCENT = "#cc6633"  # Orange accent
SUCCESS_COLOR = "#4ec9b0"  # Green for success
WARNING_COLOR = "#ce9178"  # Orange for warning
ERROR_COLOR = "#f48771"  # Red for error

# Border colors
BORDER_COLOR = "#464646"  # Light border
BORDER_LIGHT = "#3d3d3d"  # Very light border

# Component-specific colors
INPUT_BG = "#252526"  # Text input background
INPUT_BORDER = "#555555"  # Text input border
BUTTON_BG = PRIMARY_ACCENT  # Button background
BUTTON_HOVER = "#006699"  # Button hover state
BUTTON_TEXT = PRIMARY_TEXT  # Button text

# Status colors
ENRICHED = SUCCESS_COLOR  # Entity enriched status
PENDING = WARNING_COLOR  # Entity pending enrichment
ERROR = ERROR_COLOR  # Entity error status

def apply_dark_theme(page):
    """Apply dark theme to Flet page."""
    page.bgcolor = PRIMARY_BG
    page.theme_mode = "dark"
