"""
Centralized application state management for SOC Case Builder.
All app-level state is managed through this AppState class.
"""

import json
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from src.ui_flet.utils.config_manager import load_settings, save_settings, update_settings


class AppState:
    """
    Centralized state manager for the entire application.
    Maintains settings, cases, and entity cache references.
    """

    def __init__(self):
        """Initialize app state."""
        self.settings: Dict[str, Any] = load_settings()
        self.cases: Dict[str, Dict[str, Any]] = {}  # {case_id: case_data}
        self.current_case_id: Optional[str] = None
        self.entity_cache: Any = None  # Reference to EntityStore instance
        self.queries: List[Dict[str, Any]] = []  # Query templates
        self.subscribers: Dict[str, List[Callable]] = {
            "settings_changed": [],
            "case_added": [],
            "case_updated": [],
            "case_deleted": [],
            "case_selected": [],
            "queries_loaded": [],
        }
        self._load_queries()

    # ==================== Settings Management ====================

    def load_settings(self) -> Dict[str, Any]:
        """Reload settings from file."""
        self.settings = load_settings()
        return self.settings

    def save_settings(self) -> bool:
        """Save current settings to file."""
        result = save_settings(self.settings)
        self._notify("settings_changed", self.settings)
        return result

    def update_settings(self, updates: Dict[str, Any]) -> bool:
        """Update multiple settings and save."""
        self.settings.update(updates)
        result = save_settings(self.settings)
        self._notify("settings_changed", self.settings)
        return result

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting."""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting and save."""
        self.settings[key] = value
        result = save_settings(self.settings)
        self._notify("settings_changed", self.settings)
        return result

    # ==================== Case Management ====================

    def create_case(self, case_name: str = None) -> str:
        """
        Create a new case.
        Returns case_id.
        """
        if case_name is None:
            case_name = f"Case {len(self.cases) + 1}"

        case_id = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cases[case_id] = {
            "id": case_id,
            "name": case_name,
            "fields": {},  # {field_label: [field_values]}
            "close_reason": None,
            "escalation_reason": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._notify("case_added", case_id)
        return case_id

    def update_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Update a case with new data."""
        if case_id not in self.cases:
            return False

        self.cases[case_id].update(updates)
        self.cases[case_id]["updated_at"] = datetime.now().isoformat()
        self._notify("case_updated", case_id)
        return True

    def delete_case(self, case_id: str) -> bool:
        """Delete a case."""
        if case_id in self.cases:
            del self.cases[case_id]
            if self.current_case_id == case_id:
                self.current_case_id = None
            self._notify("case_deleted", case_id)
            return True
        return False

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case data."""
        return self.cases.get(case_id)

    def get_all_cases(self) -> Dict[str, Dict[str, Any]]:
        """Get all cases."""
        return self.cases

    def select_case(self, case_id: str) -> bool:
        """Select the current active case."""
        if case_id in self.cases:
            self.current_case_id = case_id
            self._notify("case_selected", case_id)
            return True
        return False

    def get_current_case(self) -> Optional[Dict[str, Any]]:
        """Get currently selected case."""
        if self.current_case_id:
            return self.cases.get(self.current_case_id)
        return None

    # ==================== Case Field Management ====================

    def add_field_to_case(
        self, case_id: str, field_label: str, field_value: str = ""
    ) -> bool:
        """Add a field to a case."""
        case = self.get_case(case_id)
        if case is None:
            return False

        if field_label not in case["fields"]:
            case["fields"][field_label] = []

        case["fields"][field_label].append(field_value)
        self.update_case(case_id, case)
        return True

    def remove_field_from_case(self, case_id: str, field_label: str, index: int) -> bool:
        """Remove a specific field value from a case."""
        case = self.get_case(case_id)
        if case is None or field_label not in case["fields"]:
            return False

        if 0 <= index < len(case["fields"][field_label]):
            case["fields"][field_label].pop(index)
            if not case["fields"][field_label]:
                del case["fields"][field_label]
            self.update_case(case_id, case)
            return True
        return False

    def update_field_in_case(
        self, case_id: str, field_label: str, index: int, value: str
    ) -> bool:
        """Update a specific field value in a case."""
        case = self.get_case(case_id)
        if case is None or field_label not in case["fields"]:
            return False

        if 0 <= index < len(case["fields"][field_label]):
            case["fields"][field_label][index] = value
            self.update_case(case_id, case)
            return True
        return False

    def get_case_fields(self, case_id: str) -> Dict[str, List[str]]:
        """Get all fields for a case."""
        case = self.get_case(case_id)
        return case.get("fields", {}) if case else {}

    def set_case_route(self, case_id: str, route_type: str, reason: str = "") -> bool:
        """Set whether case is closed or escalated."""
        case = self.get_case(case_id)
        if case is None:
            return False

        if route_type == "close":
            case["close_reason"] = reason
            case["escalation_reason"] = None
        elif route_type == "escalate":
            case["escalation_reason"] = reason
            case["close_reason"] = None
        else:
            return False

        self.update_case(case_id, case)
        return True

    # ==================== Event Subscription ====================

    def subscribe(self, event: str, callback: Callable) -> bool:
        """Subscribe to an event."""
        if event in self.subscribers:
            self.subscribers[event].append(callback)
            return True
        return False

    def unsubscribe(self, event: str, callback: Callable) -> bool:
        """Unsubscribe from an event."""
        if event in self.subscribers and callback in self.subscribers[event]:
            self.subscribers[event].remove(callback)
            return True
        return False

    def _notify(self, event: str, data: Any = None) -> None:
        """Notify all subscribers of an event."""
        if event in self.subscribers:
            for callback in self.subscribers[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")

    # ==================== Serialization ====================

    def export_case_to_json(self, case_id: str) -> Optional[str]:
        """Export case to JSON string."""
        case = self.get_case(case_id)
        if case is None:
            return None
        return json.dumps(case, indent=2, ensure_ascii=False)

    def import_case_from_dict(self, case_dict: Dict[str, Any]) -> Optional[str]:
        """Import a case from dictionary. Returns case_id."""
        if "name" not in case_dict:
            return None

        case_id = self.create_case(case_dict.get("name"))
        self.cases[case_id].update(case_dict)
        return case_id

    # ==================== Query Management ====================

    def _load_queries(self) -> None:
        """Load queries from queries.json file."""
        try:
            from pathlib import Path
            queries_file = Path(__file__).parent.parent / "queries.json"
            if queries_file.exists():
                with open(queries_file, "r", encoding="utf-8") as f:
                    self.queries = json.load(f)
                self._notify("queries_loaded", self.queries)
        except Exception as e:
            print(f"Error loading queries: {e}")
            self.queries = []

    def get_queries(self) -> List[Dict[str, Any]]:
        """Get all queries."""
        return self.queries

    def get_queries_for_entity(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get queries applicable to an entity type."""
        entity_type = entity_type.upper()
        return [
            q for q in self.queries
            if entity_type in [e.upper() for e in q.get("entity_types", [])]
        ]

    def apply_query_template(self, query: Dict[str, Any], entity_value: str) -> str:
        """Apply entity value to query template."""
        template = query.get("template", "")
        return template.replace("{{Entity}}", entity_value)
