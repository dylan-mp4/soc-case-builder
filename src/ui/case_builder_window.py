import json
import os
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QInputDialog, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QAction
from resources.version import __version__
from ui.case_builder_tab import CaseBuilderTab
from ui.settings_tab import SettingsTab
from ui.getting_started import GettingStarted

class CaseBuilderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_tab = SettingsTab()
        if self.settings_tab.load_settings():
            self.show_getting_started()

        self.setWindowTitle(f"SOC Case Builder v{__version__}")

        # Get screen dimensions
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width() // 2, screen.height()-100)

        self.central_widget = QTabWidget()
        self.central_widget.tabBarDoubleClicked.connect(self.handle_tab_double_click)
        self.central_widget.tabBarClicked.connect(self.handle_tab_click)
        self.setCentralWidget(self.central_widget)
        
        self.create_menu()
        self.case_builder_tab = CaseBuilderTab(self.settings_tab)
        self.central_widget.addTab(self.case_builder_tab, "Case 1")

    def show_getting_started(self):
        dialog = GettingStarted()
        dialog.exec()

    def closeEvent(self, event):
        print("Main window closing event triggered.")  # Debug print
        self.settings_tab.closeEvent(event)
        event.accept()
        
    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        new_case_action = QAction('New Case', self)
        new_case_action.setShortcut('Ctrl+T')
        new_case_action.triggered.connect(self.add_new_case_tab)
        file_menu.addAction(new_case_action)

        save_case_action = QAction('Save Case', self)
        save_case_action.setShortcut('Ctrl+S')
        save_case_action.triggered.connect(self.save_case)
        file_menu.addAction(save_case_action)

        load_case_action = QAction('Load Case', self)
        load_case_action.setShortcut('Ctrl+P')
        load_case_action.triggered.connect(self.load_case)
        file_menu.addAction(load_case_action)

        rename_case_action = QAction('Rename Case', self)
        rename_case_action.setShortcut('Ctrl+R')
        rename_case_action.triggered.connect(self.rename_case_tab)
        file_menu.addAction(rename_case_action)

        remove_case_action = QAction('Remove Case', self)
        remove_case_action.setShortcut('Ctrl+W')
        remove_case_action.triggered.connect(self.remove_case_tab)
        file_menu.addAction(remove_case_action)

        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings_dialog)
        menubar.addAction(settings_action)        
        
        GettingStarted_action = QAction('Getting Started', self)
        GettingStarted_action.triggered.connect(self.open_getting_started)
        menubar.addAction(GettingStarted_action)

    def open_getting_started(self):
        dialog = GettingStarted()
        dialog.exec()

    def add_new_case_tab(self):
        new_tab = CaseBuilderTab(self.settings_tab)
        self.central_widget.addTab(new_tab, f"Case {self.central_widget.count() + 1}")

    def rename_case_tab(self):
        current_index = self.central_widget.currentIndex()
        if current_index != -1:
            current_tab_name = self.central_widget.tabText(current_index)
            new_tab_name, ok = QInputDialog.getText(self, "Rename Case Tab", "Enter new name:", text=current_tab_name)
            if ok and new_tab_name:
                self.central_widget.setTabText(current_index, new_tab_name)

    def remove_case_tab(self):
        current_index = self.central_widget.currentIndex()
        if current_index != -1:
            self.central_widget.removeTab(current_index)

    def handle_tab_click(self, index):
        event = QGuiApplication.mouseButtons()
        if event == Qt.MouseButton.MiddleButton:
            self.central_widget.setCurrentIndex(index)
            self.remove_case_tab()

    def handle_tab_double_click(self, index):
        event = QGuiApplication.mouseButtons()
        if index != -1 and event == Qt.MouseButton.LeftButton:
            current_tab_name = self.central_widget.tabText(index)
            new_tab_name, ok = QInputDialog.getText(self, "Rename Case Tab", "Enter new name:", text=current_tab_name)
            if ok and new_tab_name:
                self.central_widget.setTabText(index, new_tab_name)

    def open_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setFixedWidth(800)  # Set the fixed width of the dialog to 800px
        layout = QVBoxLayout()

        # Create a new form layout and add copies of the widgets from settings_form_layout
        form_layout = QFormLayout()
        new_fields = {}
        for i in range(self.settings_tab.settings_form_layout.rowCount()):
            label_item = self.settings_tab.settings_form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = self.settings_tab.settings_form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                label = label_item.widget().text()
                field = field_item.widget()
                if isinstance(field, QLineEdit):
                    new_field = QLineEdit()
                    new_field.setText(field.text())
                    form_layout.addRow(label, new_field)
                    new_fields[label] = new_field

        # Add the clients text edit
        clients_label = QLabel("Clients:")
        clients_text_edit = QTextEdit()
        clients_text_edit.setPlainText(self.settings_tab.clients_text_edit.toPlainText())
        form_layout.addRow(clients_label, clients_text_edit)
        new_fields["clients_text_edit"] = clients_text_edit

        # Add the save settings button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(lambda: self.save_settings_from_dialog(new_fields))
        form_layout.addRow(save_button)

        layout.addLayout(form_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def save_settings_from_dialog(self, new_fields):
        self.settings_tab.settings_sign_off_user.setText(new_fields["Sign off (User):"].text())
        self.settings_tab.settings_sign_off_org.setText(new_fields["Sign off (Org):"].text())
        self.settings_tab.settings_abuse_api_key.setText(new_fields["AbuseIPDB API Key:"].text())
        self.settings_tab.settings_vt_api_key.setText(new_fields["VirusTotal API Key:"].text())
        self.settings_tab.settings_urlscan_api_key.setText(new_fields["URLScan API Key:"].text())
        self.settings_tab.settings_urlscan_wait_time.setText(new_fields["URLScan wait time (0-100s):"].text())
        self.settings_tab.clients_text_edit.setPlainText(new_fields["clients_text_edit"].toPlainText())
        self.settings_tab.save_settings()

    def save_case(self):
        current_index = self.central_widget.currentIndex()
        if current_index != -1:
            current_tab = self.central_widget.widget(current_index)
            if isinstance(current_tab, CaseBuilderTab):
                case_data = {
                    "tab_name": self.central_widget.tabText(current_index),
                    "fields": [],
                    "custom_entities": [],
                    "route": "close" if current_tab.close_case_rb.isChecked() else "escalation",
                    "client": current_tab.client_combo.currentText(),
                    "crux": current_tab.crux_field.text(),
                    "escalation_info": current_tab.escalation_info.toPlainText(),
                    "close_reason": current_tab.close_reason.toPlainText(),
                    "close_info": current_tab.close_info.toPlainText()
                }

                # Save common fields
                for i in range(current_tab.common_fields_layout.rowCount()):
                    label_item = current_tab.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    field_item = current_tab.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
                    if label_item and field_item:
                        label = label_item.widget().text()
                        field_layout = field_item.layout()
                        if field_layout:
                            for j in range(field_layout.count()):
                                widget = field_layout.itemAt(j).widget()
                                if isinstance(widget, QLineEdit):
                                    text = widget.text()
                                    if text:
                                        case_data["fields"].append({"label": label, "value": text})

                # Save custom entities
                for name_edit, value_edit, _ in current_tab.custom_entities:
                    name = name_edit.text()
                    value = value_edit.text()
                    if name and value:
                        case_data["custom_entities"].append({"name": name, "value": value})

                case_name = self.central_widget.tabText(current_index)
                sanitized_case_name = case_name.replace(".", "_")
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{sanitized_case_name}_{timestamp}.json"
                logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
                os.makedirs(logs_dir, exist_ok=True)
                filepath = os.path.join(logs_dir, filename)
                with open(filepath, "w") as file:
                    json.dump(case_data, file, indent=4)

    def load_case(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Case", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            with open(file_path, "r") as file:
                case_data = json.load(file)
                initial_fields = case_data.get("fields", [])
                new_tab = CaseBuilderTab(self.settings_tab, initial_fields)
                self.central_widget.addTab(new_tab, case_data["tab_name"])

                # Load custom entities
                for entity in case_data.get("custom_entities", []):
                    new_tab.add_custom_entity()
                    new_tab.custom_entities[-1][0].setText(entity["name"])
                    new_tab.custom_entities[-1][1].setText(entity["value"])

                # Load other fields
                new_tab.client_combo.setCurrentText(case_data.get("client", ""))
                new_tab.crux_field.setText(case_data.get("crux", ""))
                new_tab.escalation_info.setPlainText(case_data.get("escalation_info", ""))
                new_tab.close_reason.setPlainText(case_data.get("close_reason", ""))
                new_tab.close_info.setPlainText(case_data.get("close_info", ""))
                if case_data.get("route") == "escalation":
                    new_tab.escalation_rb.setChecked(True)
                else:
                    new_tab.close_case_rb.setChecked(True)
                new_tab.toggle_fields()
                        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CaseBuilderWindow()
    window.show()
    sys.exit(app.exec())