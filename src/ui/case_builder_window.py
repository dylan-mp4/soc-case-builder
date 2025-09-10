import json
import os
import re
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QInputDialog, QFormLayout, QLineEdit, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QAction
from resources.version import __version__
from ui.case_builder_tab import CaseBuilderTab
from ui.settings_dialog import SettingsDialog
from ui.getting_started import GettingStarted
from ui.search_cases import SearchCases
from ui.query_builder_dialog import QueryBuilderDialog
from ui.bulk_add_entities_dialog import BulkAddEntitiesDialog
from ui.stats_for_nerds import StatsForNerds
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

flask_main_window = None

class CaseBuilderWindow(QMainWindow):
    add_case_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        global flask_main_window
        flask_main_window = self
        self.add_case_signal.connect(self._add_case_from_api)

        self.settings_dialog = SettingsDialog()
        if self.settings_dialog.load_settings():
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
        self.case_builder_tab = CaseBuilderTab(self.settings_dialog)
        self.central_widget.addTab(self.case_builder_tab, "Case 1")

        self.start_flask_server()

    def start_flask_server(self):
        app = Flask(__name__)
        CORS(app)

        @app.route('/receive', methods=['POST'])
        def receive():
            data = request.get_json()
            print(f"Raw Recieved data: {data}")  # Debug print
            original_event_str = data.get("original-event", "")
            try:
                original_event = json.loads(original_event_str)
            except Exception as e:
                print("Failed to parse original-event JSON:", e)
                original_event = {}
            # Merge outer fields into original_event
            for key in ("case-url-link", "alert-title", "organization"):
                if key in data:
                    original_event[key] = data[key]
            print(f"Received data: {original_event}")
            if flask_main_window:
                flask_main_window.add_case_from_api(original_event)
            return jsonify({"status": "received"})

        threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False), daemon=True).start()

    def add_case_from_api(self, event_dict):
        print("add_case_from_api called!")
        self.add_case_signal.emit(event_dict)

    def _add_case_from_api(self, event_dict):
        print("_add_case_from_api called!")
        new_tab = CaseBuilderTab(self.settings_dialog)
        tab_name = event_dict.get("alert-title", f"Case {self.central_widget.count() + 1}")
        self.central_widget.addTab(new_tab, tab_name)
        self.central_widget.setCurrentWidget(new_tab)
        # Do NOT automatically select escalation flow; stay on close info flow
        new_tab.close_case_rb.setChecked(True)
        new_tab.toggle_fields()
        # Set info text if present
        info_text = event_dict.get("info", "")
        new_tab.escalation_info.setPlainText(info_text)
        # Insert organisation into client text box and print it
        organisation = event_dict.get("organization", "")
        if organisation:
            print(f"organization: {organisation}")
            new_tab.client_combo.setCurrentText(organisation)
            index = new_tab.client_combo.findText(organisation, Qt.MatchFlag.MatchFixedString)
            if index != -1:
                new_tab.client_combo.setCurrentIndex(index)
        # Add observables as regular entities (fields), supporting multiples
        observables = event_dict.get("observables", [])
        for obs in observables:
            obs_type = obs.get("observable-type", "Other")
            obs_value = obs.get("observable", "")
            if obs_type.lower() == "user":
                label = "Username:"
            elif obs_type.lower() == "mailbox":
                label = "E-mail:"
            elif obs_type in ("ipv4_public", "ipv6_public", "IP", "ip", "Ip"):
                label = "IP:"
            else:
                label = f"{obs_type.capitalize()}:"
            if obs_value:
                # Try to find an existing field for this label that is empty
                found_empty = False
                for i in range(new_tab.common_fields_layout.rowCount()):
                    label_item = new_tab.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    field_item = new_tab.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
                    if label_item and field_item and label_item.widget().text() == label:
                        field_layout = field_item.layout()
                        if field_layout and field_layout.count() > 0:
                            widget = field_layout.itemAt(0).widget()
                            if widget and not widget.text():
                                widget.setText(obs_value)
                                found_empty = True
                                break
                if not found_empty:
                    # If no empty field, add a new one
                    new_tab.add_field(label, new_tab.common_fields_layout)
                    pos = new_tab.entity_positions.get(label)
                    if pos is not None:
                        field_item = new_tab.common_fields_layout.itemAt(pos, QFormLayout.ItemRole.FieldRole)
                        if field_item:
                            field_layout = field_item.layout()
                            if field_layout and field_layout.count() > 0:
                                widget = field_layout.itemAt(0).widget()
                                if widget:
                                    widget.setText(obs_value)
        # Handle Case Link
        case_url = event_dict.get("case-url-link", "")
        if case_url:
            label = "Case Link:"
            # Try to find an existing Case Link field that is empty
            found_empty = False
            for i in range(new_tab.common_fields_layout.rowCount()):
                label_item = new_tab.common_fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                field_item = new_tab.common_fields_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
                if label_item and field_item and label_item.widget().text() == label:
                    field_layout = field_item.layout()
                    if field_layout and field_layout.count() > 0:
                        widget = field_layout.itemAt(0).widget()
                        if widget and not widget.text():
                            widget.setText(case_url)
                            found_empty = True
                            break
            if not found_empty:
                new_tab.add_field(label, new_tab.common_fields_layout)
                pos = new_tab.entity_positions.get(label)
                if pos is not None:
                    field_item = new_tab.common_fields_layout.itemAt(pos, QFormLayout.ItemRole.FieldRole)
                    if field_item:
                        field_layout = field_item.layout()
                        if field_layout and field_layout.count() > 0:
                            widget = field_layout.itemAt(0).widget()
                            if widget:
                                widget.setText(case_url)
        print(f"Added new case tab '{tab_name}' with info and {len(observables)} observables.")

    def show_getting_started(self):
        dialog = GettingStarted()
        dialog.exec()

    def closeEvent(self, event):
        print("Main window closing event triggered.")  # Debug print
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

        save_all_cases_action = QAction('Save All Cases', self)
        save_all_cases_action.setShortcut('Ctrl+Shift+S')
        save_all_cases_action.triggered.connect(self.save_all_cases)
        file_menu.addAction(save_all_cases_action)

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

        search_cases_action = QAction('Search Cases', self)
        search_cases_action.setShortcut('Ctrl+F')
        search_cases_action.triggered.connect(self.open_search_cases)
        menubar.addAction(search_cases_action)
        
        getting_started_action = QAction('Getting Started', self)
        getting_started_action.triggered.connect(self.open_getting_started)
        menubar.addAction(getting_started_action)

        query_builder_action = QAction('Query Builder', self)
        query_builder_action.triggered.connect(self.open_query_builder_dialog)
        menubar.addAction(query_builder_action)

        bulk_add_action = QAction('Bulk Add Entities', self)
        bulk_add_action.triggered.connect(self.open_bulk_add_entities)
        menubar.addAction(bulk_add_action)

        stats_action = QAction('Stats for Nerds', self)
        stats_action.triggered.connect(self.open_stats_for_nerds)
        menubar.addAction(stats_action)

    def open_search_cases(self):
        dialog = SearchCases(self)
        dialog.exec()

    def open_getting_started(self):
        dialog = GettingStarted()
        dialog.exec()

    def open_settings_dialog(self):
        self.settings_dialog.load_settings()  # Reload settings before showing the dialog
        self.settings_dialog.exec()

    def open_stats_for_nerds(self):
        print("Opening Stats for Nerds dialog...")  # Debug print
        self.stats_dialog = StatsForNerds(self)
        self.stats_dialog.show()

    def open_query_builder_dialog(self):
        dialog = QueryBuilderDialog(self)
        dialog.exec()

    def add_new_case_tab(self):
        new_tab = CaseBuilderTab(self.settings_dialog)
        self.central_widget.addTab(new_tab, f"Case {self.central_widget.count() + 1}")
        self.central_widget.setCurrentWidget(new_tab)

    # ...existing code...
    def open_bulk_add_entities(self):
        dialog = BulkAddEntitiesDialog(self)
        if dialog.exec():
            entities = dialog.get_entities()
            for label, value in entities:
                entity_type = dialog.detect_entity_type(value)
                if not label or label.lower() == "other":
                    if entity_type == "Other":
                        label = "Other:"
                    else:
                        label = f"{entity_type}:"
                else:
                    label = f"{label}:"
                # Add to current tab
                current_tab = self.central_widget.currentWidget()
                if isinstance(current_tab, CaseBuilderTab):
                    current_tab.add_field(label, current_tab.common_fields_layout)
                    # Set value in the last added field
                    pos = current_tab.entity_positions.get(label)
                    if pos is not None:
                        field_item = current_tab.common_fields_layout.itemAt(pos, QFormLayout.ItemRole.FieldRole)
                        if field_item:
                            field_layout = field_item.layout()
                            if field_layout and field_layout.count() > 0:
                                widget = field_layout.itemAt(0).widget()
                                if widget:
                                    widget.setText(value)
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
                    # "close_info": current_tab.close_info.toPlainText(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                for name_edit, value_edit, *_ in current_tab.custom_entities:
                    name = name_edit.text()
                    value = value_edit.text()
                    if name and value:
                        case_data["custom_entities"].append({"name": name, "value": value})

                case_name = self.central_widget.tabText(current_index)
                sanitized_case_name = re.sub(r'[^\w\s-]', '_', case_name)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{sanitized_case_name}_{timestamp}.json"
                logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
                os.makedirs(logs_dir, exist_ok=True)
                filepath = os.path.join(logs_dir, filename)
                with open(filepath, "w") as file:
                    json.dump(case_data, file, indent=4)
                    
    def save_all_cases(self):
        for i in range(self.central_widget.count()):
            current_tab = self.central_widget.widget(i)
            if isinstance(current_tab, CaseBuilderTab):
                case_data = {
                    "tab_name": self.central_widget.tabText(i),
                    "fields": [],
                    "custom_entities": [],
                    "route": "close" if current_tab.close_case_rb.isChecked() else "escalation",
                    "client": current_tab.client_combo.currentText(),
                    "crux": current_tab.crux_field.text(),
                    "escalation_info": current_tab.escalation_info.toPlainText(),
                    "close_reason": current_tab.close_reason.toPlainText(),
                    # "close_info": current_tab.close_info.toPlainText(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Save common fields
                for j in range(current_tab.common_fields_layout.rowCount()):
                    label_item = current_tab.common_fields_layout.itemAt(j, QFormLayout.ItemRole.LabelRole)
                    field_item = current_tab.common_fields_layout.itemAt(j, QFormLayout.ItemRole.FieldRole)
                    if label_item and field_item:
                        label = label_item.widget().text()
                        field_layout = field_item.layout()
                        if field_layout:
                            for k in range(field_layout.count()):
                                widget = field_layout.itemAt(k).widget()
                                if isinstance(widget, QLineEdit):
                                    text = widget.text()
                                    if text:
                                        case_data["fields"].append({"label": label, "value": text})

                # Save custom entities
                for name_edit, value_edit, *_ in current_tab.custom_entities:
                    name = name_edit.text()
                    value = value_edit.text()
                    if name and value:
                        case_data["custom_entities"].append({"name": name, "value": value})

                case_name = self.central_widget.tabText(i)
                sanitized_case_name = re.sub(r'[^\w\s-]', '_', case_name)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{sanitized_case_name}_{timestamp}.json"
                logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
                os.makedirs(logs_dir, exist_ok=True)
                filepath = os.path.join(logs_dir, filename)
                with open(filepath, "w") as file:
                    json.dump(case_data, file, indent=4)

    def load_case(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Load Case", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
            full_file_path = os.path.join(logs_dir, file_path)
            print(f"Loading case from file: {full_file_path}")  # Debug print
            with open(full_file_path, "r") as file:
                case_data = json.load(file)
                initial_fields = case_data.get("fields", [])
                new_tab = CaseBuilderTab(self.settings_dialog, initial_fields)
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
                # new_tab.close_info.setPlainText(case_data.get("close_info", ""))
                if case_data.get("route") == "escalation":
                    new_tab.escalation_rb.setChecked(True)
                else:
                    new_tab.close_case_rb.setChecked(True)
                new_tab.toggle_fields()
                self.central_widget.setCurrentWidget(new_tab)
                        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CaseBuilderWindow()
    window.show()
    sys.exit(app.exec())