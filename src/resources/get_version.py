import re
import requests
import webbrowser
from PyQt6.QtWidgets import QMessageBox
from packaging.version import Version, InvalidVersion

GITHUB_TAGS_URL = "https://api.github.com/repos/dylan-mp4/soc-case-builder/tags"
GITHUB_RELEASES_PAGE = "https://github.com/dylan-mp4/soc-case-builder/releases"

def get_version():
    with open('resources/version.py', 'r') as file:
        content = file.read()
        version_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", content)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def check_for_updates(current_version):
    try:
        # Fetch the latest tags from the GitHub API
        response = requests.get(GITHUB_TAGS_URL, timeout=10)
        response.raise_for_status()
        tags = response.json()

        if tags:
            latest_version = tags[0]['name'].lstrip('v')  # Remove 'v' prefix if present
            try:
                # Compare versions using packaging.version
                if Version(latest_version) > Version(current_version):
                    return latest_version
            except InvalidVersion:
                print(f"Invalid version format: {latest_version}")
    except requests.RequestException as e:
        print(f"Error checking for updates: {e}")
    return None

def prompt_update_dialog(parent, current_version, latest_version):
    # Show a dialog asking the user if they want to update
    message = (
        f"A new version of SOC Case Builder is available!\n\n"
        f"Current version: {current_version}\n"
        f"Latest version: {latest_version}\n\n"
        f"Would you like to visit the GitHub releases page to download the update?"
    )
    reply = QMessageBox.question(
        parent,
        "Update Available",
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        webbrowser.open(GITHUB_RELEASES_PAGE)