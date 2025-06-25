import sys
import os
import json
from PyQt6.QtWidgets import QApplication
from ui.case_builder_window import CaseBuilderWindow
from resources.get_version import get_version
from utils.check_updates import prompt_and_update_if_needed

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(root_dir)

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
    apply_saved_theme(app)
    # Check for updates and prompt if needed
    if prompt_and_update_if_needed(get_version()):
        return  # Exit early if update was triggered
    window = CaseBuilderWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()