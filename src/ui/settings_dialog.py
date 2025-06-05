import json
import csv
import os
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QMessageBox, QDialog, QVBoxLayout, QTabWidget, QListWidget, QComboBox, QHBoxLayout
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt
import enchant

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedWidth(800)  # Set the fixed width of the dialog to 800px

        self.tab_widget = QTabWidget()
        self.general_tab = QWidget()
        self.api_settings_tab = QWidget()
        self.spellcheck_tab = QWidget()
        self.entity_settings_tab = QWidget()
        self.preferences_tab = QWidget()

        self.init_general_tab()
        self.init_api_settings_tab()
        self.init_spellcheck_tab()
        self.init_entity_settings_tab()
        self.init_preferences_tab()

        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.api_settings_tab, "API Settings")
        self.tab_widget.addTab(self.spellcheck_tab, "Spellcheck")
        self.tab_widget.addTab(self.entity_settings_tab, "Entity Settings")
        self.tab_widget.addTab(self.preferences_tab, "Preferences")


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        # Load settings and clients when the settings dialog is initialized
        self.load_settings()
        self.load_clients()

    # General Tab
    def init_general_tab(self):
        self.general_form_layout = QFormLayout()

        self.settings_sign_off_user = QLineEdit()
        self.settings_sign_off_org = QLineEdit()
        self.general_form_layout.addRow("Sign off (User):", self.settings_sign_off_user)
        self.general_form_layout.addRow("Sign off (Org):", self.settings_sign_off_org)

        self.save_general_settings_button = QPushButton("Save General Settings")
        self.save_general_settings_button.clicked.connect(self.save_settings)
        self.general_form_layout.addRow(self.save_general_settings_button)

        # Add clients section
        self.general_form_layout.addRow(QLabel("<h3>Clients</h3>"))
        self.clients_text_edit = QTextEdit()
        self.general_form_layout.addRow(self.clients_text_edit)

        self.general_tab.setLayout(self.general_form_layout)

    # API Settings Tab
    def init_api_settings_tab(self):
        self.api_settings_form_layout = QFormLayout()

        self.settings_abuse_api_key = QLineEdit()
        self.settings_vt_api_key = QLineEdit()
        self.settings_urlscan_api_key = QLineEdit()
        self.settings_urlscan_wait_time = QLineEdit()
        self.settings_urlscan_wait_time.setValidator(QIntValidator(0, 100))
        self.api_settings_form_layout.addRow("AbuseIPDB API Key:", self.settings_abuse_api_key)
        self.api_settings_form_layout.addRow("VirusTotal API Key:", self.settings_vt_api_key)
        self.api_settings_form_layout.addRow("URLScan API Key:", self.settings_urlscan_api_key)
        self.api_settings_form_layout.addRow("URLScan wait time (0-100s):", self.settings_urlscan_wait_time)

        self.save_api_settings_button = QPushButton("Save API Settings")
        self.save_api_settings_button.clicked.connect(self.save_settings)
        self.api_settings_form_layout.addRow(self.save_api_settings_button)

        self.api_settings_tab.setLayout(self.api_settings_form_layout)

    # Spellcheck Tab
    def init_spellcheck_tab(self):
        self.spellcheck_form_layout = QFormLayout()

        self.custom_dict_list = QListWidget()
        self.load_custom_dictionary()
        self.spellcheck_form_layout.addRow("Custom Dictionary:", self.custom_dict_list)

        self.add_word_line_edit = QLineEdit()
        self.add_word_button = QPushButton("Add Word")
        self.add_word_button.clicked.connect(self.add_word_to_custom_dict)
        add_word_layout = QHBoxLayout()
        add_word_layout.addWidget(self.add_word_line_edit)
        add_word_layout.addWidget(self.add_word_button)
        self.spellcheck_form_layout.addRow("Add Word:", add_word_layout)

        self.remove_word_button = QPushButton("Remove Selected Word")
        self.remove_word_button.clicked.connect(self.remove_word_from_custom_dict)
        self.spellcheck_form_layout.addRow(self.remove_word_button)

        self.language_region_combo = QComboBox()
        self.language_region_combo.addItems(enchant.list_languages())
        self.spellcheck_form_layout.addRow("Language Region:", self.language_region_combo)

        self.save_spellcheck_settings_button = QPushButton("Save Spellcheck Settings")
        self.save_spellcheck_settings_button.clicked.connect(self.save_spellcheck_settings)
        self.spellcheck_form_layout.addRow(self.save_spellcheck_settings_button)

        self.spellcheck_tab.setLayout(self.spellcheck_form_layout)

    # Entity Settings Tab
    def init_entity_settings_tab(self):
        layout = QVBoxLayout()

        self.entity_list = QListWidget()
        self.load_entities()
        layout.addWidget(self.entity_list)

        self.new_entity_edit = QLineEdit()
        layout.addWidget(self.new_entity_edit)

        self.add_entity_button = QPushButton("Add Entity")
        self.add_entity_button.clicked.connect(self.add_entity)
        layout.addWidget(self.add_entity_button)

        self.remove_entity_button = QPushButton("Remove Selected Entity")
        self.remove_entity_button.clicked.connect(self.remove_entity)
        layout.addWidget(self.remove_entity_button)

        self.reset_entities_button = QPushButton("Reset to Default")
        self.reset_entities_button.clicked.connect(self.reset_entities)
        layout.addWidget(self.reset_entities_button)

        self.entity_settings_tab.setLayout(layout)

    # Load and Save Entities
    def load_entities(self):
        try:
            with open("entities.json", "r") as file:
                entities = json.load(file)
                self.entity_list.addItems(entities)
        except FileNotFoundError:
            self.entity_list.addItems([
                "Case Link", "Username", "Role", "Location", "Host", "IP", "Domain", "Hash", "URL"
            ])
            
    def save_entities(self):
        entities = [self.entity_list.item(i).text() for i in range(self.entity_list.count())]
        with open("entities.json", "w") as file:
            json.dump(entities, file, indent=4)

    def add_entity(self):
        new_entity = self.new_entity_edit.text().strip()
        if new_entity:
            self.entity_list.addItem(new_entity)
            self.new_entity_edit.clear()
            self.save_entities()

    def remove_entity(self):
        selected_items = self.entity_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.entity_list.takeItem(self.entity_list.row(item))
        self.save_entities()
    
    def reset_entities(self):
        default_entities = [
            "Case Link", "Username", "Role", "Location", "Host", "IP", "Domain", "Hash", "URL"
        ]
        self.entity_list.clear()
        self.entity_list.addItems(default_entities)
        self.save_entities()

    # Save Settings
    def save_settings(self):
        settings = {
            "sign_off_user": self.settings_sign_off_user.text(),
            "sign_off_org": self.settings_sign_off_org.text(),
            "abuse_api_key": self.settings_abuse_api_key.text(),
            "vt_api_key": self.settings_vt_api_key.text(),
            "urlscan_api_key": self.settings_urlscan_api_key.text(),
            "urlscan_wait_time": self.settings_urlscan_wait_time.text(),
            "first_time": False,
            "language_region": self.language_region_combo.currentText()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

        self.save_clients()
        self.save_custom_dictionary()
        self.save_entities()

    # Load Settings
    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.settings_sign_off_user.setText(settings.get("sign_off_user", ""))
                self.settings_sign_off_org.setText(settings.get("sign_off_org", ""))
                self.settings_abuse_api_key.setText(settings.get("abuse_api_key", ""))
                self.settings_vt_api_key.setText(settings.get("vt_api_key", ""))
                self.settings_urlscan_api_key.setText(settings.get("urlscan_api_key", ""))
                self.settings_urlscan_wait_time.setText(settings.get("urlscan_wait_time", ""))
                self.language_region_combo.setCurrentText(settings.get("language_region", "en_GB"))
                return settings.get("first_time", True)
        except FileNotFoundError:
            return True

    # Load and Save Clients
    def load_clients(self):
        try:
            with open('clients.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                clients = "\n".join([",".join(row) for row in reader])
                self.clients_text_edit.setPlainText(clients)
        except FileNotFoundError:
            self.clients_text_edit.setPlainText("")

    def save_clients(self):
        clients_text = self.clients_text_edit.toPlainText()
        clients = [row.split(",") for row in clients_text.split("\n") if row]
        with open('clients.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(clients)
        QMessageBox.information(self, "Success", "Settings and clients saved successfully!")

    # Load and Save Custom Dictionary
    def load_custom_dictionary(self):
        try:
            with open('custom_dict.txt', 'r') as f:
                words = f.read().splitlines()
                self.custom_dict_list.addItems(words)
        except FileNotFoundError:
            pass

    def save_custom_dictionary(self):
        words = [self.custom_dict_list.item(i).text() for i in range(self.custom_dict_list.count())]
        with open('custom_dict.txt', 'w') as f:
            f.write("\n".join(words))

    def add_word_to_custom_dict(self):
        word = self.add_word_line_edit.text().strip()
        if word and not self.custom_dict_list.findItems(word, Qt.MatchFlag.MatchExactly):
            self.custom_dict_list.addItem(word)
            self.add_word_line_edit.clear()

    def remove_word_from_custom_dict(self):
        for item in self.custom_dict_list.selectedItems():
            self.custom_dict_list.takeItem(self.custom_dict_list.row(item))

    def save_spellcheck_settings(self):
        self.save_custom_dictionary()
        QMessageBox.information(self, "Success", "Spellcheck settings saved successfully!")

    def init_preferences_tab(self):
        layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.load_themes()
        self.apply_theme_button = QPushButton("Apply Theme")
        self.apply_theme_button.clicked.connect(self.apply_selected_theme)
        layout.addRow(QLabel("Theme:"), self.theme_combo)
        layout.addRow(self.apply_theme_button)
        self.preferences_tab.setLayout(layout)

    def load_themes(self):
        themes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'themes')
        self.theme_combo.clear()
        if os.path.isdir(themes_dir):
            themes = [f for f in os.listdir(themes_dir) if f.endswith('.qss')]
            self.theme_combo.addItems(themes)
        else:
            self.theme_combo.addItem("No themes found")

    def apply_selected_theme(self):
        theme_name = self.theme_combo.currentText()
        themes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'themes')
        theme_path = os.path.join(themes_dir, theme_name)
        if os.path.isfile(theme_path):
            with open(theme_path, "r", encoding="utf-8") as f:
                qss = f.read()
                from PyQt6.QtWidgets import QApplication
                QApplication.instance().setStyleSheet(qss)
            self.save_theme_to_settings(theme_name)  # Save theme to settings.json
            QMessageBox.information(self, "Theme Applied", f"Theme '{theme_name}' has been applied.")
        else:
            QMessageBox.warning(self, "Theme Not Found", "Selected theme file does not exist.")

    def save_theme_to_settings(self, theme_name):
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'settings.json')
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}
        settings["theme"] = theme_name
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)