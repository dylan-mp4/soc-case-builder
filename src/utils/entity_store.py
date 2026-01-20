import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

from .api_requests import (
    get_abuse_info,
    get_domain_info,
    get_hash_info,
    get_url_info,
)

_DB_NAME = "entity_cache.sqlite3"


def _src_dir() -> str:
    return os.path.dirname(os.path.dirname(__file__))


def _db_path() -> str:
    # Place DB alongside src/settings.json for portability
    return os.path.join(_src_dir(), _DB_NAME)


def _settings_path() -> str:
    """Return the preferred settings path.

    Priority:
    1) New Flet config at src/ui_flet/config/settings.json
    2) Legacy settings.json at src/
    """
    flet_path = os.path.join(_src_dir(), "ui_flet", "config", "settings.json")
    legacy_path = os.path.join(_src_dir(), "settings.json")
    return flet_path if os.path.exists(flet_path) else legacy_path


def _load_settings() -> Dict[str, Any]:
    try:
        with open(_settings_path(), "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _get_ttl_days(entity_type: str) -> int:
    # Defaults if not specified in settings
    defaults = {
        "ip": 90,
        "domain": 7,
        "hash": 14,
        "url": 3,
        "user_profile": 30,
    }
    settings = _load_settings()
    group = settings.get("entity_ttl_days", {})
    return int(group.get(entity_type, defaults.get(entity_type, 7)))


def _ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            enriched_text TEXT,
            raw_json TEXT,
            source TEXT,
            last_updated INTEGER NOT NULL,
            UNIQUE(type, value)
        )
        """
    )
    # Grouping tables for users and associations
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            username TEXT PRIMARY KEY,
            role TEXT,
            department TEXT,
            last_updated INTEGER NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_ips (
            username TEXT NOT NULL,
            ip TEXT NOT NULL,
            UNIQUE(username, ip)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_hosts (
            username TEXT NOT NULL,
            host TEXT NOT NULL,
            UNIQUE(username, host)
        )
        """
    )
    conn.commit()


class _DB:
    def __init__(self):
        os.makedirs(_src_dir(), exist_ok=True)
        self.path = _db_path()
        self._conn = sqlite3.connect(self.path)
        _ensure_schema(self._conn)

    @property
    def conn(self) -> sqlite3.Connection:
        return self._conn

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


_db_singleton: Optional[_DB] = None


def _db() -> _DB:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = _DB()
    return _db_singleton


def _now() -> int:
    return int(time.time())


def _is_stale(last_updated: int, ttl_days: int) -> bool:
    age = _now() - int(last_updated)
    return age > ttl_days * 86400


def upsert_entity(entity_type: str, value: str, enriched_text: str, raw_json: Optional[str] = None, source: Optional[str] = None) -> None:
    conn = _db().conn
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO entities(type, value, enriched_text, raw_json, source, last_updated)
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(type, value)
        DO UPDATE SET enriched_text=excluded.enriched_text, raw_json=excluded.raw_json, source=excluded.source, last_updated=excluded.last_updated
        """,
        (entity_type, value, enriched_text, raw_json, source, _now()),
    )
    conn.commit()


def get_entity(entity_type: str, value: str) -> Optional[Tuple[str, int]]:
    """Return (enriched_text, last_updated) if exists."""
    conn = _db().conn
    cur = conn.cursor()
    cur.execute(
        "SELECT enriched_text, last_updated FROM entities WHERE type=? AND value=?",
        (entity_type, value),
    )
    row = cur.fetchone()
    if row:
        return row[0], int(row[1])
    return None


# Public helpers used by UI code

def get_or_enrich_ip(ip: str, api_key: Optional[str], return_status: bool = False):
    entity_type = "ip"
    ttl = _get_ttl_days(entity_type)
    cached = get_entity(entity_type, ip)
    if cached and not _is_stale(cached[1], ttl):
        return (cached[0], "cached") if return_status else cached[0]
    # Fetch fresh
    if not api_key:
        # If no API key, return cached if any or fallback text
        return ((cached[0], "cached") if cached else ("No API key configured", "error")) if return_status else (cached[0] if cached else "No API key configured")
    raw = get_abuse_info(ip, api_key)
    upsert_entity(entity_type, ip, raw, source="abuseipdb")
    return (raw, "refreshed") if return_status else raw


def get_or_enrich_domain(domain: str, return_status: bool = False):
    entity_type = "domain"
    ttl = _get_ttl_days(entity_type)
    cached = get_entity(entity_type, domain)
    if cached and not _is_stale(cached[1], ttl):
        return (cached[0], "cached") if return_status else cached[0]
    raw = get_domain_info(domain)
    upsert_entity(entity_type, domain, raw, source="networkcalc")
    return (raw, "refreshed") if return_status else raw


def get_or_enrich_hash(hash_value: str, api_key: Optional[str], return_status: bool = False):
    entity_type = "hash"
    ttl = _get_ttl_days(entity_type)
    cached = get_entity(entity_type, hash_value)
    if cached and not _is_stale(cached[1], ttl):
        return (cached[0], "cached") if return_status else cached[0]
    if not api_key:
        return ((cached[0], "cached") if cached else ("No API key configured", "error")) if return_status else (cached[0] if cached else "No API key configured")
    raw = get_hash_info(hash_value, api_key)
    upsert_entity(entity_type, hash_value, raw, source="virustotal")
    return (raw, "refreshed") if return_status else raw


def get_or_enrich_url(url: str, api_key: Optional[str], return_status: bool = False):
    entity_type = "url"
    ttl = _get_ttl_days(entity_type)
    cached = get_entity(entity_type, url)
    if cached and not _is_stale(cached[1], ttl):
        return (cached[0], "cached") if return_status else cached[0]
    if not api_key:
        return ((cached[0], "cached") if cached else ("No API key configured", "error")) if return_status else (cached[0] if cached else "No API key configured")
    raw = get_url_info(url, api_key)
    upsert_entity(entity_type, url, raw, source="urlscan")
    return (raw, "refreshed") if return_status else raw


# User grouping functions

def upsert_user_profile(username: str, role: Optional[str] = None, department: Optional[str] = None) -> None:
    cur = _db().conn.cursor()
    cur.execute(
        """
        INSERT INTO user_profiles(username, role, department, last_updated)
        VALUES(?,?,?,?)
        ON CONFLICT(username) DO UPDATE SET role=excluded.role, department=excluded.department, last_updated=excluded.last_updated
        """,
        (username, role, department, _now()),
    )
    _db().conn.commit()


def add_user_associations(username: str, ips: Optional[List[str]] = None, hosts: Optional[List[str]] = None) -> None:
    ips = ips or []
    hosts = hosts or []
    cur = _db().conn.cursor()
    for ip in ips:
        try:
            cur.execute("INSERT OR IGNORE INTO user_ips(username, ip) VALUES(?,?)", (username, ip))
        except Exception:
            pass
    for host in hosts:
        try:
            cur.execute("INSERT OR IGNORE INTO user_hosts(username, host) VALUES(?,?)", (username, host))
        except Exception:
            pass
    _db().conn.commit()


def get_user_profile(username: str) -> Dict[str, Any]:
    cur = _db().conn.cursor()
    cur.execute("SELECT role, department, last_updated FROM user_profiles WHERE username=?", (username,))
    row = cur.fetchone()
    role, department, updated = (row[0], row[1], row[2]) if row else (None, None, None)
    cur.execute("SELECT ip FROM user_ips WHERE username=?", (username,))
    ips = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT host FROM user_hosts WHERE username=?", (username,))
    hosts = [r[0] for r in cur.fetchall()]
    return {
        "username": username,
        "role": role,
        "department": department,
        "ips": ips,
        "hosts": hosts,
        "last_updated": updated,
    }


def upsert_full_user_profile(username: str, role: Optional[str] = None, department: Optional[str] = None, ips: Optional[List[str]] = None, hosts: Optional[List[str]] = None) -> None:
    """Convenience helper to save user profile and associations in one call."""
    upsert_user_profile(username, role=role, department=department)
    add_user_associations(username, ips=ips, hosts=hosts)
