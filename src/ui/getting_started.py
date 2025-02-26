from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class GettingStarted(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Getting Started")
        self.setFixedWidth(600)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Welcome to the SOC Case Builder!<br><br>"
            "This application helps you manage and build cases for security operations.<br><br>"
            "To get started, you need to configure API keys for various services:<br>"
            "- <a href='https://www.abuseipdb.com/account'>AbuseIPDB</a>: Retrieve your API key<br>"
            "- <a href='https://www.virustotal.com'>VirusTotal</a>: Retrieve your API key<br>"
            "- <a href='https://urlscan.io/user/'>URLScan</a>: Retrieve your API key<br><br>"
            "Please go to the Settings tab to enter your API keys<br><br>"
            "Clients can be added and managed through the settings dialog. The clients are stored in clients.csv.<br>"
            "Cases can be saved either with the Save button or by pressing Ctrl+S.<br>"
            "Cases are stored in the logs directory as json files and can be reloaded with the Load button or Ctrl+P.<br>"
            "Clients are stored in clients.csv and can be managed through the settings dialog, each client should be on a new line<br><br>"
            "Created by dylan-mp4"
        )
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)  # Enable clickable links
        layout.addWidget(info_label)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)