# src/models.py

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List
import uuid


# ─────────────────────────────────────────
# ENUMERATIONS
# ─────────────────────────────────────────

class Role(Enum):
    EMPLOYEE = "EMPLOYEE"
    HR_MANAGER = "HR_MANAGER"
    FINANCE_OFFICER = "FINANCE_OFFICER"
    LEGAL_OFFICER = "LEGAL_OFFICER"
    OPS_MANAGER = "OPS_MANAGER"
    ADMIN = "ADMIN"


class AccountStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    DEACTIVATED = "DEACTIVATED"
    DELETED = "DELETED"


class DocumentStatus(Enum):
    UPLOADED = "UPLOADED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    FLAGGED = "FLAGGED"
    DELETED = "DELETED"


class NamespaceId(Enum):
    HR = "HR"
    FINANCE = "FINANCE"
    LEGAL = "LEGAL"
    OPERATIONS = "OPERATIONS"


class QueryStatus(Enum):
    INITIATED = "INITIATED"
    SCANNING = "SCANNING"
    EMBEDDING = "EMBEDDING"
    RETRIEVING = "RETRIEVING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TokenStatus(Enum):
    ISSUED = "ISSUED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


# ─────────────────────────────────────────
# USER ACCOUNT
# ─────────────────────────────────────────

class UserAccount:
    MAX_FAILED_ATTEMPTS = 5

    def __init__(self, user_id: str, email: str, role: Role):
        self._user_id = user_id
        self._email = email
        self._role = role
        self._status = AccountStatus.PENDING
        self._failed_login_attempts = 0
        self._created_at = datetime.now()
        self._last_login_at: Optional[datetime] = None

    def login(self) -> None:
        if self._status == AccountStatus.LOCKED:
            raise PermissionError("Account is locked. Contact your administrator.")
        if self._status in (AccountStatus.DEACTIVATED, AccountStatus.DELETED):
            raise PermissionError("Account is not active.")
        self._status = AccountStatus.ACTIVE
        self._failed_login_attempts = 0
        self._last_login_at = datetime.now()

    def record_failed_login(self) -> None:
        self._failed_login_attempts += 1
        if self._failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.lock_account()

    def lock_account(self) -> None:
        self._status = AccountStatus.LOCKED

    def unlock_account(self) -> None:
        self._status = AccountStatus.ACTIVE
        self._failed_login_attempts = 0

    def deactivate(self) -> None:
        self._status = AccountStatus.DEACTIVATED

    def delete(self) -> None:
        self._status = AccountStatus.DELETED

    def get_permitted_namespaces(self) -> List[NamespaceId]:
        if self._role == Role.ADMIN:
            return list(NamespaceId)
        mapping = {
            Role.HR_MANAGER: [NamespaceId.HR],
            Role.FINANCE_OFFICER: [NamespaceId.FINANCE],
            Role.LEGAL_OFFICER: [NamespaceId.LEGAL],
            Role.OPS_MANAGER: [NamespaceId.OPERATIONS],
            Role.EMPLOYEE: [],
        }
        return mapping.get(self._role, [])

    # Getters
    @property
    def user_id(self): return self._user_id
    @property
    def email(self): return self._email
    @property
    def role(self): return self._role
    @role.setter
    def role(self, value: Role): self._role = value
    @property
    def status(self): return self._status
    @property
    def failed_login_attempts(self): return self._failed_login_attempts
    @property
    def created_at(self): return self._created_at
    @property
    def last_login_at(self): return self._last_login_at


# ─────────────────────────────────────────
# JWT TOKEN
# ─────────────────────────────────────────

class JWTToken:
    def __init__(self, user_id: str, role: Role, expires_in_minutes: int = 60):
        self._token_id = str(uuid.uuid4())
        self._user_id = user_id
        self._role = role
        self._issued_at = datetime.now()
        self._expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        self._status = TokenStatus.ISSUED

    def validate(self) -> bool:
        if self._status == TokenStatus.REVOKED:
            return False
        if self.is_expired():
            self._status = TokenStatus.EXPIRED
            return False
        self._status = TokenStatus.ACTIVE
        return True

    def revoke(self) -> None:
        self._status = TokenStatus.REVOKED

    def is_expired(self) -> bool:
        return datetime.now() > self._expires_at

    def get_claims(self) -> dict:
        return {"user_id": self._user_id, "role": self._role.value}

    @property
    def token_id(self): return self._token_id
    @property
    def user_id(self): return self._user_id
    @property
    def role(self): return self._role
    @property
    def status(self): return self._status
    @property
    def expires_at(self): return self._expires_at


# ─────────────────────────────────────────
# DOCUMENT
# ─────────────────────────────────────────

class Document:
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
    EXPIRY_THRESHOLD_DAYS = 365             # 12 months

    def __init__(self, document_id: str, file_name: str, file_type: str,
                 file_size_bytes: int, namespace: NamespaceId, uploaded_by: str):
        self._document_id = document_id
        self._file_name = file_name
        self._file_type = file_type.upper()
        self._file_size_bytes = file_size_bytes
        self._namespace = namespace
        self._status = DocumentStatus.UPLOADED
        self._uploaded_by = uploaded_by
        self._uploaded_at = datetime.now()
        self._last_reviewed_at: Optional[datetime] = None
        self._ingestion_error: Optional[str] = None

    def validate(self) -> bool:
        if self._file_type not in ("PDF", "DOCX"):
            return False
        if self._file_size_bytes > self.MAX_FILE_SIZE_BYTES:
            return False
        return True

    def start_ingestion(self) -> None:
        if not self.validate():
            self._status = DocumentStatus.FAILED
            self._ingestion_error = "Validation failed: unsupported type or size exceeded."
            return
        self._status = DocumentStatus.PENDING

    def mark_reviewed(self) -> None:
        self._last_reviewed_at = datetime.now()
        if self._status == DocumentStatus.FLAGGED:
            self._status = DocumentStatus.READY

    def is_expired(self) -> bool:
        reference = self._last_reviewed_at or self._uploaded_at
        return (datetime.now() - reference).days >= self.EXPIRY_THRESHOLD_DAYS

    def delete(self) -> None:
        self._status = DocumentStatus.DELETED

    @property
    def document_id(self): return self._document_id
    @property
    def file_name(self): return self._file_name
    @property
    def file_type(self): return self._file_type
    @property
    def file_size_bytes(self): return self._file_size_bytes
    @property
    def namespace(self): return self._namespace
    @property
    def status(self): return self._status
    @status.setter
    def status(self, value: DocumentStatus): self._status = value
    @property
    def uploaded_by(self): return self._uploaded_by
    @property
    def uploaded_at(self): return self._uploaded_at
    @property
    def last_reviewed_at(self): return self._last_reviewed_at
    @property
    def ingestion_error(self): return self._ingestion_error


# ─────────────────────────────────────────
# VECTOR EMBEDDING
# ─────────────────────────────────────────

class VectorEmbedding:
    def __init__(self, embedding_id: str, document_id: str, namespace: NamespaceId,
                 chunk_text: str, chunk_index: int, page_number: int):
        self._embedding_id = embedding_id
        self._document_id = document_id
        self._namespace = namespace
        self._chunk_text = chunk_text
        self._chunk_index = chunk_index
        self._page_number = page_number
        self._vector: Optional[List[float]] = None
        self._created_at = datetime.now()
        self._is_stale = False

    def generate(self, text: str) -> List[float]:
        # Stub: production calls HuggingFace SentenceTransformer
        self._vector = [0.1 * (i % 10) for i in range(384)]
        return self._vector

    def store(self) -> None:
        print(f"Storing embedding {self._embedding_id} to ChromaDB [{self._namespace.value}]")

    def mark_stale(self) -> None:
        self._is_stale = True

    def delete(self) -> None:
        print(f"Deleting embedding {self._embedding_id} from ChromaDB")

    def get_similarity(self, query_vector: List[float]) -> float:
        if not self._vector or not query_vector:
            return 0.0
        dot = sum(a * b for a, b in zip(self._vector, query_vector))
        norm_a = sum(a ** 2 for a in self._vector) ** 0.5
        norm_b = sum(b ** 2 for b in query_vector) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def clone(self) -> "VectorEmbedding":
        import copy
        return copy.deepcopy(self)

    @property
    def embedding_id(self): return self._embedding_id
    @property
    def document_id(self): return self._document_id
    @property
    def namespace(self): return self._namespace
    @property
    def chunk_text(self): return self._chunk_text
    @property
    def chunk_index(self): return self._chunk_index
    @property
    def page_number(self): return self._page_number
    @property
    def vector(self): return self._vector
    @property
    def is_stale(self): return self._is_stale


# ─────────────────────────────────────────
# AUDIT LOG ENTRY
# ─────────────────────────────────────────

class AuditLogEntry:
    RETENTION_DAYS = 365  # 12 months

    def __init__(self, user_id: str, query_id: str, namespace: NamespaceId,
                 raw_query_text: str, redacted_query_text: str,
                 pii_detected: bool, sources_retrieved: List[str], response_text: str):
        self._log_id = str(uuid.uuid4())
        self._user_id = user_id
        self._query_id = query_id
        self._namespace = namespace
        self._raw_query_text = raw_query_text
        self._redacted_query_text = redacted_query_text
        self._pii_detected = pii_detected
        self._sources_retrieved = sources_retrieved
        self._response_text = response_text
        self._created_at = datetime.now()
        self._retention_expires_at = self._created_at + timedelta(days=self.RETENTION_DAYS)

    def write(self) -> None:
        print(f"[AUDIT] Writing log entry {self._log_id} for query {self._query_id}")

    def is_retention_expired(self) -> bool:
        return datetime.now() > self._retention_expires_at

    def export(self) -> str:
        return (f"{self._log_id},{self._user_id},{self._query_id},"
                f"{self._namespace.value},{self._created_at.isoformat()},"
                f"{self._pii_detected},{self._redacted_query_text}")

    @property
    def log_id(self): return self._log_id
    @property
    def user_id(self): return self._user_id
    @property
    def query_id(self): return self._query_id
    @property
    def namespace(self): return self._namespace
    @property
    def pii_detected(self): return self._pii_detected
    @property
    def response_text(self): return self._response_text
    @property
    def created_at(self): return self._created_at
    @property
    def retention_expires_at(self): return self._retention_expires_at


# ─────────────────────────────────────────
# NAMESPACE
# ─────────────────────────────────────────

class Namespace:
    def __init__(self, namespace_id: NamespaceId):
        self._namespace_id = namespace_id
        self._display_name = namespace_id.value.title()
        self._status = "INITIALISED"
        self._documents: List[Document] = []
        self._created_at = datetime.now()
        self._locked_at: Optional[datetime] = None

    def lock(self) -> None:
        self._status = "LOCKED"
        self._locked_at = datetime.now()

    def unlock(self) -> None:
        self._status = "ACTIVE" if self._documents else "EMPTY"
        self._locked_at = None

    def add_document(self, document: Document) -> None:
        self._documents.append(document)
        self._status = "ACTIVE"

    def get_documents(self) -> List[Document]:
        return self._documents

    def get_embedding_count(self) -> int:
        return len(self._documents)

    def is_queryable(self) -> bool:
        return self._status == "ACTIVE"

    @property
    def namespace_id(self): return self._namespace_id
    @property
    def display_name(self): return self._display_name
    @property
    def status(self): return self._status


# ─────────────────────────────────────────
# QUERY SESSION
# ─────────────────────────────────────────

class QuerySession:
    def __init__(self, query_id: str, user_id: str, namespace: NamespaceId, raw_query_text: str):
        self._query_id = query_id
        self._user_id = user_id
        self._namespace = namespace
        self._raw_query_text = raw_query_text
        self._redacted_query_text = raw_query_text
        self._pii_detected = False
        self._status = QueryStatus.INITIATED
        self._response_text: Optional[str] = None
        self._submitted_at = datetime.now()
        self._completed_at: Optional[datetime] = None

    def scan_for_pii(self) -> None:
        self._status = QueryStatus.SCANNING
        # Stub: production uses a real PII detection model
        pii_keywords = ["id:", "ID:", "password", "@"]
        for keyword in pii_keywords:
            if keyword in self._raw_query_text:
                self._pii_detected = True
                self._redacted_query_text = self._raw_query_text.replace(keyword, "[REDACTED]")

    def embed(self) -> List[float]:
        self._status = QueryStatus.EMBEDDING
        # Stub: production calls EmbeddingService
        return [0.1] * 384

    def retrieve(self, top_k: int = 5) -> List[VectorEmbedding]:
        self._status = QueryStatus.RETRIEVING
        # Stub: production queries ChromaDB
        return []

    def generate_response(self) -> str:
        self._status = QueryStatus.GENERATING
        # Stub: production calls LLMClient
        self._response_text = "This is a stub response from the LLM."
        self._status = QueryStatus.COMPLETED
        self._completed_at = datetime.now()
        return self._response_text

    def log_to_audit(self) -> AuditLogEntry:
        entry = AuditLogEntry(
            user_id=self._user_id,
            query_id=self._query_id,
            namespace=self._namespace,
            raw_query_text=self._raw_query_text,
            redacted_query_text=self._redacted_query_text,
            pii_detected=self._pii_detected,
            sources_retrieved=[],
            response_text=self._response_text or ""
        )
        entry.write()
        return entry

    @property
    def query_id(self): return self._query_id
    @property
    def user_id(self): return self._user_id
    @property
    def status(self): return self._status
    @property
    def pii_detected(self): return self._pii_detected
    @property
    def redacted_query_text(self): return self._redacted_query_text
    @property
    def response_text(self): return self._response_text
