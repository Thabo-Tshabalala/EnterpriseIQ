# EnterpriseIQ — Unit Tests for All Classes and Creational Patterns
# Run with: pytest tests/test_all.py -v --tb=short

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import threading
from src.models import (
    UserAccount, Role, AccountStatus,
    JWTToken, TokenStatus,
    Document, DocumentStatus, NamespaceId,
    VectorEmbedding, AuditLogEntry, Namespace, QuerySession, QueryStatus
)
from creational_patterns.simple_factory import NamespaceFactory
from creational_patterns.factory_method import DocumentParserFactory, PDFParser, DOCXParser
from creational_patterns.abstract_factory import (
    OpenAIProviderFactory, OllamaProviderFactory, get_provider_factory
)
from creational_patterns.builder import QuerySessionBuilder
from creational_patterns.prototype import EmbeddingPrototypeCache
from creational_patterns.singleton import AuditLogger


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — CORE MODEL TESTS
# ═══════════════════════════════════════════════════════════════

class TestUserAccount:

    def test_user_created_with_pending_status(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        assert user.status == AccountStatus.PENDING

    def test_login_activates_account(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        user.login()
        assert user.status == AccountStatus.ACTIVE

    def test_login_resets_failed_attempts(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        user._failed_login_attempts = 3
        user.login()
        assert user.failed_login_attempts == 0

    def test_account_locks_after_five_failed_attempts(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        for _ in range(5):
            user.record_failed_login()
        assert user.status == AccountStatus.LOCKED

    def test_account_does_not_lock_before_five_attempts(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        for _ in range(4):
            user.record_failed_login()
        assert user.status != AccountStatus.LOCKED

    def test_login_raises_on_locked_account(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        user.lock_account()
        with pytest.raises(PermissionError):
            user.login()

    def test_login_raises_on_deactivated_account(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        user.deactivate()
        with pytest.raises(PermissionError):
            user.login()

    def test_unlock_resets_failed_attempts(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        for _ in range(5):
            user.record_failed_login()
        user.unlock_account()
        assert user.status == AccountStatus.ACTIVE
        assert user.failed_login_attempts == 0

    def test_admin_gets_all_namespaces(self):
        admin = UserAccount("a1", "admin@corp.com", Role.ADMIN)
        namespaces = admin.get_permitted_namespaces()
        assert set(namespaces) == set(NamespaceId)

    def test_hr_manager_gets_only_hr_namespace(self):
        hr = UserAccount("h1", "hr@corp.com", Role.HR_MANAGER)
        assert hr.get_permitted_namespaces() == [NamespaceId.HR]

    def test_employee_gets_no_namespaces(self):
        emp = UserAccount("e1", "emp@corp.com", Role.EMPLOYEE)
        assert emp.get_permitted_namespaces() == []

    def test_delete_sets_deleted_status(self):
        user = UserAccount("u1", "alice@corp.com", Role.EMPLOYEE)
        user.delete()
        assert user.status == AccountStatus.DELETED


class TestJWTToken:

    def test_new_token_is_issued(self):
        token = JWTToken("u1", Role.EMPLOYEE)
        assert token.status == TokenStatus.ISSUED

    def test_validate_active_token_returns_true(self):
        token = JWTToken("u1", Role.EMPLOYEE, expires_in_minutes=60)
        assert token.validate() is True

    def test_revoked_token_fails_validation(self):
        token = JWTToken("u1", Role.EMPLOYEE)
        token.revoke()
        assert token.validate() is False

    def test_expired_token_fails_validation(self):
        token = JWTToken("u1", Role.EMPLOYEE, expires_in_minutes=-1)
        assert token.validate() is False

    def test_get_claims_returns_user_id_and_role(self):
        token = JWTToken("u1", Role.HR_MANAGER)
        claims = token.get_claims()
        assert claims["user_id"] == "u1"
        assert claims["role"] == Role.HR_MANAGER.value

    def test_is_expired_on_past_token(self):
        token = JWTToken("u1", Role.EMPLOYEE, expires_in_minutes=-10)
        assert token.is_expired() is True

    def test_is_not_expired_on_future_token(self):
        token = JWTToken("u1", Role.EMPLOYEE, expires_in_minutes=60)
        assert token.is_expired() is False


class TestDocument:

    def _make_doc(self, file_type="PDF", size=1024):
        return Document("d1", "policy.pdf", file_type, size, NamespaceId.HR, "u1")

    def test_document_created_with_uploaded_status(self):
        doc = self._make_doc()
        assert doc.status == DocumentStatus.UPLOADED

    def test_validate_returns_true_for_pdf(self):
        doc = self._make_doc("PDF")
        assert doc.validate() is True

    def test_validate_returns_true_for_docx(self):
        doc = self._make_doc("DOCX")
        assert doc.validate() is True

    def test_validate_returns_false_for_unsupported_type(self):
        doc = self._make_doc("XLSX")
        assert doc.validate() is False

    def test_validate_returns_false_for_oversized_file(self):
        doc = self._make_doc("PDF", 60 * 1024 * 1024)  # 60MB
        assert doc.validate() is False

    def test_start_ingestion_sets_pending_for_valid_doc(self):
        doc = self._make_doc()
        doc.start_ingestion()
        assert doc.status == DocumentStatus.PENDING

    def test_start_ingestion_sets_failed_for_invalid_doc(self):
        doc = self._make_doc("XLSX")
        doc.start_ingestion()
        assert doc.status == DocumentStatus.FAILED

    def test_mark_reviewed_clears_flagged_status(self):
        doc = self._make_doc()
        doc.status = DocumentStatus.FLAGGED
        doc.mark_reviewed()
        assert doc.status == DocumentStatus.READY

    def test_delete_sets_deleted_status(self):
        doc = self._make_doc()
        doc.delete()
        assert doc.status == DocumentStatus.DELETED


class TestVectorEmbedding:

    def _make_embedding(self):
        return VectorEmbedding("e1", "d1", NamespaceId.HR, "Sample text.", 0, 1)

    def test_generate_returns_vector(self):
        emb = self._make_embedding()
        vector = emb.generate("Sample text.")
        assert isinstance(vector, list)
        assert len(vector) == 384

    def test_mark_stale_sets_flag(self):
        emb = self._make_embedding()
        emb.mark_stale()
        assert emb.is_stale is True

    def test_get_similarity_returns_float(self):
        emb = self._make_embedding()
        emb.generate("text")
        query_vector = [0.1] * 384
        score = emb.get_similarity(query_vector)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_get_similarity_returns_zero_for_empty_vector(self):
        emb = self._make_embedding()
        score = emb.get_similarity([0.1] * 384)
        assert score == 0.0

    def test_clone_produces_independent_copy(self):
        emb = self._make_embedding()
        emb.generate("text")
        clone = emb.clone()
        assert clone.embedding_id == emb.embedding_id
        clone._embedding_id = "clone-id"
        assert emb.embedding_id != clone.embedding_id


class TestAuditLogEntry:

    def _make_entry(self):
        return AuditLogEntry("u1", "q1", NamespaceId.HR,
                             "raw query", "redacted query",
                             False, ["doc1.pdf p.3"], "LLM response")

    def test_entry_has_unique_log_id(self):
        e1 = self._make_entry()
        e2 = self._make_entry()
        assert e1.log_id != e2.log_id

    def test_export_returns_csv_string(self):
        entry = self._make_entry()
        csv = entry.export()
        assert "u1" in csv
        assert "q1" in csv
        assert "HR" in csv

    def test_retention_not_expired_on_new_entry(self):
        entry = self._make_entry()
        assert entry.is_retention_expired() is False


class TestQuerySession:

    def test_session_created_with_initiated_status(self):
        session = QuerySession("q1", "u1", NamespaceId.HR, "What is the leave policy?")
        assert session.status == QueryStatus.INITIATED

    def test_scan_for_pii_detects_email_symbol(self):
        session = QuerySession("q1", "u1", NamespaceId.HR, "Query for user@corp.com details")
        session.scan_for_pii()
        assert session.pii_detected is True

    def test_scan_for_pii_clean_query(self):
        session = QuerySession("q1", "u1", NamespaceId.HR, "What is the annual leave policy?")
        session.scan_for_pii()
        assert session.pii_detected is False

    def test_generate_response_returns_string(self):
        session = QuerySession("q1", "u1", NamespaceId.HR, "What is the leave policy?")
        response = session.generate_response()
        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_response_sets_completed_status(self):
        session = QuerySession("q1", "u1", NamespaceId.HR, "What is the leave policy?")
        session.generate_response()
        assert session.status == QueryStatus.COMPLETED


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — CREATIONAL PATTERN TESTS
# ═══════════════════════════════════════════════════════════════

class TestSimpleFactory:

    def test_creates_hr_namespace(self):
        ns = NamespaceFactory.create(NamespaceId.HR)
        assert ns.namespace_id == NamespaceId.HR

    def test_creates_finance_namespace(self):
        ns = NamespaceFactory.create(NamespaceId.FINANCE)
        assert ns.namespace_id == NamespaceId.FINANCE

    def test_creates_all_four_namespaces(self):
        namespaces = NamespaceFactory.create_all()
        assert len(namespaces) == 4
        assert NamespaceId.HR in namespaces
        assert NamespaceId.LEGAL in namespaces
        assert NamespaceId.OPERATIONS in namespaces

    def test_all_namespaces_are_namespace_instances(self):
        namespaces = NamespaceFactory.create_all()
        for ns in namespaces.values():
            assert isinstance(ns, Namespace)


class TestFactoryMethod:

    def test_get_parser_returns_pdf_parser(self):
        parser = DocumentParserFactory.get_parser("PDF")
        assert isinstance(parser, PDFParser)

    def test_get_parser_returns_docx_parser(self):
        parser = DocumentParserFactory.get_parser("DOCX")
        assert isinstance(parser, DOCXParser)

    def test_get_parser_case_insensitive(self):
        parser = DocumentParserFactory.get_parser("pdf")
        assert isinstance(parser, PDFParser)

    def test_get_parser_raises_for_unknown_type(self):
        with pytest.raises(ValueError):
            DocumentParserFactory.get_parser("XLSX")

    def test_pdf_parser_ingests_valid_document(self):
        doc = Document("d1", "report.pdf", "PDF", 1024, NamespaceId.HR, "u1")
        parser = DocumentParserFactory.get_parser("PDF")
        result = parser.ingest(doc)
        assert "report.pdf" in result
        assert doc.status == DocumentStatus.READY

    def test_parser_sets_failed_on_invalid_document(self):
        doc = Document("d1", "data.xlsx", "XLSX", 1024, NamespaceId.HR, "u1")
        parser = PDFParser()
        with pytest.raises(ValueError):
            parser.ingest(doc)
        assert doc.status == DocumentStatus.FAILED


class TestAbstractFactory:

    def test_openai_factory_creates_openai_embedding_service(self):
        factory = OpenAIProviderFactory()
        service = factory.create_embedding_service()
        assert service.get_model_name() == "text-embedding-3-small"

    def test_openai_factory_creates_openai_llm_client(self):
        factory = OpenAIProviderFactory()
        client = factory.create_llm_client()
        assert client.get_model_name() == "gpt-4o"

    def test_ollama_factory_creates_ollama_embedding_service(self):
        factory = OllamaProviderFactory()
        service = factory.create_embedding_service()
        assert service.get_model_name() == "nomic-embed-text"

    def test_ollama_factory_creates_ollama_llm_client(self):
        factory = OllamaProviderFactory()
        client = factory.create_llm_client()
        assert client.get_model_name() == "llama3"

    def test_openai_embed_returns_vector(self):
        factory = OpenAIProviderFactory()
        service = factory.create_embedding_service()
        vector = service.embed("test text")
        assert isinstance(vector, list)
        assert len(vector) == 1536

    def test_ollama_embed_returns_vector(self):
        factory = OllamaProviderFactory()
        service = factory.create_embedding_service()
        vector = service.embed("test text")
        assert isinstance(vector, list)
        assert len(vector) == 768

    def test_get_provider_factory_openai(self):
        factory = get_provider_factory("openai")
        assert isinstance(factory, OpenAIProviderFactory)

    def test_get_provider_factory_ollama(self):
        factory = get_provider_factory("ollama")
        assert isinstance(factory, OllamaProviderFactory)

    def test_get_provider_factory_raises_for_unknown(self):
        with pytest.raises(ValueError):
            get_provider_factory("unknown_provider")


class TestBuilder:

    def test_build_creates_valid_query_session(self):
        session = (QuerySessionBuilder()
                   .set_user("u1")
                   .set_namespace(NamespaceId.HR)
                   .set_query_text("What is the leave policy?")
                   .build())
        assert isinstance(session, QuerySession)
        assert session.user_id == "u1"

    def test_build_raises_without_user_id(self):
        with pytest.raises(ValueError):
            QuerySessionBuilder().set_query_text("query").build()

    def test_build_raises_without_query_text(self):
        with pytest.raises(ValueError):
            QuerySessionBuilder().set_user("u1").build()

    def test_build_raises_on_empty_query_text(self):
        with pytest.raises(ValueError):
            (QuerySessionBuilder()
             .set_user("u1")
             .set_query_text("   ")
             .build())

    def test_set_top_k_raises_on_invalid_value(self):
        with pytest.raises(ValueError):
            QuerySessionBuilder().set_top_k(0)

    def test_set_top_k_raises_on_value_above_ten(self):
        with pytest.raises(ValueError):
            QuerySessionBuilder().set_top_k(11)

    def test_set_max_tokens_raises_below_minimum(self):
        with pytest.raises(ValueError):
            QuerySessionBuilder().set_max_response_tokens(50)

    def test_method_chaining_returns_builder(self):
        builder = QuerySessionBuilder().set_user("u1")
        assert isinstance(builder, QuerySessionBuilder)

    def test_built_session_has_correct_namespace(self):
        session = (QuerySessionBuilder()
                   .set_user("u1")
                   .set_namespace(NamespaceId.FINANCE)
                   .set_query_text("Stock level for SKU-4821?")
                   .build())
        assert session._namespace == NamespaceId.FINANCE


class TestPrototype:

    def test_cache_initialises_all_four_namespaces(self):
        cache = EmbeddingPrototypeCache()
        for ns in NamespaceId:
            clone = cache.get_clone(ns, "e1", "d1", "chunk", 0, 1)
            assert clone is not None

    def test_clone_has_correct_embedding_id(self):
        cache = EmbeddingPrototypeCache()
        clone = cache.get_clone(NamespaceId.HR, "my-id", "d1", "text", 0, 1)
        assert clone.embedding_id == "my-id"

    def test_clone_has_correct_chunk_text(self):
        cache = EmbeddingPrototypeCache()
        clone = cache.get_clone(NamespaceId.LEGAL, "e1", "d1", "Contract clause", 2, 5)
        assert clone.chunk_text == "Contract clause"

    def test_clone_has_correct_page_number(self):
        cache = EmbeddingPrototypeCache()
        clone = cache.get_clone(NamespaceId.FINANCE, "e1", "d1", "text", 0, 7)
        assert clone.page_number == 7

    def test_two_clones_are_independent(self):
        cache = EmbeddingPrototypeCache()
        clone1 = cache.get_clone(NamespaceId.HR, "e1", "d1", "text1", 0, 1)
        clone2 = cache.get_clone(NamespaceId.HR, "e2", "d1", "text2", 1, 2)
        assert clone1.embedding_id != clone2.embedding_id
        assert clone1.chunk_text != clone2.chunk_text

    def test_clone_vector_is_independent_from_prototype(self):
        cache = EmbeddingPrototypeCache()
        clone = cache.get_clone(NamespaceId.HR, "e1", "d1", "text", 0, 1)
        if clone.vector:
            original_vector = cache._prototypes[NamespaceId.HR].vector
            assert clone.vector is not original_vector

    def test_raises_for_unknown_namespace(self):
        cache = EmbeddingPrototypeCache()
        cache._prototypes = {}  # Clear all prototypes
        with pytest.raises(ValueError):
            cache.get_clone(NamespaceId.HR, "e1", "d1", "text", 0, 1)


class TestSingleton:

    def setup_method(self):
        """Reset singleton before each test."""
        AuditLogger.reset_for_testing()

    def test_singleton_returns_same_instance(self):
        logger1 = AuditLogger()
        logger2 = AuditLogger()
        assert logger1 is logger2

    def test_write_increments_count(self):
        logger = AuditLogger()
        entry = AuditLogEntry("u1", "q1", NamespaceId.HR,
                              "raw", "redacted", False, [], "response")
        logger.write(entry)
        assert logger.get_write_count() == 1

    def test_multiple_writes_tracked(self):
        logger = AuditLogger()
        for i in range(5):
            entry = AuditLogEntry(f"u{i}", f"q{i}", NamespaceId.HR,
                                  "raw", "redacted", False, [], "response")
            logger.write(entry)
        assert logger.get_write_count() == 5

    def test_get_all_entries_returns_written_entries(self):
        logger = AuditLogger()
        entry = AuditLogEntry("u1", "q1", NamespaceId.HR,
                              "raw", "redacted", False, [], "response")
        logger.write(entry)
        entries = logger.get_all_entries()
        assert len(entries) == 1
        assert entries[0].log_id == entry.log_id

    def test_export_csv_contains_header(self):
        logger = AuditLogger()
        csv = logger.export_csv()
        assert "log_id" in csv

    def test_thread_safety(self):
        """Multiple threads should share the same singleton instance."""
        instances = []

        def get_instance():
            instances.append(AuditLogger())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first = instances[0]
        assert all(inst is first for inst in instances)

    def test_singleton_state_shared_across_references(self):
        logger1 = AuditLogger()
        entry = AuditLogEntry("u1", "q1", NamespaceId.HR,
                              "raw", "redacted", False, [], "response")
        logger1.write(entry)

        logger2 = AuditLogger()
        assert logger2.get_write_count() == 1
