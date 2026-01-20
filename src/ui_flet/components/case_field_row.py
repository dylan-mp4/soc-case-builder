"""
Reusable case field row component for dynamic field management.
"""

import flet as ft
from typing import Callable, Optional


class CaseFieldRow(ft.Row):
    """
    A reusable row component for case fields.
    Contains: TextField + 5 action buttons (Query, Search, Add, Remove, Status)
    """

    def __init__(
        self,
        field_label: str,
        field_value: str = "",
        index: int = 0,
        on_query: Optional[Callable] = None,
        on_search: Optional[Callable] = None,
        on_add: Optional[Callable] = None,
        on_remove: Optional[Callable] = None,
        on_value_change: Optional[Callable] = None,
        status: str = "",  # "enriched", "pending", "error", or ""
    ):
        """
        Initialize field row.

        Args:
            field_label: Label of the field (IP, Domain, etc.)
            field_value: Initial value of the field
            on_query: Callback for query button
            on_search: Callback for search button
            on_add: Callback for add button
            on_remove: Callback for remove button
            on_value_change: Callback when field value changes
            status: Current status icon/indicator
        """
        super().__init__(spacing=8, vertical_alignment="center")

        self.field_label = field_label
        self.on_query = on_query
        self.on_search = on_search
        self.on_add = on_add
        self.on_remove = on_remove
        self.index = index
        self.status = status

        # Main text field
        self.text_field = ft.TextField(
            value=field_value,
            label=field_label,
            expand=True,
            on_change=lambda e: on_value_change(self.field_label, self.index, e.control.value)
            if on_value_change
            else None,
        )

        # Status indicator (small icon)
        self.status_icon = ft.Icon(
            ft.Icons.CIRCLE,
            size=12,
            color="#808080" if not status else status,
            visible=bool(status),
        )

        # Query button (🔨)
        query_btn = ft.IconButton(
            icon=ft.Icons.BUILD,
            tooltip="Query",
            on_click=lambda e: on_query(field_label, self.text_field.value) if on_query else None,
        )

        # Search button (🔍)
        search_btn = ft.IconButton(
            icon=ft.Icons.SEARCH,
            tooltip="Search Cases",
            on_click=lambda e: on_search(field_label, self.text_field.value) if on_search else None,
        )

        # Add button (+)
        add_btn = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="Add Field",
            on_click=lambda e: on_add(field_label) if on_add else None,
        )

        # Remove button (❌)
        remove_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            tooltip="Remove Field",
            on_click=lambda e: on_remove(field_label, self.index) if on_remove else None,
        )

        # Add components to row
        self.controls = [
            self.text_field,
            self.status_icon,
            query_btn,
            search_btn,
            add_btn,
            remove_btn,
        ]

    def update_status(self, status: str):
        """Update the status indicator."""
        self.status = status
        self.status_icon.visible = bool(status)
        self.status_icon.color = status
        self.update()

    def get_value(self) -> str:
        """Get the current field value."""
        return self.text_field.value

    def set_value(self, value: str):
        """Set the field value."""
        self.text_field.value = value
        self.update()
