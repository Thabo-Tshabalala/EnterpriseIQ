# creational_patterns/singleton.py
# Pattern: Singleton
# Use Case: AuditLogger — exactly one audit logger must exist system-wide.
# Justification: The audit log must be written to a single PostgreSQL table.
# Multiple AuditLogger instances could cause race conditions, duplicate entries,
# or inconsistent connection pool management. The Singleton guarantees one
# shared instance handles all audit writes across all query sessions.
# Thread-safe implementation using a lock for concurrent environments.

import threading
from datetime import datetime
from typing import List
from src.models import AuditLogEntry


class AuditLogger:
    """
    Singleton AuditLogger — one instance manages all audit log writes.
    Thread-safe: uses a lock to prevent race conditions during instantiation.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking — prevents race condition
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialise()
        return cls._instance

    def _initialise(self) -> None:
        """Called once when the singleton is first created."""
        self._log: List[AuditLogEntry] = []
        self._write_count = 0
        print("[AuditLogger] Singleton instance created.")

    def write(self, entry: AuditLogEntry) -> None:
        """Writes an audit log entry. Thread-safe."""
        with self._lock:
            self._log.append(entry)
            self._write_count += 1
            print(f"[AuditLogger] Entry {entry.log_id} written. "
                  f"Total entries: {self._write_count}")

    def get_all_entries(self) -> List[AuditLogEntry]:
        return list(self._log)

    def get_write_count(self) -> int:
        return self._write_count

    def export_csv(self) -> str:
        lines = ["log_id,user_id,query_id,namespace,created_at,pii_detected"]
        for entry in self._log:
            lines.append(entry.export())
        return "\n".join(lines)

    @classmethod
    def reset_for_testing(cls) -> None:
        """
        Resets the singleton instance.
        ONLY for use in unit tests — never call in production.
        """
        with cls._lock:
            cls._instance = None
