from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QLabel, QMessageBox
import csv
import json
import re

class BulkAddEntitiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Add Entities")
        self.resize(500, 400)
        layout = QVBoxLayout(self)

        self.info_label = QLabel("Paste entities (CSV, JSON, or raw text). Supported delimiters: comma, space, newline.")
        layout.addWidget(self.info_label)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.load_file_btn = QPushButton("Import from File")
        self.load_file_btn.clicked.connect(self.load_file)
        layout.addWidget(self.load_file_btn)

        self.add_btn = QPushButton("Add Entities")
        self.add_btn.clicked.connect(self.accept)
        layout.addWidget(self.add_btn)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_edit.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file: {e}")

    def get_entities(self):
        text = self.text_edit.toPlainText()
        # Try JSON
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                data = [data]
            if isinstance(data, list):
                # Flatten dicts to key-value pairs
                entities = []
                for item in data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            entities.append((k, v))
                    else:
                        entities.append(("", str(item)))
                return entities
        except Exception:
            pass

        # Try CSV
        try:
            reader = csv.reader(text.splitlines())
            entities = []
            for row in reader:
                if len(row) == 2:
                    entities.append((row[0], row[1]))
                elif len(row) == 1:
                    entities.append(("", row[0]))
            if entities:
                return entities
        except Exception:
            pass

        # Raw text: split by comma, space, or newline
        raw = re.split(r'[\s,]+', text)
        entities = [("", item) for item in raw if item.strip()]
        return entities

    def detect_entity_type(self, value):
        # Simple regex-based detection (expand as needed)
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", value):
            return "IP"
        elif re.match(r"^(?:[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})$", value):
            return "Hash"
        elif re.match(r"^(https?://|www\.)", value):
            return "URL"
        elif re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", value):
            return "Email"
        elif re.match(r"^[\w\.-]+\.[a-zA-Z]{2,}$", value):
            return "Domain"
        else:
            return "Other"