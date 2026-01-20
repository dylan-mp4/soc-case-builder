"""
Escalation Note Dialog - Create escalation notes.
"""

import flet as ft
from typing import Callable, Optional


class EscalationNoteDialog(ft.Column):
    """Dialog for creating escalation notes."""

    def __init__(self, on_close: Optional[Callable] = None):
        """
        Initialize escalation note dialog.

        Args:
            on_close: Callback when dialog is closed
        """
        super().__init__(spacing=12)

        self.on_close = on_close

        title = ft.Text("Escalation Note", size=16, weight="bold")

        case_id_field = ft.TextField(label="Case ID", read_only=True)
        escalation_reason_field = ft.TextField(
            label="Escalation Reason",
            multiline=True,
            min_lines=4,
        )
        recipient_field = ft.TextField(label="Escalate To")

        submit_btn = ft.ElevatedButton(
            "Send Escalation",
            icon="send",
            on_click=self._on_submit,
        )
        close_btn = ft.TextButton("Cancel", on_click=lambda e: self._on_close())

        self.controls = [
            title,
            ft.Divider(),
            case_id_field,
            escalation_reason_field,
            recipient_field,
            ft.Row(controls=[submit_btn, close_btn]),
        ]

    def _on_submit(self, e):
        """Submit escalation."""
        print("Escalation sent")

    def _on_close(self):
        """Close dialog."""
        if self.on_close:
            self.on_close()
