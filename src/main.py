import sys
import os
from PyQt6.QtWidgets import QApplication

# Dynamically add the root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(root_dir)

from ui.case_builder_window import CaseBuilderWindow

def main():
    app = QApplication(sys.argv)
    window = CaseBuilderWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()