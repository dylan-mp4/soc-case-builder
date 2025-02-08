from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class GettingStarted(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Getting Started")
        self.setFixedWidth(600)
        
        layout = QVBoxLayout()
        
        info_label = QLabel("Welcome to the SOC Case Builder!\n\n"
                            "This application helps you manage and build cases for security operations.\n\n"
                            "To get started, you need to configure API keys for various services:\n"
                            "- AbuseIPDB: Retrieve your API key from https://www.abuseipdb.com/account\n"
                            "- VirusTotal: Retrieve your API key from https://www.virustotal.com\n"
                            "- URLScan: Retrieve your API key from https://urlscan.io/user/\n\n"
                            "Please go to the Settings tab to enter your API keys and other information."
                            "\n\n Created by dylan-mp4")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
