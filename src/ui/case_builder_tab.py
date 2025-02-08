from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QScrollArea, QTabWidget,
    QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QTextEdit, QComboBox, QHBoxLayout
)
import csv
from src.utils.api_requests import get_abuse_info, get_domain_info, get_hash_info, get_url_info
class CaseBuilderTab(QWidget):
    def __init__(self, settings_tab):
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

        self.add_field_with_button("Username:", self.common_fields_layout)
        self.add_field_with_button("Role:", self.common_fields_layout)
        self.add_field_with_button("Host:", self.common_fields_layout)
        self.add_field_with_button("IP:", self.common_fields_layout)
        self.add_field_with_button("Domain:", self.common_fields_layout)
        self.add_field_with_button("Hash:", self.common_fields_layout)
        self.add_field_with_button("URL:", self.common_fields_layout)
        self.scroll_layout.addLayout(self.common_fields_layout)

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

        self.crux_field = QLineEdit()
        self.escalation_info = QTextEdit()
        self.sign_off_user = QLineEdit()
        self.sign_off_org = QLineEdit()

        self.escalation_layout.addRow("Client:", self.client_combo)
        self.escalation_layout.addRow("Crux:", self.crux_field)
        self.escalation_layout.addRow("Information:", self.escalation_info)
        # deprecated sign off fields
        # self.escalation_layout.addRow("Sign off (User):", self.sign_off_user)
        # self.escalation_layout.addRow("Sign off (Org):", self.sign_off_org)

        self.close_reason = QTextEdit()
        self.close_info = QTextEdit()
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

        self.output_text = QTextEdit()
        self.case_builder_layout.addWidget(self.output_text)

        # Show relevant fields by default (close case)
        self.toggle_fields()

        self.close_case_rb.toggled.connect(self.toggle_fields)
        self.escalation_rb.toggled.connect(self.toggle_fields)

        self.setLayout(self.case_builder_layout)

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

    def add_field_with_button(self, label, layout):
        field_layout = QHBoxLayout()
        line_edit = QLineEdit()
        add_button = QPushButton("+")
        add_button.setMaximumWidth(20)
        add_button.clicked.connect(lambda: self.add_field_with_button(label, layout))
        field_layout.addWidget(line_edit)
        field_layout.addWidget(add_button)

        if label not in self.entity_positions:
            self.entity_positions[label] = layout.rowCount()
        else:
            self.entity_positions[label] += 1

        layout.insertRow(self.entity_positions[label], label, field_layout)
        self.update_entity_positions()

    def update_entity_positions(self):
        for i in range(self.common_fields_layout.rowCount()):
            label_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label_item:
                label = label_item.widget().text()
                self.entity_positions[label] = i

    def add_custom_entity(self):
        field_layout = QHBoxLayout()
        name_edit = QLineEdit()
        value_edit = QLineEdit()
        add_button = QPushButton("+")
        add_button.setMaximumWidth(20)
        add_button.clicked.connect(lambda: self.add_custom_entity())
        field_layout.addWidget(name_edit)
        field_layout.addWidget(value_edit)
        field_layout.addWidget(add_button)
        self.common_fields_layout.insertRow(self.common_fields_layout.rowCount() - 1, "", field_layout)
        self.custom_entities.append((name_edit, value_edit, add_button))

    def clear_fields(self):
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
        self.add_field_with_button("Username:", self.common_fields_layout)
        self.add_field_with_button("Role:", self.common_fields_layout)
        self.add_field_with_button("Host:", self.common_fields_layout)
        self.add_field_with_button("IP:", self.common_fields_layout)
        self.add_field_with_button("Domain:", self.common_fields_layout)
        self.add_field_with_button("Hash:", self.common_fields_layout)
        self.add_field_with_button("URL:", self.common_fields_layout)
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
        
        # Append client information at the top
        if self.escalation_rb.isChecked():
            client = self.client_combo.currentText()
            if client:
                final_text.append(f"Dear {client},")

        if self.close_case_rb.isChecked():
            reason = self.close_reason.toPlainText()
            if reason:
                final_text.append(f"{reason}")
            info = self.close_info.toPlainText()
            if info:
                final_text.append(f"{info}")
        else:
            crux = self.crux_field.text()
            if crux:
                final_text.append(f"{crux}")
            info = self.escalation_info.toPlainText()
            if info:
                final_text.append(f"{info}\n")

        # Append other fields
        for i in range(self.common_fields_layout.rowCount()):
            label_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = self.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                label = label_item.widget().text()
                field_layout = field_item.layout()
                if field_layout:
                    for j in range(field_layout.count()):
                        widget = field_layout.itemAt(j).widget()
                        if isinstance(widget, QLineEdit):
                            text = widget.text()
                            if text:  # Only include non-empty fields
                                if label == "IP:" and self.settings_tab.settings_abuse_api_key.text():
                                    abuse_info = get_abuse_info(text, self.settings_tab.settings_abuse_api_key.text())
                                    final_text.append(f"{label} {text} - {abuse_info}")
                                elif label == "Domain:":
                                    domain_info = get_domain_info(text)
                                    final_text.append(f"{label} {text} - {domain_info}")
                                elif label == "Hash:" and self.settings_tab.settings_vt_api_key.text():
                                    hash_info = get_hash_info(text, self.settings_tab.settings_vt_api_key.text())
                                    final_text.append(f"{label} {text} - {hash_info}")
                                elif label == "URL:" and self.settings_tab.settings_urlscan_api_key.text():
                                    urlinfo = get_url_info(text, self.settings_tab.settings_urlscan_api_key.text())
                                    final_text.append(f"{label} {text} - {urlinfo}")
                                else:
                                    final_text.append(f"{label} {text}")

        # Append custom entities
        for name_edit, value_edit, _ in self.custom_entities:
            name = name_edit.text()
            value = value_edit.text()
            if name and value:
                final_text.append(f"{name}: {value}")

        # Append sign-off information at the bottom
        if self.escalation_rb.isChecked():
            sign_off_user = self.settings_tab.settings_sign_off_user.text()
            if sign_off_user:
                final_text.append(f"Kind Regards,\n{sign_off_user},")
            sign_off_org = self.settings_tab.settings_sign_off_org.text()
            if sign_off_org:
                final_text.append(f"{sign_off_org}")

        self.output_text.setPlainText("\n".join(final_text))