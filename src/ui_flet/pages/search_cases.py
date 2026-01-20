"""
Search Cases - Search and load saved cases.
"""

import flet as ft
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional
from datetime import datetime


class SearchCasesPage(ft.Column):
    """Interface for searching and loading saved cases."""

    def __init__(self, state=None, on_load_case: Optional[Callable] = None, on_close: Optional[Callable] = None):
        """
        Initialize search cases page.

        Args:
            state: Centralized AppState (for loading cases)
            on_load_case: Callback when case is loaded
            on_close: Callback when dialog is closed
        """
        super().__init__(expand=True, spacing=12)

        self.state = state
        self.on_load_case = on_load_case
        self.on_close = on_close
        self.saved_cases: List[Dict] = []
        self.filtered_cases: List[Dict] = []

        title = ft.Text("Search Cases", size=18, weight="bold")

        self.search_field = ft.TextField(
            label="Search by entity or case name",
            icon="search",
            expand=True,
            on_change=self._on_search_change,
        )

        # Results table
        self.results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Case Name")),
                ft.DataColumn(ft.Text("Created")),
                ft.DataColumn(ft.Text("Entities")),
                ft.DataColumn(ft.Text("Action")),
            ],
            rows=[],
            expand=True,
        )

        close_btn = ft.TextButton("Close", on_click=lambda e: self._on_close())
        refresh_btn = ft.ElevatedButton(
            "Refresh",
            icon="refresh",
            on_click=lambda e: self._load_saved_cases(),
        )

        button_row = ft.Row([refresh_btn, close_btn])

        self.controls = [
            title,
            ft.Divider(),
            self.search_field,
            ft.Text("Search Results:", weight="bold"),
            self.results_table,
            button_row,
        ]

        # Load cases on init
        self._load_saved_cases()

    def _load_saved_cases(self):
        """Load all saved cases from logs directory."""
        self.saved_cases.clear()
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        
        if not logs_dir.exists():
            return

        try:
            for json_file in logs_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        case_data = json.load(f)
                        if "id" in case_data:
                            self.saved_cases.append(case_data)
                except (json.JSONDecodeError, IOError):
                    pass
        except Exception as e:
            print(f"Error loading cases: {e}")

        # Re-filter based on current search
        self._filter_cases()

    def _on_search_change(self, e):
        """Handle search field changes."""
        self._filter_cases()

    def _filter_cases(self):
        """Filter cases based on search query."""
        query = self.search_field.value.lower() if self.search_field.value else ""
        self.filtered_cases = []

        for case in self.saved_cases:
            # Check if query matches case name
            if query in case.get("name", "").lower():
                self.filtered_cases.append(case)
                continue

            # Check if query matches any entity in the case
            for field_label, values in case.get("fields", {}).items():
                for value in values:
                    if query in value.lower():
                        self.filtered_cases.append(case)
                        break
                if case in self.filtered_cases:
                    break

        # Update table
        self._update_results_table()

    def _update_results_table(self):
        """Update the results table with filtered cases."""
        self.results_table.rows.clear()

        for case in self.filtered_cases:
            case_name = case.get("name", "Unknown")
            created_at = case.get("created_at", "Unknown")
            
            # Format created date
            try:
                dt = datetime.fromisoformat(created_at)
                created_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                created_str = created_at[:10] if created_at else "Unknown"

            # Get entity count
            fields = case.get("fields", {})
            entity_count = sum(len(v) for v in fields.values())
            entities_str = f"{entity_count} entities"

            # Load button
            load_btn = ft.TextButton(
                text="Load",
                on_click=lambda e, c=case: self._on_load_case(c),
            )

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(case_name)),
                    ft.DataCell(ft.Text(created_str)),
                    ft.DataCell(ft.Text(entities_str)),
                    ft.DataCell(load_btn),
                ]
            )
            self.results_table.rows.append(row)

        self.update()

    def _on_load_case(self, case_data: Dict):
        """Load a case into the state."""
        if not self.state:
            return

        try:
            # Import case from dict
            case_id = self.state.import_case_from_dict(case_data)
            self.state.select_case(case_id)

            # Callback to notify parent
            if self.on_load_case:
                self.on_load_case(case_id)
        except Exception as e:
            print(f"Error loading case: {e}")

    def _on_close(self):
        """Close dialog."""
        if self.on_close:
            self.on_close()

