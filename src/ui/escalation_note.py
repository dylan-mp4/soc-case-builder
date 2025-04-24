from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import QApplication
from weakref import ref

class EscalationNoteDialog(QDialog):
    def __init__(self, parent, assigned_analyst, case_link, client, escalation_summary):
        super().__init__(parent)
        self.setWindowTitle("Escalation Note")
        self.setFixedWidth(800)
        layout = QVBoxLayout(self)

        # Form layout for the fields
        form_layout = QFormLayout()

        # Assigned Analyst
        self.assigned_analyst = QLineEdit(assigned_analyst)
        form_layout.addRow("Assigned Analyst:", self.assigned_analyst)

        # Reviewed By
        self.reviewed_by = QLineEdit()
        form_layout.addRow("Reviewed By:", self.reviewed_by)

        # Case Link
        self.case_link = QLineEdit(case_link)
        form_layout.addRow("Case Link:", self.case_link)

        # Date
        current_date = QDate.currentDate().toString("dd/MM/yyyy")
        self.date_field = QLineEdit(current_date)
        self.date_field.setReadOnly(True)
        form_layout.addRow("Date:", self.date_field)

        # Environment
        self.environment = QLineEdit(client)
        form_layout.addRow("Environment:", self.environment)

        # Severity
        self.severity = QComboBox()
        self.severity.addItems(["Informational", "Low", "Medium", "High", "Critical"])
        form_layout.addRow("Severity:", self.severity)

        # Escalation Summary
        self.escalation_summary = QLineEdit(escalation_summary)
        form_layout.addRow("Escalation Summary:", self.escalation_summary)

        layout.addLayout(form_layout)

        # Add buttons
        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_escalation_note_data(self):
        return {
            "assigned_analyst": self.assigned_analyst.text(),
            "reviewed_by": self.reviewed_by.text(),
            "case_link": self.case_link.text(),
            "date": self.date_field.text(),
            "environment": self.environment.text(),
            "severity": self.severity.currentText(),
            "escalation_summary": self.escalation_summary.text(),
        }

    def copy_to_clipboard(self):
        # Compile the escalation note data
        escalation_note_data = self.get_escalation_note_data()
        escalation_note = (
            f"Assigned Analyst: {escalation_note_data['assigned_analyst']}\n"
            f"Reviewed By: {escalation_note_data['reviewed_by']}\n"
            f"Case Link: {escalation_note_data['case_link']}\n"
            f"Date: {escalation_note_data['date']}\n"
            f"Environment: {escalation_note_data['environment']}\n"
            f"Severity: {escalation_note_data['severity']}\n"
            f"Escalation Summary:{escalation_note_data['escalation_summary']}"
        )

        # Access the system clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(escalation_note)

        # Change the button text to "Copied"
        sender = self.sender()  # Get the button that triggered this method
        if sender:
            original_text = sender.text()  # Save the original text
            sender.setText("Copied!")
            sender.repaint()  # Force the button to update its appearance
            sender_ref = ref(sender)
            # Restore the original text after a short delay
            QTimer.singleShot(1000, lambda: sender_ref() and sender_ref().setText(original_text))