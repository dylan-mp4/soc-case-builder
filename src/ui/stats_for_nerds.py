import os
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGroupBox, QFormLayout

class StatsForNerds(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stats for Nerds")
        main_layout = QVBoxLayout()

        stats = self.calculate_stats()

        # Group 1: Case Counts
        count_group = QGroupBox("Case Counts")
        count_layout = QFormLayout()
        count_layout.addRow("Cases (last 24h):", QLabel(str(stats["Cases (last 24h)"])))
        count_layout.addRow("Cases (last 7d):", QLabel(str(stats["Cases (last 7d)"])))
        count_layout.addRow("Cases (last 30d):", QLabel(str(stats["Cases (last 30d)"])))
        count_layout.addRow("Cases (all time):", QLabel(str(stats["Cases (all time)"])))
        count_group.setLayout(count_layout)
        main_layout.addWidget(count_group)

        # Group 2: Averages
        avg_group = QGroupBox("Averages")
        avg_layout = QFormLayout()
        avg_layout.addRow("Avg cases/24h (days >= 5 cases):", QLabel(str(stats["Avg cases/24h (days >= 5 cases)"])))
        avg_group.setLayout(avg_layout)
        main_layout.addWidget(avg_group)

        self.setLayout(main_layout)

    def calculate_stats(self):
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        now = datetime.now()
        stats = {
            "Cases (last 24h)": 0,
            "Cases (last 7d)": 0,
            "Cases (last 30d)": 0,
            "Cases (all time)": 0,
            "Avg cases/24h (days >= 5 cases)": 0
        }
        daily_counts = {}
        if not os.path.exists(logs_dir):
            return stats

        for fname in os.listdir(logs_dir):
            if fname.endswith('.json'):
                try:
                    with open(os.path.join(logs_dir, fname), 'r') as f:
                        data = json.load(f)
                        ts = data.get("timestamp")
                        if not ts:
                            continue
                        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                        day = dt.date()
                        daily_counts[day] = daily_counts.get(day, 0) + 1
                        delta = now - dt
                        if delta <= timedelta(days=1):
                            stats["Cases (last 24h)"] += 1
                        if delta <= timedelta(days=7):
                            stats["Cases (last 7d)"] += 1
                        if delta <= timedelta(days=30):
                            stats["Cases (last 30d)"] += 1
                        stats["Cases (all time)"] += 1
                except Exception:
                    continue

        # Calculate average per 24h, excluding days with < 5 cases
        valid_days = [count for count in daily_counts.values() if count >= 5]
        if valid_days:
            stats["Avg cases/24h"] = round(sum(valid_days) / len(valid_days), 2)
        return stats