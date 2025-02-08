import os
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QInputDialog, QMessageBox, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QAction
from .case_builder_tab import CaseBuilderTab
from .settings_tab import SettingsTab

class CaseBuilderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOC Case Builder")

        # Get screen dimensions
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width() // 2, screen.height())

        self.central_widget = QTabWidget()
        self.central_widget.tabBarDoubleClicked.connect(self.handle_tab_double_click)
        self.central_widget.tabBarClicked.connect(self.handle_tab_click)
        self.setCentralWidget(self.central_widget)
        
        self.create_menu()

        self.settings_tab = SettingsTab()
        self.case_builder_tab = CaseBuilderTab(self.settings_tab)

        self.central_widget.addTab(self.case_builder_tab, "Case 1")

    def closeEvent(self, event):
        print("Main window closing event triggered.")  # Debug print
        self.settings_tab.closeEvent(event)
        event.accept()
        
    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        new_case_action = QAction('New Case', self)
        new_case_action.triggered.connect(self.add_new_case_tab)
        file_menu.addAction(new_case_action)
        save_case_action = QAction('Save Case', self)
        save_case_action.triggered.connect(self.save_case)
        file_menu.addAction(save_case_action)

        rename_case_action = QAction('Rename Case', self)
        rename_case_action.triggered.connect(self.rename_case_tab)
        file_menu.addAction(rename_case_action)

        remove_case_action = QAction('Remove Case', self)
        remove_case_action.triggered.connect(self.remove_case_tab)
        file_menu.addAction(remove_case_action)

        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings_dialog)
        menubar.addAction(settings_action)

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
        if index != -1:
            current_tab_name = self.central_widget.tabText(index)
            new_tab_name, ok = QInputDialog.getText(self, "Rename Case Tab", "Enter new name:", text=current_tab_name)
            if ok and new_tab_name:
                self.central_widget.setTabText(index, new_tab_name)

    def open_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
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
        self.settings_tab.save_settings()

    def save_case(self):
        current_index = self.central_widget.currentIndex()
        if current_index != -1:
            current_tab = self.central_widget.widget(current_index)
            if isinstance(current_tab, CaseBuilderTab):
                compiled_info = current_tab.output_text.toPlainText()
                if compiled_info.strip():  # Check if there is any information
                    case_name = self.central_widget.tabText(current_index)
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"{case_name}_{timestamp}.txt"
                    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
                    os.makedirs(logs_dir, exist_ok=True)
                    filepath = os.path.join(logs_dir, filename)
                    with open(filepath, "w") as file:
                        file.write(compiled_info)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CaseBuilderWindow()
    window.show()
    sys.exit(app.exec())