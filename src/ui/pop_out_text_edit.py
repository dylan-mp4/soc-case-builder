
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPainter, QPolygon, QColor
from PyQt6.QtCore import Qt, QPoint
from utils.spell_check import SpellTextEdit

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
        self.pop_out_text_edit = SpellTextEdit(self)
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
        self.text_edit = SpellTextEdit(self)  # Use SpellTextEdit here
        self.layout().addWidget(self.text_edit)

        # Pop-out button
        self.pop_out_button = ArrowButton(self)
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

    def clear(self):
        self.text_edit.clear()

class ArrowButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)  # Set the size of the button
        self.setStyleSheet("border: none;")  # Remove button border

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define the arrow points
        arrow = QPolygon([
            QPoint(6, 18),  # Bottom-left
            QPoint(18, 6),  # Top-right
            QPoint(12, 6),  # Top-middle
            QPoint(12, 12),  # Middle
            QPoint(6, 12)   # Bottom-middle
        ])

        # Set the brush and pen
        painter.setBrush(QColor("White"))  # Fill color for the arrow
        painter.setPen(Qt.PenStyle.NoPen)  # No border for the arrow

        # Draw the arrow
        painter.drawPolygon(arrow)
        painter.end()