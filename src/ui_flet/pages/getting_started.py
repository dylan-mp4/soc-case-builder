"""
Getting Started - Welcome/onboarding dialog.
"""

import flet as ft
from typing import Callable, Optional


class GettingStartedPage(ft.Column):
    """Welcome screen for first-time users."""

    def __init__(self, on_close: Optional[Callable] = None):
        """
        Initialize getting started page.

        Args:
            on_close: Callback when user closes welcome
        """
        super().__init__(expand=True, horizontal_alignment="center", spacing=16)

        self.on_close = on_close

        welcome_text = ft.Column(
            controls=[
                ft.Text(
                    "Welcome to SOC Case Builder",
                    size=24,
                    weight="bold",
                    text_align="center",
                ),
                ft.Text(
                    "A powerful tool for building and managing security cases",
                    size=14,
                    text_align="center",
                    color="#b0b0b0",
                ),
            ],
            horizontal_alignment="center",
        )

        features_text = ft.Column(
            controls=[
                ft.Text("Getting Started", weight="bold", size=16),
                ft.Text("1. Create cases with dynamic field management", size=12),
                ft.Text("2. Add entities (IP, Domain, Hash, URL, etc.)", size=12),
                ft.Text("3. Compile and save cases to JSON", size=12),
                ft.Text("4. Configure API keys in Settings", size=12),
                ft.Text("5. Search saved cases and manage workflows", size=12),
            ],
            spacing=8,
        )

        close_btn = ft.ElevatedButton(
            "Get Started",
            icon="check_circle",
            on_click=self._on_close,
        )

        self.controls = [
            ft.Container(height=50),
            welcome_text,
            ft.Divider(),
            features_text,
            ft.Container(height=50),
            close_btn,
        ]

    def _on_close(self, e):
        """Close welcome screen."""
        if self.on_close:
            self.on_close()
