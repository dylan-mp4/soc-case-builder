import requests
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

def launch_updater(download_url):
    if getattr(sys, 'frozen', False):
        # Bundled: updater.exe is next to soc_case_builder.exe
        updater_exe = os.path.join(os.path.dirname(sys.executable), 'updater.exe')
        subprocess.Popen([updater_exe, download_url])
    else:
        # Source: run updater.py with python
        updater_path = os.path.join(os.path.dirname(__file__), "updater.py")
        subprocess.Popen([sys.executable, updater_path, download_url])

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
                launch_updater(download_url)
                sys.exit(0)
                return True
    return False

def normalize_version(version):
    # Remove leading 'v' or 'V' and split into tuple of ints
    version = version.lstrip('vV')
    return tuple(map(int, (version.split("."))))