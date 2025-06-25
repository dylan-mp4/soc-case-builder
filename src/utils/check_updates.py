import requests
import tempfile
import zipfile
import subprocess
import sys
import os

def get_latest_release_info():
    url = "https://api.github.com/repos/dylan-mp4/soc-case-builder/releases/latest"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    version = data["tag_name"]
    for asset in data["assets"]:
        if asset["name"].endswith(".zip"):
            return version, asset["browser_download_url"]
    return None, None

def prompt_and_update_if_needed(current_version):
    latest_version, download_url = get_latest_release_info()
    if latest_version:
        print(f"Current version: v{current_version}, Latest version: {latest_version}")
        # Normalize both versions for comparison
        try:
            current_tuple = normalize_version(current_version)
            latest_tuple = normalize_version(latest_version)
        except Exception as e:
            print("Version normalization failed:", e)
            return False
        if latest_tuple > current_tuple:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                None,
                "Update Available",
                f"A new version ({latest_version}) is available. Update now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                updater_path = os.path.join(os.path.dirname(__file__), "updater.py")
                if getattr(sys, 'frozen', False):
                    # Running as bundled app: use the updater as a script with the bundled python
                    updater_exe = sys.executable  # This is soc_case_builder.exe
                    # The updater script path must be absolute and inside the bundle
                    updater_path = os.path.join(os.path.dirname(sys.executable), 'utils', 'updater.py')
                    subprocess.Popen([updater_exe, updater_path, download_url])
                else:
                    # Running from source
                    subprocess.Popen([sys.executable, updater_path, download_url])
                sys.exit(0)
                return True 
    return False

def normalize_version(version):
    # Remove leading 'v' or 'V' and split into tuple of ints
    version = version.lstrip('vV')
    return tuple(map(int, (version.split("."))))
