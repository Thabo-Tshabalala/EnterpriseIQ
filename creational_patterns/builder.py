# creational_patterns/builder.py
# Pattern: Builder
# Use Case: Constructing complex QuerySession objects step-by-step.
# Justification: A QuerySession has many optional attributes (PII detection results,
# retrieved embeddings, LLM response, citations). The Builder pattern allows
# the RAG pipeline to construct the session incrementally — scanning for PII,
# embedding, retrieving, then generating — without requiring a massive constructor
# with many optional parameters. Each step adds to the object.

from src.models import QuerySession, NamespaceId
import uuid


class QuerySessionBuilder:
    """
    Builder for constructing a QuerySession step-by-step.
    Each method returns self to support method chaining.
    """

    def __init__(self):
        self._query_id = str(uuid.uuid4())
        self._user_id: str = ""
        self._namespace: NamespaceId = NamespaceId.HR
        self._raw_query_text: str = ""
        self._top_k: int = 5
        self._pii_scanning_enabled: bool = True
        self._max_response_tokens: int = 1000

    def set_user(self, user_id: str) -> "QuerySessionBuilder":
        if not user_id:
            raise ValueError("user_id cannot be empty.")
        self._user_id = user_id
        return self

    def set_namespace(self, namespace: NamespaceId) -> "QuerySessionBuilder":
        self._namespace = namespace
        return self

    def set_query_text(self, text: str) -> "QuerySessionBuilder":
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty.")
        self._raw_query_text = text.strip()
        return self

    def set_top_k(self, top_k: int) -> "QuerySessionBuilder":
        if top_k < 1 or top_k > 10:
            raise ValueError("top_k must be between 1 and 10.")
        self._top_k = top_k
        return self

    def disable_pii_scanning(self) -> "QuerySessionBuilder":
        # Only allowed in internal/testing contexts
        self._pii_scanning_enabled = False
        return self

    def set_max_response_tokens(self, tokens: int) -> "QuerySessionBuilder":
        if tokens < 100:
            raise ValueError("max_response_tokens must be at least 100.")
        self._max_response_tokens = tokens
        return self

    def build(self) -> QuerySession:
        if not self._user_id:
            raise ValueError("Cannot build QuerySession without a user_id.")
        if not self._raw_query_text:
            raise ValueError("Cannot build QuerySession without query text.")

        session = QuerySession(
            query_id=self._query_id,
            user_id=self._user_id,
            namespace=self._namespace,
            raw_query_text=self._raw_query_text
        )
        return session
