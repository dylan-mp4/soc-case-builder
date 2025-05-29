from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
import os
import json

class SearchCases(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Cases")
        self.resize(800, 600)
        
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )
        layout = QVBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter search term...")
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_cases)
        layout.addWidget(self.search_button)

        self.results_table = QTableWidget(self)
        self.results_table.setColumnCount(6)  # Increase column count to 6
        self.results_table.setHorizontalHeaderLabels(["Tab Name", "Client", "Crux", "Escalation Info", "Close Reason", "File Path"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Allow user to resize columns
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)    # Allow user to resize rows
        self.results_table.setColumnHidden(5, True)  # Hide the file path column
        self.results_table.cellDoubleClicked.connect(self.load_case)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # Enable horizontal scrolling
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)    # Enable vertical scrolling
        layout.addWidget(self.results_table)
        
        for i in range(5):  # Only visible columns
            self.results_table.setColumnWidth(i, 200)

        self.setLayout(layout)

    def search_cases(self):
        search_term = self.search_input.text().lower()
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        case_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]

        results = []
        for case_file in case_files:
            with open(os.path.join(logs_dir, case_file), 'r') as file:
                case_data = json.load(file)
                if any(search_term in str(value).lower() for value in case_data.values()):
                    results.append((case_file, case_data))

        if results:
            # Get all unique keys from the JSON data
            all_keys = set()
            for _, case_data in results:
                all_keys.update(case_data.keys())
            all_keys = list(all_keys)

            self.results_table.setColumnCount(len(all_keys) + 1)  # +1 for the file path column
            self.results_table.setHorizontalHeaderLabels(all_keys + ["File Path"])
            self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            for i in range(len(all_keys)):
                self.results_table.setColumnWidth(i, 200)
            self.results_table.setColumnWidth(len(all_keys), 200)

            self.results_table.setRowCount(len(results))
            for row, (case_file, case_data) in enumerate(results):
                for col, key in enumerate(all_keys):
                    item = QTableWidgetItem(str(case_data.get(key, "")))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.results_table.setItem(row, col, item)
                file_item = QTableWidgetItem(case_file)
                file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.results_table.setItem(row, len(all_keys), file_item)
            self.results_table.setColumnHidden(len(all_keys), True)

            # Enable sorting
            self.results_table.setSortingEnabled(True)

            # Sort by 'timestamp' column if present (descending)
            if 'timestamp' in all_keys:
                timestamp_col = all_keys.index('timestamp')
                self.results_table.sortItems(timestamp_col, Qt.SortOrder.DescendingOrder)
                
    def load_case(self, row, column):
        file_path = self.results_table.item(row, self.results_table.columnCount() - 1).text()  # Get the file path from the last column
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        full_file_path = os.path.join(logs_dir, file_path)
        print(f"Retrieving file from path: {full_file_path}")  # Debug print
        self.parent().load_case(full_file_path)
        self.accept()