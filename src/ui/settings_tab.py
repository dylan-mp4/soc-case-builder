
import json
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_form_layout = QFormLayout()
        
        self.settings_sign_off_user = QLineEdit()
        self.settings_sign_off_org = QLineEdit()
        self.settings_abuse_api_key = QLineEdit()
        self.settings_vt_api_key = QLineEdit()

        self.settings_form_layout.addRow("Sign off (User):", self.settings_sign_off_user)
        self.settings_form_layout.addRow("Sign off (Org):", self.settings_sign_off_org)
        self.settings_form_layout.addRow("AbuseIPDB API Key:", self.settings_abuse_api_key)
        self.settings_form_layout.addRow("VirusTotal API Key:", self.settings_vt_api_key)

        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        self.settings_form_layout.addRow(self.save_settings_button)

        self.setLayout(self.settings_form_layout)

    def save_settings(self):
        settings = {
            "sign_off_user": self.settings_sign_off_user.text(),
            "sign_off_org": self.settings_sign_off_org.text(),
            "abuse_api_key": self.settings_abuse_api_key.text(),
            "vt_api_key": self.settings_vt_api_key.text()
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
        except FileNotFoundError:
            pass