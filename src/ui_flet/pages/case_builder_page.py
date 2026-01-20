"""
Case Builder Page - Main interface for creating and managing cases.
"""

import flet as ft
import threading
import json
from typing import Callable, Dict, List, Optional
from datetime import datetime
from pathlib import Path
from src.ui_flet.state import AppState
from src.ui_flet.theme import PRIMARY_ACCENT, PRIMARY_BG, PRIMARY_TEXT, SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR
from src.ui_flet.components.case_field_row import CaseFieldRow
from src.ui_flet.components.entity_dropdown import EntityDropdown
from src.utils import api_requests
from src.utils import entity_store


class CaseBuilderPage(ft.Column):
    """
    Main case builder interface with native tabs for case management.
    Supports dynamic field addition/removal, entity enrichment, and case compilation.
    """

    def __init__(
        self,
        state: AppState,
        on_search_cases: Optional[Callable] = None,
        on_query_finder: Optional[Callable] = None,
    ):
        """
        Initialize case builder page.

        Args:
            state: Centralized application state
            on_search_cases: Callback for search cases
            on_query_finder: Callback for query finder
        """
        super().__init__(expand=True, spacing=12)

        self.state = state
        self.on_search_cases = on_search_cases
        self.on_query_finder = on_query_finder
        self.current_field_rows: Dict[str, CaseFieldRow] = {}
        self.enrichment_threads: Dict[str, threading.Thread] = {}  # Track enrichment threads

        # ==================== Tab Management ====================

        # Create initial case
        case_id = self.state.create_case("Case 1")
        self.state.select_case(case_id)

        # Simplified: Start with single case, tabs can be added later
        case_header = ft.Row(
            controls=[
                ft.Text("Case 1", size=16, weight="bold"),
                ft.Container(expand=True),
            ]
        )

        # ==================== Field Management Controls ====================

        self.entity_dropdown = EntityDropdown(
            entities=state.get_setting("entities", []),
        )

        # Add field button
        add_field_btn = ft.ElevatedButton(
            "Add Field",
            icon="add",
            on_click=self._on_add_field,
        )

        # Route selection (Close / Escalate)
        self.close_radio = ft.Radio(value="close", label="Close Case")
        self.escalate_radio = ft.Radio(value="escalate", label="Escalate Case")

        self.route_group = ft.RadioGroup(
            content=ft.Column(
                controls=[self.close_radio, self.escalate_radio],
            )
        )
        self.route_group.value = "close"

        # Reason text field (for close/escalate)
        self.reason_field = ft.TextField(
            label="Reason",
            multiline=True,
            min_lines=3,
            expand=True,
        )

        route_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Case Route", weight="bold"),
                        self.route_group,
                        self.reason_field,
                    ]
                ),
                padding=12,
            ),
            margin=12,
        )

        # Output display
        self.output_text = ft.TextField(
            label="Case Output",
            multiline=True,
            min_lines=8,
            expand=True,
            read_only=True,
        )

        # Compile and Save buttons
        compile_btn = ft.ElevatedButton(
            "Compile Case",
            icon="edit_note",
            on_click=self._on_compile_case,
        )

        save_btn = ft.ElevatedButton(
            "Save Case",
            icon="save",
            on_click=self._on_save_case,
        )

        action_buttons = ft.Row(
            controls=[compile_btn, save_btn],
            spacing=12,
        )

        # ==================== Layout Assembly ====================

        fields_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                self.entity_dropdown,
                                add_field_btn,
                            ]
                        ),
                        ft.Divider(),
                        ft.Column(
                            controls=[],  # Populated dynamically
                            spacing=8,
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=12,
            ),
            margin=12,
        )

        self.fields_column = fields_section.content.content.controls[2]

        # Main scrollable container
        main_scroll = ft.Column(
            controls=[
                fields_section,
                route_section,
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Case Output", weight="bold"),
                                self.output_text,
                                action_buttons,
                            ]
                        ),
                        padding=12,
                    ),
                    margin=12,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # Add all to main column
        self.controls = [
            case_header,
            main_scroll,
        ]

    # ==================== Case Tab Management ====================

    def _on_add_case(self, e):
        """Add a new case (simplified without tabs for now)."""
        case_num = len(self.state.get_all_cases()) + 1
        case_id = self.state.create_case(f"Case {case_num}")
        self.state.select_case(case_id)
        self._refresh_fields()
        self.update()

    # ==================== Field Management ====================

    def _on_add_field(self, e):
        """Add a new field row."""
        entity_type = self.entity_dropdown.get_selected()
        if not entity_type:
            return

        case_id = self.state.current_case_id
        if not case_id:
            return

        self.state.add_field_to_case(case_id, entity_type)
        self._refresh_fields()

    def _on_add_field_multi(self, field_label: str):
        """Add another field of the same type."""
        case_id = self.state.current_case_id
        if not case_id:
            return

        self.state.add_field_to_case(case_id, field_label)
        self._refresh_fields()

    def _on_remove_field(self, field_label: str, index: int):
        """Remove a field."""
        case_id = self.state.current_case_id
        if not case_id:
            return

        # Find and remove the last instance of this field
        case = self.state.get_case(case_id)
        if case and field_label in case["fields"]:
            self.state.remove_field_from_case(case_id, field_label, index)
            self._refresh_fields()

    def _on_field_value_change(self, field_label: str, index: int, value: str):
        """Handle field value changes."""
        case_id = self.state.current_case_id
        if not case_id:
            return

        self.state.update_field_in_case(case_id, field_label, index, value)

    def _refresh_fields(self):
        """Refresh field display from state."""
        case_id = self.state.current_case_id
        if not case_id:
            return

        case = self.state.get_case(case_id)
        if not case:
            return

        self.fields_column.controls.clear()

        for field_label, values in case.get("fields", {}).items():
            for idx, value in enumerate(values):
                field_row = CaseFieldRow(
                    field_label=field_label,
                    field_value=value,
                    index=idx,
                    on_query=self._on_query,
                    on_search=self._on_search,
                    on_add=self._on_add_field_multi,
                    on_remove=self._on_remove_field,
                    on_value_change=self._on_field_value_change,
                )
                self.fields_column.controls.append(field_row)

        self.update()

    # ==================== Case Actions ====================

    def _on_query(self, field_label: str, value: str):
        """Query entity with enrichment via background thread."""
        if not value or not value.strip():
            return

        case_id = self.state.current_case_id
        if not case_id:
            return

        # Show pending status
        self._show_snack_bar(f"Enriching {field_label}...", duration=2000)
        
        # Start enrichment in background thread
        thread_id = f"{case_id}_{field_label}_{id(value)}"
        thread = threading.Thread(
            target=self._enrich_entity_background,
            args=(field_label, value, thread_id),
            daemon=True,
        )
        thread.start()
        self.enrichment_threads[thread_id] = thread

    def _enrich_entity_background(self, field_label: str, value: str, thread_id: str):
        """Background thread for entity enrichment."""
        try:
            enrichment_data = self._get_enrichment_for_entity(field_label, value)
            if enrichment_data:
                # Store in entity cache using functional API
                entity_store.upsert_entity(field_label, value, enrichment_data)
                # Show success message in main thread
                self._show_snack_bar(f"✓ {field_label} enriched", duration=2000)
            else:
                self._show_snack_bar(f"⚠ No enrichment found for {field_label}", duration=2000)
        except Exception as e:
            self._show_snack_bar(f"✗ Enrichment error: {str(e)}", duration=3000)
        finally:
            # Clean up thread reference
            self.enrichment_threads.pop(thread_id, None)

    def _get_enrichment_for_entity(self, field_label: str, value: str) -> Optional[str]:
        """Get enrichment data for an entity based on its type."""
        settings = self.state.settings
        
        # Normalize field label to entity type
        entity_type = field_label.lower()
        
        if "ip" in entity_type:
            api_key = settings.get("abuseipdb_api_key", "")
            if not api_key:
                return None
            return api_requests.get_abuse_info(value, api_key)
        
        elif "domain" in entity_type:
            return api_requests.get_domain_info(value)
        
        elif "hash" in entity_type or "md5" in entity_type or "sha" in entity_type:
            api_key = settings.get("virustotal_api_key", "")
            if not api_key:
                return None
            return api_requests.get_hash_info(value, api_key)
        
        elif "url" in entity_type:
            api_key = settings.get("urlscan_api_key", "")
            if not api_key:
                return None
            return api_requests.get_url_info(value, api_key)
        
        return None

    def _show_snack_bar(self, message: str, duration: int = 2000):
        """Show a temporary notification message."""
        if hasattr(self, 'page') and self.page:
            snack = ft.SnackBar(ft.Text(message))
            snack.open = True
            self.page.overlay.append(snack)
            self.page.update()

    def _on_search(self, field_label: str, value: str):
        """Search for cases with this entity."""
        if self.on_search_cases:
            self.on_search_cases(field_label, value)

    def _on_compile_case(self, e):
        """Compile case to formatted output."""
        case_id = self.state.current_case_id
        if not case_id:
            return

        case = self.state.get_case(case_id)
        if not case:
            return

        # Format case output
        output_lines = [
            f"Case: {case['name']}",
            f"Created: {case['created_at']}",
            "",
            "Fields:",
        ]

        for field_label, values in case.get("fields", {}).items():
            for value in values:
                output_lines.append(f"  {field_label}: {value}")

        if case.get("close_reason"):
            output_lines.append(f"\nClosed: {case['close_reason']}")
        elif case.get("escalation_reason"):
            output_lines.append(f"\nEscalated: {case['escalation_reason']}")

        self.output_text.value = "\n".join(output_lines)
        self.update()

    def _on_save_case(self, e):
        """Save case to file."""
        case_id = self.state.current_case_id
        if not case_id:
            return

        # Update case route info
        route_type = self.route_group.value
        reason = self.reason_field.value
        self.state.set_case_route(case_id, route_type, reason)

        # Export to JSON
        case_json = self.state.export_case_to_json(case_id)
        if case_json:
            # Save to logs directory
            logs_dir = Path(__file__).parent.parent.parent / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)

            case_name = self.state.get_case(case_id)["name"]
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = logs_dir / f"{case_name}_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(case_json)

            # Show success message
            self._show_snack_bar(f"✓ Case saved to {filename.name}")
            print(f"Case saved to {filename}")
