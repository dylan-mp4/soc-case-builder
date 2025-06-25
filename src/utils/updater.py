import sys
import os
import time
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QMessageBox
import subprocess

class UpdateWindow(QWidget):
    def __init__(self, total_size):
        super().__init__()
        self.setWindowTitle("Updating Application")
        self.layout = QVBoxLayout()
        self.label = QLabel("Downloading update...")
        self.progress = QProgressBar()
        self.progress.setMaximum(total_size)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)
        self.setLayout(self.layout)
        self.show()

    def update_progress(self, value):
        self.progress.setValue(value)
        QApplication.processEvents()

def main():
    if len(sys.argv) < 2:
        print("No download URL provided.")
        sys.exit(1)
    download_url = sys.argv[1]
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    zip_path = os.path.join(app_dir, "update.zip")
    batch_path = os.path.join(app_dir, "update.bat")

    # Get file size for progress bar
    resp = requests.head(download_url, allow_redirects=True)
    total_size = int(resp.headers.get('content-length', 0))

    app = QApplication(sys.argv)
    win = UpdateWindow(total_size)

    print("Downloading update...")
    downloaded = 0
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    win.update_progress(downloaded)
    win.label.setText("Preparing update finalizer...")
    win.progress.setMaximum(0)
    QApplication.processEvents()

    # Write the batch file to disk
    batch_contents = r"""@echo off
timeout /t 2 >nul
powershell -Command "Expand-Archive -Path '%~1' -DestinationPath '%~2' -Force"
del "%~1"
start "" "%~2\soc_case_builder\soc_case_builder.exe"
"""
    try:
        with open(batch_path, "w") as bf:
            bf.write(batch_contents)
    except Exception as e:
        QMessageBox.critical(win, "Update Failed", f"Could not write batch file:\n{e}")
        sys.exit(1)

    win.label.setText("Launching update finalizer...")
    QApplication.processEvents()
    time.sleep(1)

    # Launch the batch file and exit
    try:
        subprocess.Popen(['cmd', '/c', batch_path, zip_path, app_dir])
    except Exception as e:
        QMessageBox.critical(win, "Update Failed", f"Could not launch batch file:\n{e}")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    time.sleep(2)
    main()