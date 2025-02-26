import json
import csv
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

        self.init_general_tab()
        self.init_api_settings_tab()
        self.init_spellcheck_tab()

        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.api_settings_tab, "API Settings")
        self.tab_widget.addTab(self.spellcheck_tab, "Spellcheck")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        # Load settings and clients when the settings dialog is initialized
        self.load_settings()
        self.load_clients()

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