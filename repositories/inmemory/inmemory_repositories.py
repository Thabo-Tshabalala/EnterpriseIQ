# All implementations are fully interchangeable with future DB-backed versions.

from typing import List, Optional
from repositories.interfaces import (
    UserAccountRepository, DocumentRepository,
    VectorEmbeddingRepository, AuditLogRepository,
    NamespaceRepository, QuerySessionRepository
)
from src.models import (
    UserAccount, Document, VectorEmbedding,
    AuditLogEntry, Namespace, QuerySession,
    Role, AccountStatus, DocumentStatus, NamespaceId
)


class InMemoryUserAccountRepository(UserAccountRepository):
    """In-memory HashMap implementation for UserAccount. Keyed by user_id."""

    def __init__(self):
        self._storage: dict = {}

    def save(self, entity: UserAccount) -> None:
        self._storage[entity.user_id] = entity

    def find_by_id(self, entity_id: str) -> Optional[UserAccount]:
        return self._storage.get(entity_id)

    def find_all(self) -> List[UserAccount]:
        return list(self._storage.values())

    def delete(self, entity_id: str) -> None:
        self._storage.pop(entity_id, None)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)

    def find_by_email(self, email: str) -> Optional[UserAccount]:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None

    def find_by_role(self, role: Role) -> List[UserAccount]:
        return [u for u in self._storage.values() if u.role == role]

    def find_by_status(self, status: AccountStatus) -> List[UserAccount]:
        return [u for u in self._storage.values() if u.status == status]


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory HashMap implementation for Document. Keyed by document_id."""

    def __init__(self):
        self._storage: dict = {}

    def save(self, entity: Document) -> None:
        self._storage[entity.document_id] = entity

    def find_by_id(self, entity_id: str) -> Optional[Document]:
        return self._storage.get(entity_id)

    def find_all(self) -> List[Document]:
        return list(self._storage.values())

    def delete(self, entity_id: str) -> None:
        self._storage.pop(entity_id, None)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)

    def find_by_namespace(self, namespace: NamespaceId) -> List[Document]:
        return [d for d in self._storage.values() if d.namespace == namespace]

    def find_by_status(self, status: DocumentStatus) -> List[Document]:
        return [d for d in self._storage.values() if d.status == status]

    def find_by_uploader(self, user_id: str) -> List[Document]:
        return [d for d in self._storage.values() if d.uploaded_by == user_id]

    def find_flagged(self) -> List[Document]:
        return [d for d in self._storage.values() if d.status == DocumentStatus.FLAGGED]


class InMemoryVectorEmbeddingRepository(VectorEmbeddingRepository):
    """In-memory HashMap implementation for VectorEmbedding. Keyed by embedding_id."""

    def __init__(self):
        self._storage: dict = {}

    def save(self, entity: VectorEmbedding) -> None:
        self._storage[entity.embedding_id] = entity

    def find_by_id(self, entity_id: str) -> Optional[VectorEmbedding]:
        return self._storage.get(entity_id)

    def find_all(self) -> List[VectorEmbedding]:
        return list(self._storage.values())

    def delete(self, entity_id: str) -> None:
        self._storage.pop(entity_id, None)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)

    def find_by_document(self, document_id: str) -> List[VectorEmbedding]:
        return [e for e in self._storage.values() if e.document_id == document_id]

    def find_by_namespace(self, namespace: NamespaceId) -> List[VectorEmbedding]:
        return [e for e in self._storage.values() if e.namespace == namespace]

    def delete_by_document(self, document_id: str) -> None:
        keys = [k for k, v in self._storage.items() if v.document_id == document_id]
        for key in keys:
            del self._storage[key]

    def find_stale(self) -> List[VectorEmbedding]:
        return [e for e in self._storage.values() if e.is_stale]


class InMemoryAuditLogRepository(AuditLogRepository):
    """
    In-memory HashMap implementation for AuditLogEntry. Keyed by log_id.
    Entries are IMMUTABLE — save() raises if trying to overwrite an existing entry.
    """

    def __init__(self):
        self._storage: dict = {}

    def save(self, entity: AuditLogEntry) -> None:
        if entity.log_id in self._storage:
            raise ValueError(
                f"Audit entry {entity.log_id} already exists. "
                "Audit log entries are immutable and cannot be updated."
            )
        self._storage[entity.log_id] = entity

    def find_by_id(self, entity_id: str) -> Optional[AuditLogEntry]:
        return self._storage.get(entity_id)

    def find_all(self) -> List[AuditLogEntry]:
        return list(self._storage.values())

    def delete(self, entity_id: str) -> None:
        # Deletion only permitted by the retention policy process
        self._storage.pop(entity_id, None)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)

    def find_by_user(self, user_id: str) -> List[AuditLogEntry]:
        return [e for e in self._storage.values() if e.user_id == user_id]

    def find_by_namespace(self, namespace: NamespaceId) -> List[AuditLogEntry]:
        return [e for e in self._storage.values() if e.namespace == namespace]

    def find_expired(self) -> List[AuditLogEntry]:
        return [e for e in self._storage.values() if e.is_retention_expired()]


class InMemoryNamespaceRepository(NamespaceRepository):
    """In-memory HashMap implementation for Namespace. Keyed by NamespaceId enum."""

    def __init__(self):
        self._storage: dict = {}

    def save(self, entity: Namespace) -> None:
        self._storage[entity.namespace_id] = entity

    def find_by_id(self, entity_id: NamespaceId) -> Optional[Namespace]:
        return self._storage.get(entity_id)

    def find_all(self) -> List[Namespace]:
        return list(self._storage.values())

    def delete(self, entity_id: NamespaceId) -> None:
        self._storage.pop(entity_id, None)

    def exists(self, entity_id: NamespaceId) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)

    def find_queryable(self) -> List[Namespace]:
        return [n for n in self._storage.values() if n.is_queryable()]


class InMemoryQuerySessionRepository(QuerySessionRepository):
    """In-memory HashMap implementation for QuerySession. Keyed by query_id."""

    def __init__(self):
        self._storage: dict = {}

    def save(self, entity: QuerySession) -> None:
        self._storage[entity.query_id] = entity

    def find_by_id(self, entity_id: str) -> Optional[QuerySession]:
        return self._storage.get(entity_id)

    def find_all(self) -> List[QuerySession]:
        return list(self._storage.values())

    def delete(self, entity_id: str) -> None:
        self._storage.pop(entity_id, None)

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)

    def find_by_user(self, user_id: str) -> List[QuerySession]:
        return [q for q in self._storage.values() if q.user_id == user_id]

    def find_by_namespace(self, namespace: NamespaceId) -> List[QuerySession]:
        return [q for q in self._storage.values() if q._namespace == namespace]
