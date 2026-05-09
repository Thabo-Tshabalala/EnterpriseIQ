# Run with: pytest tests/test_repositories.py -v

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.models import (
    UserAccount, Document, VectorEmbedding,
    AuditLogEntry, Namespace, QuerySession,
    Role, AccountStatus, DocumentStatus, NamespaceId, QueryStatus
)
from repositories.inmemory.inmemory_repositories import (
    InMemoryUserAccountRepository,
    InMemoryDocumentRepository,
    InMemoryVectorEmbeddingRepository,
    InMemoryAuditLogRepository,
    InMemoryNamespaceRepository,
    InMemoryQuerySessionRepository
)
from factories.repository_factory import RepositoryFactory


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_user(uid="u1", email="alice@corp.com", role=Role.EMPLOYEE):
    return UserAccount(uid, email, role)

def make_document(did="d1", ftype="PDF", namespace=NamespaceId.HR, uploader="u1"):
    return Document(did, "policy.pdf", ftype, 1024, namespace, uploader)

def make_embedding(eid="e1", doc_id="d1", namespace=NamespaceId.HR):
    emb = VectorEmbedding(eid, doc_id, namespace, "Sample chunk text", 0, 1)
    emb.generate("sample")
    return emb

def make_audit_entry(log_id_suffix="1", user_id="u1", namespace=NamespaceId.HR):
    entry = AuditLogEntry(
        user_id=user_id,
        query_id=f"q{log_id_suffix}",
        namespace=namespace,
        raw_query_text="What is the leave policy?",
        redacted_query_text="What is the leave policy?",
        pii_detected=False,
        sources_retrieved=["policy.pdf p.3"],
        response_text="Annual leave is 15 days."
    )
    return entry

def make_namespace(ns_id=NamespaceId.HR):
    return Namespace(ns_id)

def make_query_session(qid="q1", user_id="u1", namespace=NamespaceId.HR):
    return QuerySession(qid, user_id, namespace, "What is the leave policy?")


# ═══════════════════════════════════════════════════════════════════════════════
# USER ACCOUNT REPOSITORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryUserAccountRepository:

    def setup_method(self):
        self.repo = InMemoryUserAccountRepository()

    def test_save_and_find_by_id(self):
        user = make_user()
        self.repo.save(user)
        result = self.repo.find_by_id("u1")
        assert result is not None
        assert result.user_id == "u1"

    def test_find_by_id_returns_none_when_missing(self):
        assert self.repo.find_by_id("nonexistent") is None

    def test_find_all_returns_all_saved_users(self):
        self.repo.save(make_user("u1", "a@corp.com"))
        self.repo.save(make_user("u2", "b@corp.com"))
        assert len(self.repo.find_all()) == 2

    def test_find_all_returns_empty_on_empty_store(self):
        assert self.repo.find_all() == []

    def test_delete_removes_user(self):
        self.repo.save(make_user())
        self.repo.delete("u1")
        assert self.repo.find_by_id("u1") is None

    def test_delete_nonexistent_does_not_raise(self):
        self.repo.delete("does-not-exist")  # Should not raise

    def test_exists_returns_true_after_save(self):
        self.repo.save(make_user())
        assert self.repo.exists("u1") is True

    def test_exists_returns_false_for_missing(self):
        assert self.repo.exists("ghost") is False

    def test_count_reflects_saved_entities(self):
        self.repo.save(make_user("u1", "a@corp.com"))
        self.repo.save(make_user("u2", "b@corp.com"))
        assert self.repo.count() == 2

    def test_save_overwrites_existing_user(self):
        user = make_user()
        self.repo.save(user)
        user.role = Role.HR_MANAGER
        self.repo.save(user)
        result = self.repo.find_by_id("u1")
        assert result.role == Role.HR_MANAGER

    def test_find_by_email_returns_correct_user(self):
        self.repo.save(make_user("u1", "alice@corp.com"))
        result = self.repo.find_by_email("alice@corp.com")
        assert result is not None
        assert result.user_id == "u1"

    def test_find_by_email_returns_none_when_missing(self):
        assert self.repo.find_by_email("nobody@corp.com") is None

    def test_find_by_role_returns_matching_users(self):
        self.repo.save(make_user("u1", "a@corp.com", Role.HR_MANAGER))
        self.repo.save(make_user("u2", "b@corp.com", Role.EMPLOYEE))
        self.repo.save(make_user("u3", "c@corp.com", Role.HR_MANAGER))
        result = self.repo.find_by_role(Role.HR_MANAGER)
        assert len(result) == 2

    def test_find_by_role_returns_empty_when_no_match(self):
        self.repo.save(make_user("u1", "a@corp.com", Role.EMPLOYEE))
        assert self.repo.find_by_role(Role.ADMIN) == []

    def test_find_by_status_returns_locked_users(self):
        user = make_user()
        user.lock_account()
        self.repo.save(user)
        result = self.repo.find_by_status(AccountStatus.LOCKED)
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT REPOSITORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryDocumentRepository:

    def setup_method(self):
        self.repo = InMemoryDocumentRepository()

    def test_save_and_find_by_id(self):
        doc = make_document()
        self.repo.save(doc)
        assert self.repo.find_by_id("d1") is not None

    def test_find_by_id_returns_none_when_missing(self):
        assert self.repo.find_by_id("missing") is None

    def test_find_all_returns_all_documents(self):
        self.repo.save(make_document("d1"))
        self.repo.save(make_document("d2"))
        assert len(self.repo.find_all()) == 2

    def test_delete_removes_document(self):
        self.repo.save(make_document())
        self.repo.delete("d1")
        assert self.repo.find_by_id("d1") is None

    def test_exists_true_after_save(self):
        self.repo.save(make_document())
        assert self.repo.exists("d1") is True

    def test_count_correct(self):
        self.repo.save(make_document("d1"))
        self.repo.save(make_document("d2"))
        assert self.repo.count() == 2

    def test_find_by_namespace_returns_correct_docs(self):
        self.repo.save(make_document("d1", namespace=NamespaceId.HR))
        self.repo.save(make_document("d2", namespace=NamespaceId.FINANCE))
        self.repo.save(make_document("d3", namespace=NamespaceId.HR))
        result = self.repo.find_by_namespace(NamespaceId.HR)
        assert len(result) == 2

    def test_find_by_namespace_returns_empty_when_no_match(self):
        self.repo.save(make_document("d1", namespace=NamespaceId.HR))
        assert self.repo.find_by_namespace(NamespaceId.LEGAL) == []

    def test_find_by_status_returns_matching_docs(self):
        doc = make_document()
        doc.status = DocumentStatus.READY
        self.repo.save(doc)
        result = self.repo.find_by_status(DocumentStatus.READY)
        assert len(result) == 1

    def test_find_by_uploader_returns_correct_docs(self):
        self.repo.save(make_document("d1", uploader="u1"))
        self.repo.save(make_document("d2", uploader="u2"))
        self.repo.save(make_document("d3", uploader="u1"))
        result = self.repo.find_by_uploader("u1")
        assert len(result) == 2

    def test_find_flagged_returns_only_flagged(self):
        doc = make_document()
        doc.status = DocumentStatus.FLAGGED
        self.repo.save(doc)
        self.repo.save(make_document("d2"))
        result = self.repo.find_flagged()
        assert len(result) == 1
        assert result[0].document_id == "d1"


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR EMBEDDING REPOSITORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryVectorEmbeddingRepository:

    def setup_method(self):
        self.repo = InMemoryVectorEmbeddingRepository()

    def test_save_and_find_by_id(self):
        emb = make_embedding()
        self.repo.save(emb)
        assert self.repo.find_by_id("e1") is not None

    def test_find_by_document_returns_all_for_doc(self):
        self.repo.save(make_embedding("e1", "d1"))
        self.repo.save(make_embedding("e2", "d1"))
        self.repo.save(make_embedding("e3", "d2"))
        result = self.repo.find_by_document("d1")
        assert len(result) == 2

    def test_find_by_namespace_returns_correct(self):
        self.repo.save(make_embedding("e1", "d1", NamespaceId.HR))
        self.repo.save(make_embedding("e2", "d2", NamespaceId.FINANCE))
        result = self.repo.find_by_namespace(NamespaceId.HR)
        assert len(result) == 1

    def test_delete_by_document_removes_all_for_doc(self):
        self.repo.save(make_embedding("e1", "d1"))
        self.repo.save(make_embedding("e2", "d1"))
        self.repo.save(make_embedding("e3", "d2"))
        self.repo.delete_by_document("d1")
        assert self.repo.count() == 1
        assert self.repo.find_by_id("e3") is not None

    def test_find_stale_returns_only_stale(self):
        emb = make_embedding()
        emb.mark_stale()
        self.repo.save(emb)
        self.repo.save(make_embedding("e2"))
        result = self.repo.find_stale()
        assert len(result) == 1
        assert result[0].embedding_id == "e1"

    def test_delete_removes_embedding(self):
        self.repo.save(make_embedding())
        self.repo.delete("e1")
        assert self.repo.exists("e1") is False

    def test_count_correct(self):
        self.repo.save(make_embedding("e1"))
        self.repo.save(make_embedding("e2"))
        assert self.repo.count() == 2


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOG REPOSITORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryAuditLogRepository:

    def setup_method(self):
        self.repo = InMemoryAuditLogRepository()

    def test_save_and_find_by_id(self):
        entry = make_audit_entry()
        self.repo.save(entry)
        result = self.repo.find_by_id(entry.log_id)
        assert result is not None

    def test_save_same_entry_twice_raises(self):
        entry = make_audit_entry()
        self.repo.save(entry)
        with pytest.raises(ValueError, match="immutable"):
            self.repo.save(entry)

    def test_find_by_user_returns_correct_entries(self):
        e1 = make_audit_entry("1", "u1")
        e2 = make_audit_entry("2", "u2")
        e3 = make_audit_entry("3", "u1")
        self.repo.save(e1)
        self.repo.save(e2)
        self.repo.save(e3)
        result = self.repo.find_by_user("u1")
        assert len(result) == 2

    def test_find_by_namespace_returns_correct(self):
        e1 = make_audit_entry("1", namespace=NamespaceId.HR)
        e2 = make_audit_entry("2", namespace=NamespaceId.FINANCE)
        self.repo.save(e1)
        self.repo.save(e2)
        result = self.repo.find_by_namespace(NamespaceId.HR)
        assert len(result) == 1

    def test_count_reflects_all_entries(self):
        self.repo.save(make_audit_entry("1"))
        self.repo.save(make_audit_entry("2"))
        assert self.repo.count() == 2

    def test_find_all_returns_all_entries(self):
        self.repo.save(make_audit_entry("1"))
        self.repo.save(make_audit_entry("2"))
        assert len(self.repo.find_all()) == 2

    def test_exists_true_after_save(self):
        entry = make_audit_entry()
        self.repo.save(entry)
        assert self.repo.exists(entry.log_id) is True

    def test_exists_false_for_unknown_id(self):
        assert self.repo.exists("unknown-log-id") is False


# ═══════════════════════════════════════════════════════════════════════════════
# NAMESPACE REPOSITORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryNamespaceRepository:

    def setup_method(self):
        self.repo = InMemoryNamespaceRepository()

    def test_save_and_find_by_id(self):
        ns = make_namespace(NamespaceId.HR)
        self.repo.save(ns)
        result = self.repo.find_by_id(NamespaceId.HR)
        assert result is not None
        assert result.namespace_id == NamespaceId.HR

    def test_find_all_returns_all_namespaces(self):
        for ns_id in NamespaceId:
            self.repo.save(make_namespace(ns_id))
        assert self.repo.count() == 4

    def test_delete_removes_namespace(self):
        self.repo.save(make_namespace(NamespaceId.LEGAL))
        self.repo.delete(NamespaceId.LEGAL)
        assert self.repo.find_by_id(NamespaceId.LEGAL) is None

    def test_find_queryable_returns_active_namespaces(self):
        ns = make_namespace(NamespaceId.HR)
        doc = make_document()
        ns.add_document(doc)  # Makes namespace ACTIVE
        self.repo.save(ns)
        self.repo.save(make_namespace(NamespaceId.FINANCE))  # stays INITIALISED
        result = self.repo.find_queryable()
        assert len(result) == 1
        assert result[0].namespace_id == NamespaceId.HR

    def test_exists_after_save(self):
        self.repo.save(make_namespace(NamespaceId.OPERATIONS))
        assert self.repo.exists(NamespaceId.OPERATIONS) is True


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY SESSION REPOSITORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryQuerySessionRepository:

    def setup_method(self):
        self.repo = InMemoryQuerySessionRepository()

    def test_save_and_find_by_id(self):
        session = make_query_session()
        self.repo.save(session)
        result = self.repo.find_by_id("q1")
        assert result is not None

    def test_find_by_user_returns_all_for_user(self):
        self.repo.save(make_query_session("q1", "u1"))
        self.repo.save(make_query_session("q2", "u2"))
        self.repo.save(make_query_session("q3", "u1"))
        result = self.repo.find_by_user("u1")
        assert len(result) == 2

    def test_find_by_namespace_returns_correct(self):
        self.repo.save(make_query_session("q1", "u1", NamespaceId.HR))
        self.repo.save(make_query_session("q2", "u1", NamespaceId.FINANCE))
        result = self.repo.find_by_namespace(NamespaceId.HR)
        assert len(result) == 1

    def test_delete_removes_session(self):
        self.repo.save(make_query_session())
        self.repo.delete("q1")
        assert self.repo.exists("q1") is False

    def test_count_correct(self):
        self.repo.save(make_query_session("q1"))
        self.repo.save(make_query_session("q2"))
        assert self.repo.count() == 2


# ═══════════════════════════════════════════════════════════════════════════════
# REPOSITORY FACTORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRepositoryFactory:

    def test_memory_factory_returns_user_repo(self):
        factory = RepositoryFactory("MEMORY")
        repo = factory.get_user_repository()
        assert isinstance(repo, InMemoryUserAccountRepository)

    def test_memory_factory_returns_document_repo(self):
        factory = RepositoryFactory("MEMORY")
        repo = factory.get_document_repository()
        assert isinstance(repo, InMemoryDocumentRepository)

    def test_memory_factory_returns_embedding_repo(self):
        factory = RepositoryFactory("MEMORY")
        repo = factory.get_embedding_repository()
        assert isinstance(repo, InMemoryVectorEmbeddingRepository)

    def test_memory_factory_returns_audit_repo(self):
        factory = RepositoryFactory("MEMORY")
        repo = factory.get_audit_log_repository()
        assert isinstance(repo, InMemoryAuditLogRepository)

    def test_memory_factory_returns_namespace_repo(self):
        factory = RepositoryFactory("MEMORY")
        repo = factory.get_namespace_repository()
        assert isinstance(repo, InMemoryNamespaceRepository)

    def test_memory_factory_returns_query_session_repo(self):
        factory = RepositoryFactory("MEMORY")
        repo = factory.get_query_session_repository()
        assert isinstance(repo, InMemoryQuerySessionRepository)

    def test_factory_is_case_insensitive(self):
        factory = RepositoryFactory("memory")
        repo = factory.get_user_repository()
        assert isinstance(repo, InMemoryUserAccountRepository)

    def test_factory_raises_for_unknown_storage_type(self):
        with pytest.raises(ValueError, match="Unknown storage type"):
            RepositoryFactory("CASSANDRA")

    def test_filesystem_factory_returns_document_repo(self):
        from repositories.filesystem.filesystem_repositories import FileSystemDocumentRepository
        factory = RepositoryFactory("FILESYSTEM")
        repo = factory.get_document_repository()
        assert isinstance(repo, FileSystemDocumentRepository)

    def test_filesystem_factory_raises_for_unimplemented_repo(self):
        factory = RepositoryFactory("FILESYSTEM")
        with pytest.raises(NotImplementedError):
            factory.get_user_repository()

    def test_database_factory_raises_not_implemented_on_use(self):
        factory = RepositoryFactory("DATABASE")
        repo = factory.get_user_repository()
        with pytest.raises(NotImplementedError):
            repo.save(make_user())
