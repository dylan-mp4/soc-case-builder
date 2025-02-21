import json
import csv
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QMessageBox
from PyQt6.QtGui import QIntValidator

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        self.settings_form_layout = QFormLayout()
        
        self.settings_sign_off_user = QLineEdit()
        self.settings_sign_off_org = QLineEdit()
        self.settings_abuse_api_key = QLineEdit()
        self.settings_vt_api_key = QLineEdit()
        self.settings_urlscan_api_key = QLineEdit()
        self.settings_urlscan_wait_time = QLineEdit()
        self.settings_urlscan_wait_time.setValidator(QIntValidator(0, 100))
        self.settings_form_layout.addRow("Sign off (User):", self.settings_sign_off_user)
        self.settings_form_layout.addRow("Sign off (Org):", self.settings_sign_off_org)
        self.settings_form_layout.addRow("AbuseIPDB API Key:", self.settings_abuse_api_key)
        self.settings_form_layout.addRow("VirusTotal API Key:", self.settings_vt_api_key)
        self.settings_form_layout.addRow("URLScan API Key:", self.settings_urlscan_api_key)
        self.settings_form_layout.addRow("URLScan wait time (0-100s):", self.settings_urlscan_wait_time)

        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        self.settings_form_layout.addRow(self.save_settings_button)

        # Add clients section
        self.settings_form_layout.addRow(QLabel("<h3>Clients</h3>"))
        self.clients_text_edit = QTextEdit()
        self.settings_form_layout.addRow(self.clients_text_edit)

        self.setLayout(self.settings_form_layout)

        # Load settings and clients when the settings tab is initialized
        self.load_settings()
        self.load_clients()

    def save_settings(self):
        settings = {
            "sign_off_user": self.settings_sign_off_user.text(),
            "sign_off_org": self.settings_sign_off_org.text(),
            "abuse_api_key": self.settings_abuse_api_key.text(),
            "vt_api_key": self.settings_vt_api_key.text(),
            "urlscan_api_key": self.settings_urlscan_api_key.text(),
            "urlscan_wait_time": self.settings_urlscan_wait_time.text(),
            "first_time": False
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        
        self.save_clients()

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