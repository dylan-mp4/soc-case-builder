"""
Settings tabs component for tabbed settings interface.
"""

import flet as ft
from typing import Callable, Dict, List, Optional


class SettingsTabs(ft.Tabs):
    """
    Tabbed settings interface with tabs for General, API Keys, Entity Settings, etc.
    """

    def __init__(self, on_save: Optional[Callable] = None):
        """
        Initialize settings tabs.

        Args:
            on_save: Callback when settings are saved
        """
        self.on_save = on_save

        # Create tabs
        general_tab = self._create_general_tab()
        api_tab = self._create_api_tab()
        entities_tab = self._create_entities_tab()

        super().__init__(
            [
                ft.Tab("General", general_tab),
                ft.Tab("API Keys", api_tab),
                ft.Tab("Entity Settings", entities_tab),
            ]
        )

    def _create_general_tab(self) -> ft.Control:
        """Create General settings tab."""
        return ft.Column(
            controls=[
                ft.TextField(label="User Name", expand=True),
                ft.TextField(label="Organization Name", expand=True),
                ft.TextField(
                    label="Clients (comma-separated)",
                    multiline=True,
                    min_lines=4,
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _create_api_tab(self) -> ft.Control:
        """Create API Keys settings tab."""
        return ft.Column(
            controls=[
                ft.TextField(label="AbuseIPDB API Key", password=True, expand=True),
                ft.TextField(label="VirusTotal API Key", password=True, expand=True),
                ft.TextField(label="URLScan API Key", password=True, expand=True),
                ft.TextField(
                    label="URLScan Wait Time (seconds)",
                    value="0",
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _create_entities_tab(self) -> ft.Control:
        """Create Entity Settings tab."""
        return ft.Column(
            controls=[
                ft.TextField(
                    label="Custom Entities (one per line)",
                    multiline=True,
                    min_lines=8,
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def get_settings(self) -> Dict[str, str]:
        """Extract settings from all tabs."""
        settings = {}
        # This would be implemented to extract values from all fields
        return settings

    def set_settings(self, settings: Dict[str, str]):
        """Populate tabs with settings values."""
        # This would be implemented to populate fields with values
        pass
