# These stubs show how the repository interfaces would be implemented
# using JSON files as a persistence backend — no code changes needed
# in services or domain classes to swap from MEMORY to FILESYSTEM.
# Only the factory needs to be updated to return these instead.

import json
import os
from typing import List, Optional
from repositories.interfaces import DocumentRepository, AuditLogRepository
from src.models import (
    Document, AuditLogEntry, DocumentStatus, NamespaceId
)


class FileSystemDocumentRepository(DocumentRepository):
    """
    STUB: Filesystem implementation of DocumentRepository.
    Serialises Document objects to a JSON file.
    Full implementation would replace the stub methods below.
    """

    def __init__(self, file_path: str):
        self._file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None

    def _load(self) -> dict:
        """Load all records from the JSON file. Returns empty dict if file missing."""
        if not os.path.exists(self._file_path):
            return {}
        with open(self._file_path, "r") as f:
            return json.load(f)

    def _dump(self, data: dict) -> None:
        """Write all records back to the JSON file."""
        with open(self._file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def save(self, entity: Document) -> None:
        # STUB: Serialises document metadata to JSON (not binary file content)
        data = self._load()
        data[entity.document_id] = {
            "document_id": entity.document_id,
            "file_name": entity.file_name,
            "file_type": entity.file_type,
            "namespace": entity.namespace.value,
            "status": entity.status.value,
            "uploaded_by": entity.uploaded_by,
        }
        self._dump(data)

    def find_by_id(self, entity_id: str) -> Optional[Document]:
        # STUB: Returns None — full implementation would deserialise JSON to Document
        data = self._load()
        return None if entity_id not in data else None  # Deserialisation stub

    def find_all(self) -> List[Document]:
        # STUB: Returns empty list — full implementation would deserialise all records
        return []

    def delete(self, entity_id: str) -> None:
        data = self._load()
        data.pop(entity_id, None)
        self._dump(data)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._load()

    def count(self) -> int:
        return len(self._load())

    def find_by_namespace(self, namespace: NamespaceId) -> List[Document]:
        return []  # STUB

    def find_by_status(self, status: DocumentStatus) -> List[Document]:
        return []  # STUB

    def find_by_uploader(self, user_id: str) -> List[Document]:
        return []  # STUB

    def find_flagged(self) -> List[Document]:
        return []  # STUB


class FileSystemAuditLogRepository(AuditLogRepository):
    """
    STUB: Filesystem implementation of AuditLogRepository.
    Appends AuditLogEntry records to a JSON file.
    """

    def __init__(self, file_path: str):
        self._file_path = file_path

    def _load(self) -> dict:
        if not os.path.exists(self._file_path):
            return {}
        with open(self._file_path, "r") as f:
            return json.load(f)

    def _dump(self, data: dict) -> None:
        with open(self._file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def save(self, entity: AuditLogEntry) -> None:
        data = self._load()
        if entity.log_id in data:
            raise ValueError(f"Audit entry {entity.log_id} is immutable.")
        data[entity.log_id] = {
            "log_id": entity.log_id,
            "user_id": entity.user_id,
            "query_id": entity.query_id,
            "namespace": entity.namespace.value,
            "pii_detected": entity.pii_detected,
            "created_at": str(entity.created_at),
        }
        self._dump(data)

    def find_by_id(self, entity_id: str) -> Optional[AuditLogEntry]:
        return None  # STUB

    def find_all(self) -> List[AuditLogEntry]:
        return []  # STUB

    def delete(self, entity_id: str) -> None:
        data = self._load()
        data.pop(entity_id, None)
        self._dump(data)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._load()

    def count(self) -> int:
        return len(self._load())

    def find_by_user(self, user_id: str) -> List[AuditLogEntry]:
        return []  # STUB

    def find_by_namespace(self, namespace: NamespaceId) -> List[AuditLogEntry]:
        return []  # STUB

    def find_expired(self) -> List[AuditLogEntry]:
        return []  # STUB
