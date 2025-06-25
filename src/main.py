import json
import sys
import os
from PyQt6.QtWidgets import QApplication
# from PyQt6.QtGui import QFont
from ui.case_builder_window import CaseBuilderWindow

# Dynamically add the root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(root_dir)

from resources.get_version import get_version
from utils.check_updates import prompt_and_update_if_needed

def apply_saved_theme(app):
    settings_path = os.path.join(current_dir, 'settings.json')
    themes_dir = os.path.join(current_dir, 'assets', 'themes')
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            theme = settings.get("theme")
            if theme:
                theme_path = os.path.join(themes_dir, theme)
                print(f"Trying to load theme from: {theme_path}")
                if os.path.isfile(theme_path):
                    with open(theme_path, "r", encoding="utf-8") as tf:
                        qss = tf.read()
                        app.setStyleSheet(qss)
                        print("Theme applied!")
                else:
                    print("Theme file does not exist:", theme_path)
            else:
                print("No theme set in settings.json")
    except Exception as e:
        print("Error applying theme. Using default theme.", e)

def main():
    app = QApplication(sys.argv)
    # app.setFont(QFont("Segoe UI", 10))
    apply_saved_theme(app)
    # Check for updates and prompt if needed
    prompt_and_update_if_needed(get_version())
    window = CaseBuilderWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()