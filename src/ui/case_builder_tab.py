import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QScrollArea, QLineEdit, QPushButton, 
    QRadioButton, QButtonGroup, QComboBox, QHBoxLayout, QVBoxLayout, QTabWidget
)
import csv
import json
from utils.api_requests import get_abuse_info, get_domain_info, get_hash_info, get_url_info
from utils.spell_check import SpellTextEdit
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QMessageBox
from ui.escalation_note import EscalationNoteDialog
from ui.pop_out_text_edit import PopOutTextBox

class PlainTextLineEdit(QLineEdit):
    def insertFromMimeData(self, source):
        plain_text = source.text()
        self.insert(plain_text)

class PlainTextTextEdit(SpellTextEdit):
    def insertFromMimeData(self, source):
        plain_text = source.text()
        self.insertPlainText(plain_text)

class CaseBuilderTab(QWidget):
    def __init__(self, settings_tab, initial_fields=None):
        super().__init__()
        self.settings_tab = settings_tab
        self.case_builder_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.common_fields_layout = QFormLayout()
        self.entity_positions = {}
        self.custom_entities = []

        if initial_fields:
            for field in initial_fields:
                self.add_field(field["label"], self.common_fields_layout)
                field_position = self.entity_positions.get(field["label"])
                if field_position is not None:
                    field_widget = self.common_fields_layout.itemAt(field_position, QFormLayout.ItemRole.FieldRole).layout().itemAt(0).widget()
                    if field_widget:
                        field_widget.setText(field["value"])
        else:
            self.generate_default_fields()

        self.scroll_layout.addLayout(self.common_fields_layout)

        # Add dropdown and button for premade entities
        self.entity_dropdown_layout = QHBoxLayout()
        self.entity_dropdown = QComboBox()
        self.load_entities()
        self.add_entity_button = QPushButton("Add Entity")
        self.add_entity_button.clicked.connect(self.add_selected_entity)
        self.entity_dropdown_layout.addWidget(self.entity_dropdown)
        self.entity_dropdown_layout.addWidget(self.add_entity_button)
        self.scroll_layout.addLayout(self.entity_dropdown_layout)

        self.add_custom_entity_button = QPushButton("Add Custom Entity")
        self.add_custom_entity_button.clicked.connect(self.add_custom_entity)
        self.common_fields_layout.addRow(self.add_custom_entity_button)

        self.case_builder_layout.addWidget(self.scroll_area)

        self.route_layout = QHBoxLayout()
        self.close_case_rb = QRadioButton("Close Case")
        self.escalation_rb = QRadioButton("Escalation")
        self.close_case_rb.setChecked(True)
        self.route_group = QButtonGroup()
        self.route_group.addButton(self.close_case_rb)
        self.route_group.addButton(self.escalation_rb)
        self.route_layout.addWidget(self.close_case_rb)
        self.route_layout.addWidget(self.escalation_rb)
        self.case_builder_layout.addLayout(self.route_layout)

        self.additional_info_layout = QVBoxLayout()
        self.escalation_layout = QFormLayout()
        self.close_layout = QFormLayout()

        self.client_combo = QComboBox()
        try:
            with open("clients.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row: self.client_combo.addItem(row[0])
        except FileNotFoundError:
            pass

        self.crux_field = PlainTextLineEdit()
        self.escalation_info = PopOutTextBox()
        self.sign_off_user = PlainTextLineEdit()
        self.sign_off_org = PlainTextLineEdit()

        self.escalation_layout.addRow("Client:", self.client_combo)
        self.escalation_layout.addRow("Crux:", self.crux_field)
        self.escalation_layout.addRow("Information:", self.escalation_info)
        # deprecated sign off fields
        # self.escalation_layout.addRow("Sign off (User):", self.sign_off_user)
        # self.escalation_layout.addRow("Sign off (Org):", self.sign_off_org)

        self.close_reason = PopOutTextBox()
        self.close_info = PopOutTextBox()
        self.close_layout.addRow("Reason:", self.close_reason)
        self.close_layout.addRow("Information:", self.close_info)

        self.additional_info_layout.addLayout(self.escalation_layout)
        self.additional_info_layout.addLayout(self.close_layout)
        self.case_builder_layout.addLayout(self.additional_info_layout)

        self.submit_button = QPushButton("Compile Case info")
        self.submit_button.clicked.connect(self.compile_case)
        self.case_builder_layout.addWidget(self.submit_button)

        self.clear_button = QPushButton("Clear All Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        self.case_builder_layout.addWidget(self.clear_button)

        self.escalation_note = QPushButton("Create Escalation Note")
        self.escalation_note.clicked.connect(self.escalationnote)
        self.case_builder_layout.addWidget(self.escalation_note)
        self.escalation_note.setVisible(False)  # Initially hidden
        # Update visibility of the button when toggling fields
        self.escalation_rb.toggled.connect(lambda: self.escalation_note.setVisible(self.escalation_rb.isChecked()))

        self.output_text = PlainTextTextEdit()
        self.case_builder_layout.addWidget(self.output_text)


        
        # Show relevant fields by default (close case)
        self.toggle_fields()

        self.close_case_rb.toggled.connect(self.toggle_fields)
        self.escalation_rb.toggled.connect(self.toggle_fields)

        self.setLayout(self.case_builder_layout)

    def load_entities(self):
        try:
            with open("entities.json", "r") as file:
                entities = json.load(file)
                self.entity_dropdown.addItems(entities)
        except FileNotFoundError:
            self.entity_dropdown.addItems([
                "Case Link", "Username", "Role", "Location", "Host", "IP", "Domain", "Hash", "URL"
            ])

    def toggle_fields(self):
        is_escalation = self.escalation_rb.isChecked()
        for i in range(self.escalation_layout.rowCount()):
            widget_label = self.escalation_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            widget_field = self.escalation_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if widget_label and widget_field:
                widget_label.widget().setVisible(is_escalation)
                widget_field.widget().setVisible(is_escalation)

        for i in range(self.close_layout.rowCount()):
            widget_label = self.close_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            widget_field = self.close_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if widget_label and widget_field:
                widget_label.widget().setVisible(not is_escalation)
                widget_field.widget().setVisible(not is_escalation)

    def add_field(self, label, layout):
        field_layout = QHBoxLayout()
        line_edit = PlainTextLineEdit()
        query_button = QPushButton("S")
        query_button.setMaximumWidth(20)
        query_button.clicked.connect(lambda: self.open_query_finder(label, line_edit.text()))
        add_button = QPushButton("+")
        add_button.setMaximumWidth(20)
        add_button.clicked.connect(lambda: self.add_field(label, layout))
        remove_button = QPushButton("x")
        remove_button.setMaximumWidth(20)
        remove_button.clicked.connect(lambda: self.remove_field(label, layout, field_layout))
        field_layout.addWidget(line_edit)
        field_layout.addWidget(query_button)
        field_layout.addWidget(add_button)
        field_layout.addWidget(remove_button)

        if label not in self.entity_positions:
            self.entity_positions[label] = layout.rowCount()
        else:
            self.entity_positions[label] += 1

        layout.insertRow(self.entity_positions[label], label, field_layout)
        self.update_entity_positions()

    def remove_field(self, label, layout, field_layout):
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if field_item and field_item.layout() == field_layout:
                layout.removeRow(i)
                break
        self.update_entity_positions()

    def generate_default_fields(self):
        self.add_field("Case Link:", self.common_fields_layout)
        self.add_field("Username:", self.common_fields_layout)
        self.add_field("Role:", self.common_fields_layout)
        self.add_field("Location:", self.common_fields_layout)
        self.add_field("Host:", self.common_fields_layout)
        self.add_field("IP:", self.common_fields_layout)
        self.add_field("Domain:", self.common_fields_layout)
        self.add_field("Hash:", self.common_fields_layout)
        self.add_field("URL:", self.common_fields_layout)
    
    def update_entity_positions(self):
        for i in range(self.common_fields_layout.rowCount()):
            label_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label_item:
                label = label_item.widget().text()
                self.entity_positions[label] = i

    def add_custom_entity(self):
        field_layout = QHBoxLayout()
        name_edit = PlainTextLineEdit()
        value_edit = PlainTextLineEdit()
        add_button = QPushButton("+")
        add_button.setMaximumWidth(20)
        add_button.clicked.connect(lambda: self.add_custom_entity())
        field_layout.addWidget(name_edit)
        field_layout.addWidget(value_edit)
        field_layout.addWidget(add_button)
        self.common_fields_layout.insertRow(self.common_fields_layout.rowCount() - 1, "", field_layout)
        self.custom_entities.append((name_edit, value_edit, add_button))

    def add_selected_entity(self):
        selected_entity = self.entity_dropdown.currentText()
        self.add_field(f"{selected_entity}:", self.common_fields_layout)

    def escalationnote(self):
    # Get the required data for the dialog
        assigned_analyst = self.settings_tab.settings_sign_off_user.text()
        case_link = self.common_fields_layout.itemAt(0, QFormLayout.ItemRole.FieldRole).layout().itemAt(0).widget().text()
        client = self.client_combo.currentText()
        parent_widget = self.parentWidget()
        if parent_widget and hasattr(parent_widget, 'parentWidget'):
            tab_widget = parent_widget.parentWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_index = tab_widget.indexOf(self)
                tab_name = tab_widget.tabText(tab_index)
            else:
                tab_name = ""
        else:
            tab_name = ""
        if re.match(r"(?i)^case \d+$", tab_name):  # Case-insensitive match
            escalation_summary = ""  # Set to blank
        else:
            escalation_summary = tab_name  # Otherwise, use the tab name

        # Create and show the dialog
        dialog = EscalationNoteDialog(self, assigned_analyst, case_link, client, escalation_summary)
        if dialog.exec():
            # Retrieve the data from the dialog
            escalation_note_data = dialog.get_escalation_note_data()
            escalation_note = (
                f"Assigned Analyst: {escalation_note_data['assigned_analyst']}\n"
                f"Reviewed By: {escalation_note_data['reviewed_by']}\n"
                f"Case Link: {escalation_note_data['case_link']}\n"
                f"Date: {escalation_note_data['date']}\n"
                f"Environment: {escalation_note_data['environment']}\n"
                f"Severity: {escalation_note_data['severity']}\n"
                f"Escalation Summary:{escalation_note_data['escalation_summary']}"
            )
            QMessageBox.information(self, "Escalation Note", escalation_note)
            
    def open_query_finder(self, label, value):
        from ui.query_finder_dialog import QueryFinderDialog
        # Extract entity type from label (e.g., "IP:" -> "IP")
        entity_type = label.rstrip(":")
        dialog = QueryFinderDialog(entity_type, value, self)
        dialog.exec()
    def clear_fields(self):
        # Show a confirmation dialog before clearing fields
        confirmation = QMessageBox.question(
            self, "Confirm Clear", "Are you sure you want to clear all fields?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.No:
            return
    
        # Remove all dynamically added fields
        for i in reversed(range(self.common_fields_layout.rowCount())):
            label_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                label_widget = label_item.widget()
                field_layout = field_item.layout()
                if field_layout:
                    for j in range(field_layout.count()):
                        widget = field_layout.itemAt(j).widget()
                        if isinstance(widget, QLineEdit):
                            widget.clear()
                if isinstance(label_widget, QLineEdit):
                    label_widget.clear()
                self.common_fields_layout.removeRow(i)

        # Clear custom entities
        for name_edit, value_edit, add_button in self.custom_entities:
            name_edit.deleteLater()
            value_edit.deleteLater()
            add_button.deleteLater()
        self.custom_entities.clear()

        # Re-add the default fields
        self.entity_positions.clear()
        self.generate_default_fields()
        self.common_fields_layout.addRow(self.add_custom_entity_button)

        self.client_combo.setCurrentIndex(0)
        self.crux_field.clear()
        self.escalation_info.clear()
        self.sign_off_user.clear()
        self.sign_off_org.clear()
        self.close_reason.clear()
        self.close_info.clear()
        self.output_text.clear()

        # Update the layout to remove any gaps
        self.scroll_content.adjustSize()
        self.scroll_area.setWidget(self.scroll_content)

    def compile_case(self):
        final_text = []
        other_fields_text = []
        custom_entities_text = []

        # Append client information at the top
        if self.escalation_rb.isChecked():
            client = self.client_combo.currentText()
            if client:
                final_text.append(f"Dear {client},\n")

        # Append case link at the top
        for i in range(self.common_fields_layout.rowCount()):
            label_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                label = label_item.widget().text()
        # Append reason and information sections
        if self.close_case_rb.isChecked():
            reason = self.close_reason.toPlainText()
            if reason:
                final_text.append(f"{reason}\n")
            info = self.close_info.toPlainText()
            if info:
                final_text.append(f"{info}\n")
        else:
            crux = self.crux_field.text()
            if crux:
                final_text.append(f"{crux}\n")
            info = self.escalation_info.toPlainText()
            if info:
                final_text.append(f"{info}\n")

        # Append other fields
        for i in range(self.common_fields_layout.rowCount()):
            label_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                label = label_item.widget().text()
                if label != "Case Link:":
                    field_layout = field_item.layout()
                    if field_layout:
                        for j in range(field_layout.count()):
                            widget = field_layout.itemAt(j).widget()
                            if isinstance(widget, QLineEdit):
                                text = widget.text()
                                if text:  # Only include non-empty fields
                                    if label == "IP:" and self.settings_tab.settings_abuse_api_key.text():
                                        abuse_info = get_abuse_info(text, self.settings_tab.settings_abuse_api_key.text())
                                        other_fields_text.append(f"\n{label} {text} - {abuse_info}")
                                    elif label == "Domain:":
                                        domain_info = get_domain_info(text)
                                        other_fields_text.append(f"\n{label} {text} - {domain_info}")
                                    elif label == "Hash:" and self.settings_tab.settings_vt_api_key.text():
                                        hash_info = get_hash_info(text, self.settings_tab.settings_vt_api_key.text())
                                        other_fields_text.append(f"\n{label} {text} - {hash_info}")
                                    elif label == "URL:" and self.settings_tab.settings_urlscan_api_key.text():
                                        urlinfo = get_url_info(text, self.settings_tab.settings_urlscan_api_key.text())
                                        other_fields_text.append(f"\n{label} {text} - {urlinfo}")
                                    else:
                                        final_text.append(f"{label} {text}")

        # Append custom entities
        for name_edit, value_edit, _ in self.custom_entities:
            name = name_edit.text()
            value = value_edit.text()
            if name and value:
                custom_entities_text.append(f"{name}: {value}")

        # Append custom entities text
        final_text.extend(custom_entities_text)

        # Append other fields text
        final_text.extend(other_fields_text)

        # Append sign-off information at the bottom
        if self.escalation_rb.isChecked():
            sign_off_user = self.settings_tab.settings_sign_off_user.text()
            if sign_off_user:
                final_text.append(f"\nKind Regards,\n{sign_off_user},")
            sign_off_org = self.settings_tab.settings_sign_off_org.text()
            if sign_off_org:
                final_text.append(f"{sign_off_org}")

        self.output_text.setPlainText("\n".join(final_text))