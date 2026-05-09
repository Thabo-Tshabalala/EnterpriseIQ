# CHOICE: Factory Pattern (over Dependency Injection)
# REASON: EnterpriseIQ's storage backend is determined at startup via a
# configuration value (e.g. environment variable STORAGE_TYPE=MEMORY).
# A Factory encapsulates this selection in one place — no framework needed.
# New backends (DATABASE, FILESYSTEM) are added by registering them here,
# without touching any service or domain class.

from repositories.interfaces import (
    UserAccountRepository, DocumentRepository,
    VectorEmbeddingRepository, AuditLogRepository,
    NamespaceRepository, QuerySessionRepository
)
from repositories.inmemory.inmemory_repositories import (
    InMemoryUserAccountRepository,
    InMemoryDocumentRepository,
    InMemoryVectorEmbeddingRepository,
    InMemoryAuditLogRepository,
    InMemoryNamespaceRepository,
    InMemoryQuerySessionRepository
)
from repositories.filesystem.filesystem_repositories import (
    FileSystemDocumentRepository,
    FileSystemAuditLogRepository
)
from repositories.database.database_repositories import (
    DatabaseUserAccountRepository,
    DatabaseDocumentRepository
)


STORAGE_MEMORY = "MEMORY"
STORAGE_FILESYSTEM = "FILESYSTEM"
STORAGE_DATABASE = "DATABASE"


class RepositoryFactory:
    """
    Factory that returns the correct repository implementation
    based on the configured storage backend.

    Usage:
        factory = RepositoryFactory(storage_type="MEMORY")
        user_repo = factory.get_user_repository()
        doc_repo  = factory.get_document_repository()
    """

    def __init__(self, storage_type: str = STORAGE_MEMORY):
        self._storage_type = storage_type.upper()
        self._validate()

    def _validate(self) -> None:
        valid = {STORAGE_MEMORY, STORAGE_FILESYSTEM, STORAGE_DATABASE}
        if self._storage_type not in valid:
            raise ValueError(
                f"Unknown storage type: '{self._storage_type}'. "
                f"Valid options: {valid}"
            )

    def get_user_repository(self) -> UserAccountRepository:
        if self._storage_type == STORAGE_MEMORY:
            return InMemoryUserAccountRepository()
        if self._storage_type == STORAGE_DATABASE:
            return DatabaseUserAccountRepository()
        raise NotImplementedError(
            f"UserAccountRepository not yet implemented for: {self._storage_type}"
        )

    def get_document_repository(self) -> DocumentRepository:
        if self._storage_type == STORAGE_MEMORY:
            return InMemoryDocumentRepository()
        if self._storage_type == STORAGE_FILESYSTEM:
            return FileSystemDocumentRepository(file_path="data/documents.json")
        if self._storage_type == STORAGE_DATABASE:
            return DatabaseDocumentRepository()
        raise NotImplementedError(
            f"DocumentRepository not yet implemented for: {self._storage_type}"
        )

    def get_embedding_repository(self) -> VectorEmbeddingRepository:
        if self._storage_type == STORAGE_MEMORY:
            return InMemoryVectorEmbeddingRepository()
        raise NotImplementedError(
            f"VectorEmbeddingRepository not yet implemented for: {self._storage_type}"
        )

    def get_audit_log_repository(self) -> AuditLogRepository:
        if self._storage_type == STORAGE_MEMORY:
            return InMemoryAuditLogRepository()
        if self._storage_type == STORAGE_FILESYSTEM:
            return FileSystemAuditLogRepository(file_path="data/audit_log.json")
        raise NotImplementedError(
            f"AuditLogRepository not yet implemented for: {self._storage_type}"
        )

    def get_namespace_repository(self) -> NamespaceRepository:
        if self._storage_type == STORAGE_MEMORY:
            return InMemoryNamespaceRepository()
        raise NotImplementedError(
            f"NamespaceRepository not yet implemented for: {self._storage_type}"
        )

    def get_query_session_repository(self) -> QuerySessionRepository:
        if self._storage_type == STORAGE_MEMORY:
            return InMemoryQuerySessionRepository()
        raise NotImplementedError(
            f"QuerySessionRepository not yet implemented for: {self._storage_type}"
        )
