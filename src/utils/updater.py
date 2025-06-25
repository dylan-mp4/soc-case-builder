import sys
import os
import time
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar

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
    win.label.setText("Extracting update...")
    win.progress.setMaximum(0)
    QApplication.processEvents()

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(app_dir)
    os.remove(zip_path)
    extracted_dir = os.path.join(app_dir, "soc_case_builder")
    if os.path.isdir(extracted_dir):
        for item in os.listdir(extracted_dir):
            s = os.path.join(extracted_dir, item)
            d = os.path.join(app_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.move(s, d)
            else:
                shutil.move(s, d)
        shutil.rmtree(extracted_dir)
    win.label.setText("Update complete. Restarting app...")
    QApplication.processEvents()
    time.sleep(1)
    exe_path = os.path.join(app_dir, "soc_case_builder.exe")
    os.execv(exe_path, [exe_path])

if __name__ == "__main__":
    time.sleep(2)
    main()