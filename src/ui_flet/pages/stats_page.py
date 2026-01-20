"""
Stats for Nerds - Display application statistics and info.
"""

import flet as ft
from typing import Callable, Optional


class StatsPage(ft.Column):
    """Display application statistics and information."""

    def __init__(self, on_close: Optional[Callable] = None):
        """
        Initialize stats page.

        Args:
            on_close: Callback when dialog is closed
        """
        super().__init__(expand=True, spacing=12)

        self.on_close = on_close

        title = ft.Text("Stats for Nerds", size=18, weight="bold")

        stats_content = ft.Column(
            controls=[
                ft.Text("Application Statistics", weight="bold"),
                ft.Text("Total Cases: 0"),
                ft.Text("Total Entities: 0"),
                ft.Text("API Calls: 0"),
                ft.Divider(),
                ft.Text("System Information", weight="bold"),
                ft.Text("Version: 0.1.0"),
                ft.Text("Platform: Windows"),
            ],
            spacing=8,
        )

        close_btn = ft.TextButton("Close", on_click=lambda e: self._on_close())

        self.controls = [
            title,
            ft.Divider(),
            stats_content,
            ft.Container(height=20),
            close_btn,
        ]

    def _on_close(self):
        """Close dialog."""
        if self.on_close:
            self.on_close()
