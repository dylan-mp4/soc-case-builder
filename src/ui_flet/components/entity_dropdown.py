"""
Entity dropdown component for selecting entity types.
"""

import flet as ft
from typing import Callable, List, Optional


class EntityDropdown(ft.Dropdown):
    """
    Dropdown for selecting entity types (IP, Domain, Hash, URL, etc.)
    """

    def __init__(
        self,
        entities: List[str],
        on_change: Optional[Callable] = None,
        value: str = "",
    ):
        """
        Initialize entity dropdown.

        Args:
            entities: List of available entity types
            on_change: Callback when selection changes
            value: Initial selected value
        """
        # Create dropdown options
        options = [ft.dropdown.Option(entity) for entity in entities]

        super().__init__(
            options=options,
            value=value or (entities[0] if entities else ""),
            label="Select Entity Type",
            width=200,
        )
        
        # Set on_change after initialization
        if on_change:
            self.on_change = on_change

    def get_selected(self) -> str:
        """Get currently selected entity."""
        return self.value

    def set_selected(self, entity: str):
        """Set selected entity."""
        self.value = entity
        self.update()
