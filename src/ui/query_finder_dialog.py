import os
import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QTextEdit

QUERY_FILE = "queries.json"

class QueryFinderDialog(QDialog):
    def __init__(self, entity_type, entity_value, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Query Finder - {entity_type}")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        self.entity_value = entity_value

        layout.addWidget(QLabel(f"Entity: {entity_type} = {entity_value}"))

        # Load queries from file if available, else use empty list
        self.queries = []
        if os.path.exists(QUERY_FILE):
            try:
                with open(QUERY_FILE, "r", encoding="utf-8") as f:
                    self.queries = json.load(f)
            except Exception:
                self.queries = []
        # Filter queries by entity_type
        self.relevant_queries = [q for q in self.queries if entity_type in q.get("entity_types", [])]

        self.list_widget = QListWidget()
        for q in self.relevant_queries:
            self.list_widget.addItem(q["name"])
        layout.addWidget(self.list_widget)

        self.query_text = QTextEdit()
        self.query_text.setReadOnly(True)
        layout.addWidget(self.query_text)

        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copy Query")
        self.copy_btn.clicked.connect(self.copy_query)
        btn_layout.addWidget(self.copy_btn)
        layout.addLayout(btn_layout)

        self.list_widget.currentRowChanged.connect(self.show_query)

        if self.relevant_queries:
            self.list_widget.setCurrentRow(0)
            self.show_query(0)

    def show_query(self, idx):
        if 0 <= idx < len(self.relevant_queries):
            template = self.relevant_queries[idx].get("template", "")
            query = template.replace("{{Entity}}", f'"{self.entity_value}"')
            self.query_text.setPlainText(query)
        else:
            self.query_text.clear()

    def copy_query(self):
        query = self.query_text.toPlainText()
        if query:
            from PyQt6.QtGui import QGuiApplication
            QGuiApplication.clipboard().setText(query)