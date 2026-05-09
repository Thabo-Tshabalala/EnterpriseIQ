# Each interface extends the generic Repository with domain-specific query methods.

from abc import abstractmethod
from typing import List, Optional
from repositories.base_repository import Repository
from src.models import (
    UserAccount, Document, VectorEmbedding,
    AuditLogEntry, Namespace, QuerySession,
    Role, AccountStatus, DocumentStatus, NamespaceId
)


class UserAccountRepository(Repository[UserAccount, str]):
    """Repository interface for UserAccount — extends CRUD with user-specific queries."""

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserAccount]:
        """Find a user by their corporate email address."""
        pass

    @abstractmethod
    def find_by_role(self, role: Role) -> List[UserAccount]:
        """Retrieve all users assigned a specific role."""
        pass

    @abstractmethod
    def find_by_status(self, status: AccountStatus) -> List[UserAccount]:
        """Retrieve all users with a given account status."""
        pass


class DocumentRepository(Repository[Document, str]):
    """Repository interface for Document — extends CRUD with document-specific queries."""

    @abstractmethod
    def find_by_namespace(self, namespace: NamespaceId) -> List[Document]:
        """Retrieve all documents in a specific namespace."""
        pass

    @abstractmethod
    def find_by_status(self, status: DocumentStatus) -> List[Document]:
        """Retrieve all documents with a given ingestion status."""
        pass

    @abstractmethod
    def find_by_uploader(self, user_id: str) -> List[Document]:
        """Retrieve all documents uploaded by a specific user."""
        pass

    @abstractmethod
    def find_flagged(self) -> List[Document]:
        """Retrieve all documents flagged for review."""
        pass


class VectorEmbeddingRepository(Repository[VectorEmbedding, str]):
    """Repository interface for VectorEmbedding — extends CRUD with embedding queries."""

    @abstractmethod
    def find_by_document(self, document_id: str) -> List[VectorEmbedding]:
        """Retrieve all embeddings from a specific source document."""
        pass

    @abstractmethod
    def find_by_namespace(self, namespace: NamespaceId) -> List[VectorEmbedding]:
        """Retrieve all embeddings in a specific namespace."""
        pass

    @abstractmethod
    def delete_by_document(self, document_id: str) -> None:
        """Delete all embeddings associated with a document."""
        pass

    @abstractmethod
    def find_stale(self) -> List[VectorEmbedding]:
        """Retrieve all embeddings marked as stale."""
        pass


class AuditLogRepository(Repository[AuditLogEntry, str]):
    """
    Repository interface for AuditLogEntry.
    IMPORTANT: Entries are immutable — save() only creates, never updates.
    """

    @abstractmethod
    def find_by_user(self, user_id: str) -> List[AuditLogEntry]:
        """Retrieve all audit entries for a specific user."""
        pass

    @abstractmethod
    def find_by_namespace(self, namespace: NamespaceId) -> List[AuditLogEntry]:
        """Retrieve all audit entries for a specific namespace."""
        pass

    @abstractmethod
    def find_expired(self) -> List[AuditLogEntry]:
        """Retrieve all entries whose 12-month retention period has expired."""
        pass


class NamespaceRepository(Repository[Namespace, NamespaceId]):
    """Repository interface for Namespace entities."""

    @abstractmethod
    def find_queryable(self) -> List[Namespace]:
        """Retrieve all namespaces currently in ACTIVE/queryable status."""
        pass


class QuerySessionRepository(Repository[QuerySession, str]):
    """Repository interface for QuerySession entities."""

    @abstractmethod
    def find_by_user(self, user_id: str) -> List[QuerySession]:
        """Retrieve all query sessions submitted by a specific user."""
        pass

    @abstractmethod
    def find_by_namespace(self, namespace: NamespaceId) -> List[QuerySession]:
        """Retrieve all query sessions that targeted a specific namespace."""
        pass
