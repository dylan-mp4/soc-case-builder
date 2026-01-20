"""
Settings Page - Interface for managing application settings.
"""

import flet as ft
from typing import Callable, Optional
from src.ui_flet.state import AppState
from src.ui_flet.theme import PRIMARY_TEXT, SECONDARY_BG


class SettingsPage(ft.Column):
    """
    Settings interface with tabs for General, API Keys, and Entity Settings.
    """

    def __init__(
        self,
        state: AppState,
        on_save: Optional[Callable] = None,
    ):
        """
        Initialize settings page.

        Args:
            state: Centralized application state
            on_save: Callback when settings are saved
        """
        super().__init__(expand=True, spacing=12)

        self.state = state
        self.on_save = on_save

        # ==================== General Tab ====================

        self.user_name_field = ft.TextField(
            label="User Name",
            value=state.get_setting("user_name", ""),
            expand=True,
        )

        self.org_name_field = ft.TextField(
            label="Organization Name",
            value=state.get_setting("org_name", ""),
            expand=True,
        )

        clients_str = ", ".join(state.get_setting("clients", []))
        self.clients_field = ft.TextField(
            label="Clients (comma-separated)",
            value=clients_str,
            multiline=True,
            min_lines=6,
            expand=True,
        )

        general_tab = ft.Column(
            controls=[
                ft.Text("General Settings", weight="bold", size=14),
                self.user_name_field,
                self.org_name_field,
                self.clients_field,
            ],
            spacing=12,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # ==================== API Keys Tab ====================

        self.abuse_api_field = ft.TextField(
            label="AbuseIPDB API Key",
            value=state.get_setting("abuse_api_key", ""),
            password=True,
            expand=True,
        )

        self.vt_api_field = ft.TextField(
            label="VirusTotal API Key",
            value=state.get_setting("vt_api_key", ""),
            password=True,
            expand=True,
        )

        self.urlscan_api_field = ft.TextField(
            label="URLScan API Key",
            value=state.get_setting("urlscan_api_key", ""),
            password=True,
            expand=True,
        )

        self.urlscan_wait_field = ft.TextField(
            label="URLScan Wait Time (seconds)",
            value=str(state.get_setting("urlscan_wait_time", 0)),
            input_filter="0123456789",
            expand=True,
        )

        api_tab = ft.Column(
            controls=[
                ft.Text("API Settings", weight="bold", size=14),
                self.abuse_api_field,
                self.vt_api_field,
                self.urlscan_api_field,
                self.urlscan_wait_field,
            ],
            spacing=12,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # ==================== Entity Settings Tab ====================

        entities_str = "\n".join(state.get_setting("entities", []))
        self.entities_field = ft.TextField(
            label="Custom Entities (one per line)",
            value=entities_str,
            multiline=True,
            min_lines=10,
            expand=True,
        )

        entities_tab = ft.Column(
            controls=[
                ft.Text("Entity Settings", weight="bold", size=14),
                self.entities_field,
            ],
            spacing=12,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # ==================== Main Tabs Container ====================

        tab_bar = ft.TabBar(
            tabs=[
                ft.Tab("General"),
                ft.Tab("API Keys"),
                ft.Tab("Entities"),
            ],
            on_click=self._on_tab_click,
        )

        self._tab_contents = [general_tab, api_tab, entities_tab]
        self.tab_content = ft.Container(content=self._tab_contents[0], expand=True)

        tabs_content = ft.Column(
            controls=[tab_bar, self.tab_content],
            spacing=8,
            expand=True,
        )

        self.tabs = ft.Tabs(
            content=tabs_content,
            length=3,
            expand=True,
        )

        # ==================== Action Buttons ====================

        save_btn = ft.ElevatedButton(
            "Save Settings",
            icon="save",
            on_click=self._on_save,
        )

        cancel_btn = ft.TextButton(
            "Cancel",
            on_click=self._on_cancel,
        )

        button_row = ft.Row(
            controls=[save_btn, cancel_btn],
            spacing=12,
        )

        # ==================== Layout Assembly ====================

        self.controls = [
            ft.Text("Settings", size=18, weight="bold"),
            ft.Divider(),
            self.tabs,
            button_row,
        ]

    def _on_tab_click(self, e):
        """Handle tab selection and swap visible content."""
        try:
            idx = int(e.data) if e.data is not None else 0
        except (TypeError, ValueError):
            idx = 0
        idx = max(0, min(idx, len(self._tab_contents) - 1))
        self.tab_content.content = self._tab_contents[idx]
        self.tab_content.update()

    def _on_save(self, e):
        """Save all settings."""
        try:
            # Parse clients
            clients = [
                c.strip() for c in self.clients_field.value.split(",") if c.strip()
            ]

            # Parse entities
            entities = [
                c.strip() for c in self.entities_field.value.split("\n") if c.strip()
            ]

            # Parse URLScan wait time
            urlscan_wait = int(self.urlscan_wait_field.value or "0")

            # Update settings
            self.state.update_settings(
                {
                    "user_name": self.user_name_field.value,
                    "org_name": self.org_name_field.value,
                    "clients": clients,
                    "abuse_api_key": self.abuse_api_field.value,
                    "vt_api_key": self.vt_api_field.value,
                    "urlscan_api_key": self.urlscan_api_field.value,
                    "urlscan_wait_time": urlscan_wait,
                    "entities": entities,
                }
            )

            print("Settings saved successfully")
            if self.on_save:
                self.on_save()

        except Exception as e:
            print(f"Error saving settings: {e}")

    def _on_cancel(self, e):
        """Cancel and close settings."""
        print("Settings cancelled")
