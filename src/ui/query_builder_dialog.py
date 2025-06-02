import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QListWidget, QHBoxLayout,
    QLineEdit, QMessageBox, QListWidgetItem, QComboBox, QCheckBox, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt

QUERY_FILE = "queries.json"
ENTITY_TYPES = ["IP", "Domain", "Username", "Host", "URL", "Hash", "Role", "Location"]  # Extend as needed

class QueryBuilderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Query Builder")
        self.setMinimumWidth(700)
        layout = QVBoxLayout(self)

        # Query List
        self.query_list = QListWidget()
        self.query_list.currentRowChanged.connect(self.load_query)
        layout.addWidget(QLabel("Saved Queries:"))
        layout.addWidget(self.query_list)

        # Query Meta
        meta_widget = QWidget()
        meta_layout = QGridLayout(meta_widget)
        meta_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_edit = QLineEdit()
        meta_layout.addWidget(self.name_edit, 0, 1)

        meta_layout.addWidget(QLabel("Entities:"), 1, 0)
        self.entity_checks = []
        entity_widget = QWidget()
        entity_layout = QHBoxLayout(entity_widget)
        for ent in ENTITY_TYPES:
            cb = QCheckBox(ent)
            entity_layout.addWidget(cb)
            self.entity_checks.append(cb)
        meta_layout.addWidget(entity_widget, 1, 1)
        layout.addWidget(meta_widget)

        # Query Editor
        layout.addWidget(QLabel("Query Template:"))
        self.query_editor = QTextEdit()
        layout.addWidget(self.query_editor)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("New")
        self.add_btn.clicked.connect(self.add_query)
        btn_layout.addWidget(self.add_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_query)
        btn_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_query)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        # Load queries from file
        self.queries = []
        self.load_queries()

    def load_queries(self):
        self.queries = []
        self.query_list.clear()
        if os.path.exists(QUERY_FILE):
            with open(QUERY_FILE, "r", encoding="utf-8") as f:
                try:
                    self.queries = json.load(f)
                except Exception:
                    self.queries = []
        for q in self.queries:
            self.query_list.addItem(q["name"])

    def load_query(self, idx):
        if 0 <= idx < len(self.queries):
            q = self.queries[idx]
            self.name_edit.setText(q.get("name", ""))
            self.query_editor.setPlainText(q.get("template", ""))
            # Set entity checkboxes
            ents = set(q.get("entity_types", []))
            for cb in self.entity_checks:
                cb.setChecked(cb.text() in ents)
        else:
            self.name_edit.clear()
            self.query_editor.clear()
            for cb in self.entity_checks:
                cb.setChecked(False)

    def add_query(self):
        self.name_edit.clear()
        self.query_editor.clear()
        for cb in self.entity_checks:
            cb.setChecked(False)
        self.query_list.clearSelection()

    def save_query(self):
        name = self.name_edit.text().strip()
        template = self.query_editor.toPlainText().strip()
        entities = [cb.text() for cb in self.entity_checks if cb.isChecked()]
        if not name or not template or not entities:
            QMessageBox.warning(self, "Missing Data", "Please provide a name, template, and at least one entity type.")
            return

        idx = self.query_list.currentRow()
        query_data = {"name": name, "template": template, "entity_types": entities}

        # Only update if the selected query's name matches the name field (case-insensitive)
        if 0 <= idx < len(self.queries) and self.queries[idx]["name"].lower() == name.lower():
            self.queries[idx] = query_data
            self.query_list.item(idx).setText(name)
        else:
            # Always add as a new query
            self.queries.append(query_data)
            self.query_list.addItem(name)
            self.query_list.setCurrentRow(self.query_list.count() - 1)

        self.save_queries_to_file()

    def delete_query(self):
        idx = self.query_list.currentRow()
        if 0 <= idx < len(self.queries):
            del self.queries[idx]
            self.query_list.takeItem(idx)
            self.add_query()
            self.save_queries_to_file()

    def save_queries_to_file(self):
        with open(QUERY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.queries, f, indent=2)