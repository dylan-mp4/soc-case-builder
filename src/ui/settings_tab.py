import json
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QLabel
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
        self.settings_form_layout.addRow(QLabel('Please read the API documentation for the following services especially urlscan by default scans are public and could reveal PII'), QLabel())
        self.settings_form_layout.addRow(QLabel('Retrieve API Key for AbuseIPDB from <a href="https://www.abuseipdb.com/account">here</a>'), QLabel())
        self.settings_form_layout.addRow("AbuseIPDB API Key:", self.settings_abuse_api_key)
        self.settings_form_layout.addRow(QLabel('Retrieve API Key for VirusTotal from <a href="https://www.virustotal.com">here</a>'), QLabel())
        self.settings_form_layout.addRow("VirusTotal API Key:", self.settings_vt_api_key)
        self.settings_form_layout.addRow(QLabel('Retrieve API Key for URLScan from <a href="https://urlscan.io/user/">here</a> - Note: URLScan can add a delay to the scan'), QLabel())
        self.settings_form_layout.addRow("URLScan API Key:", self.settings_urlscan_api_key)
        self.settings_form_layout.addRow("URLScan wait time (0-100s):", self.settings_urlscan_wait_time)

        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        self.settings_form_layout.addRow(self.save_settings_button)

        self.setLayout(self.settings_form_layout)

        # Load settings when the settings tab is initialized
        self.load_settings()

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