from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class PopOutTextEdit(QDialog):
    def __init__(self, main_text_edit):
        super().__init__(None)  # Set parent to None to make it independent
        self.setWindowTitle("Pop-Out Text Editor")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)

        self.main_text_edit = main_text_edit

        # Layout for the pop-out dialog
        layout = QVBoxLayout(self)

        # Text edit in the pop-out dialog
        self.pop_out_text_edit = QTextEdit(self)
        self.pop_out_text_edit.setPlainText(self.main_text_edit.toPlainText())
        self.pop_out_text_edit.textChanged.connect(self.sync_to_main)
        layout.addWidget(self.pop_out_text_edit)

        # Close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def sync_to_main(self):
        # Sync text from the pop-out dialog to the main text edit
        self.main_text_edit.setPlainText(self.pop_out_text_edit.toPlainText())

    def sync_from_main(self):
        # Sync text from the main text edit to the pop-out dialog
        self.pop_out_text_edit.setPlainText(self.main_text_edit.toPlainText())

class PopOutTextBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Main text edit
        self.text_edit = QTextEdit(self)
        self.layout().addWidget(self.text_edit)

        # Pop-out button
        self.pop_out_button = QPushButton(self)
        self.pop_out_button.setFixedSize(24, 24)
        self.pop_out_button.setIcon(QIcon("assets/popout_icon.svg"))
        self.pop_out_button.setStyleSheet("border: none;")  # Remove button border
        self.pop_out_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pop_out_button.clicked.connect(self.open_pop_out)

        # Add the button to the top-right corner
        button_layout = QHBoxLayout(self.text_edit)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()
        button_layout.addWidget(self.pop_out_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def open_pop_out(self):
        # Open the pop-out dialog
        dialog = PopOutTextEdit(self.text_edit)
        dialog.exec()

    def toPlainText(self):
        return self.text_edit.toPlainText()

    def setPlainText(self, text):
        self.text_edit.setPlainText(text)