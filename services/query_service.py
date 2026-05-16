from typing import List
from src.models import QuerySession, QueryStatus, NamespaceId, UserAccount
from repositories.interfaces import QuerySessionRepository
import uuid


class QueryNotFoundError(Exception):
    pass

class NamespaceAccessDeniedError(Exception):
    pass

class InvalidQueryError(Exception):
    pass


class QueryService:
    """
    Service class for QuerySession business operations.
    Enforces business rules:
      - Query text cannot be empty.
      - User must have permission to query the target namespace.
      - Every query is persisted with full lifecycle tracking.
    """

    def __init__(self, query_repository: QuerySessionRepository):
        self._repo = query_repository

    def submit_query(self, user: UserAccount, namespace: NamespaceId,
                     query_text: str) -> QuerySession:
        """
        Submit a new natural language query.
        Business rules:
          - Query text must not be empty or whitespace only.
          - User's permitted namespaces must include the target namespace.
          - Query is saved immediately on submission for audit purposes.
        """
        if not query_text or not query_text.strip():
            raise InvalidQueryError("Query text cannot be empty.")

        permitted = user.get_permitted_namespaces()
        if namespace not in permitted:
            raise NamespaceAccessDeniedError(
                f"User '{user.user_id}' (role: {user.role.value}) "
                f"is not permitted to query namespace '{namespace.value}'."
            )

        query_id = str(uuid.uuid4())
        session = QuerySession(query_id, user.user_id, namespace, query_text.strip())

        # PII scan
        session.scan_for_pii()

        # Persist immediately for audit trail
        self._repo.save(session)
        return session

    def process_query(self, query_id: str) -> QuerySession:
        """
        Run the full RAG pipeline for a saved query session.
        Business rule: Only SCANNING or INITIATED sessions can be processed.
        """
        session = self.get_query(query_id)
        if session.status not in (QueryStatus.INITIATED, QueryStatus.SCANNING):
            raise InvalidQueryError(
                f"Query '{query_id}' cannot be processed "
                f"from status: {session.status.value}."
            )
        # Run pipeline steps (stubs — production calls real services)
        session.embed()
        session.retrieve(top_k=5)
        session.generate_response()

        self._repo.save(session)
        return session

    def get_query(self, query_id: str) -> QuerySession:
        """Retrieve a query session by ID. Raises QueryNotFoundError if missing."""
        session = self._repo.find_by_id(query_id)
        if session is None:
            raise QueryNotFoundError(f"Query session '{query_id}' not found.")
        return session

    def get_all_queries(self) -> List[QuerySession]:
        """Return all query sessions."""
        return self._repo.find_all()

    def get_queries_by_user(self, user_id: str) -> List[QuerySession]:
        """Return all query sessions submitted by a specific user."""
        return self._repo.find_by_user(user_id)

    def get_queries_by_namespace(self, namespace: NamespaceId) -> List[QuerySession]:
        """Return all query sessions targeting a specific namespace."""
        return self._repo.find_by_namespace(namespace)

    def delete_query(self, query_id: str) -> None:
        """
        Delete a query session record.
        Business rule: Session must exist.
        """
        self.get_query(query_id)  # Raises if not found
        self._repo.delete(query_id)

    def count_queries(self) -> int:
        """Return the total number of query sessions."""
        return self._repo.count()
