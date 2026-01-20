"""
Query Finder Dialog - Look up query templates by entity type.
"""

import flet as ft
from typing import Callable, Optional


class QueryFinderPage(ft.Column):
    """Interface for finding and using query templates."""

    def __init__(self, state=None, on_close: Optional[Callable] = None):
        """
        Initialize query finder page.

        Args:
            state: Centralized AppState
            on_close: Callback when dialog is closed
        """
        super().__init__(expand=True, spacing=12)

        self.state = state
        self.on_close = on_close
        self.selected_query = None
        self.entity_value = ""

        title = ft.Text("Query Finder", size=18, weight="bold")

        self.entity_type_dropdown = ft.Dropdown(
            label="Select Entity Type",
            options=[
                ft.dropdown.Option("IP"),
                ft.dropdown.Option("Domain"),
                ft.dropdown.Option("Hash"),
                ft.dropdown.Option("URL"),
            ],
            expand=True,
            on_change=self._on_entity_type_change,
        )

        self.entity_value_field = ft.TextField(
            label="Entity Value",
            expand=True,
        )

        self.queries_list = ft.ListView(
            controls=[],
            expand=True,
        )

        # Query output display
        self.query_output = ft.TextField(
            label="Query Template (with substitution)",
            multiline=True,
            min_lines=6,
            expand=True,
            read_only=True,
        )

        copy_btn = ft.ElevatedButton(
            "Copy to Clipboard",
            icon="content_copy",
            on_click=self._on_copy,
        )
        close_btn = ft.TextButton("Close", on_click=lambda e: self._on_close())

        self.controls = [
            title,
            ft.Divider(),
            ft.Row([self.entity_type_dropdown, self.entity_value_field]),
            ft.Text("Available Queries:", weight="bold"),
            self.queries_list,
            ft.Divider(),
            self.query_output,
            ft.Row(controls=[copy_btn, close_btn]),
        ]

    def _on_entity_type_change(self, e):
        """Handle entity type dropdown change."""
        self._load_queries_for_type()

    def _load_queries_for_type(self):
        """Load queries for selected entity type."""
        self.queries_list.controls.clear()

        if not self.state or not self.entity_type_dropdown.value:
            self.update()
            return

        entity_type = self.entity_type_dropdown.value
        queries = self.state.get_queries_for_entity(entity_type)

        if not queries:
            self.queries_list.controls.append(
                ft.Text("No queries found for this entity type")
            )
        else:
            for query in queries:
                query_name = query.get("name", "Unnamed")
                query_btn = ft.TextButton(
                    text=query_name,
                    on_click=lambda e, q=query: self._on_query_selected(q),
                )
                self.queries_list.controls.append(query_btn)

        self.update()

    def _on_query_selected(self, query):
        """Handle query selection."""
        self.selected_query = query
        self._update_query_output()

    def _update_query_output(self):
        """Update query output with entity substitution."""
        if not self.selected_query:
            self.query_output.value = ""
            self.update()
            return

        entity_value = self.entity_value_field.value.strip()
        if not entity_value:
            # Show template without substitution
            self.query_output.value = self.selected_query.get("template", "")
        else:
            # Apply entity value to template
            self.query_output.value = self.state.apply_query_template(
                self.selected_query, entity_value
            )

        self.update()

    def _on_copy(self, e):
        """Copy query output to clipboard."""
        if self.query_output.value:
            import pyperclip
            try:
                pyperclip.copy(self.query_output.value)
                if hasattr(self, 'page') and self.page:
                    snack = ft.SnackBar(ft.Text("Copied to clipboard!"))
                    snack.open = True
                    self.page.overlay.append(snack)
                    self.page.update()
            except ImportError:
                # pyperclip not available, fallback to just showing message
                print("Copy to clipboard not available (install pyperclip)")

    def _on_close(self):
        """Close dialog."""
        if self.on_close:
            self.on_close()

