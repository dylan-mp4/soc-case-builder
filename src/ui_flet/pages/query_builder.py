"""
Query Builder Dialog - Create and manage query templates.
"""

import flet as ft
from typing import Callable, Optional


class QueryBuilderPage(ft.Column):
    """Interface for creating and managing query templates."""

    def __init__(self, on_close: Optional[Callable] = None):
        """
        Initialize query builder page.

        Args:
            on_close: Callback when dialog is closed
        """
        super().__init__(expand=True, spacing=12)

        self.on_close = on_close

        title = ft.Text("Query Builder", size=18, weight="bold")

        query_name_field = ft.TextField(label="Query Name", expand=True)
        entity_type_dropdown = ft.Dropdown(
            label="Entity Type",
            options=[
                ft.dropdown.Option("IP"),
                ft.dropdown.Option("Domain"),
                ft.dropdown.Option("Hash"),
                ft.dropdown.Option("URL"),
            ],
        )
        query_template_field = ft.TextField(
            label="Query Template (use {{Entity}} placeholder)",
            multiline=True,
            min_lines=4,
            expand=True,
        )

        save_btn = ft.ElevatedButton("Save Query", icon="save")
        close_btn = ft.TextButton("Close", on_click=lambda e: self._on_close())

        self.controls = [
            title,
            ft.Divider(),
            query_name_field,
            entity_type_dropdown,
            query_template_field,
            ft.Row(controls=[save_btn, close_btn]),
        ]

    def _on_close(self):
        """Close dialog."""
        if self.on_close:
            self.on_close()
