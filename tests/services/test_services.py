# Run with: pytest tests/services/test_services.py -v

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from src.models import Role, AccountStatus, DocumentStatus, NamespaceId
from repositories.inmemory.inmemory_repositories import (
    InMemoryUserAccountRepository,
    InMemoryDocumentRepository,
    InMemoryQuerySessionRepository
)
from services.user_service import (
    UserService, UserAlreadyExistsError,
    UserNotFoundError, InvalidOperationError
)
from services.document_service import (
    DocumentService, DocumentNotFoundError,
    DocumentValidationError, InvalidOperationError as DocInvalidOp
)
from services.query_service import (
    QueryService, QueryNotFoundError,
    NamespaceAccessDeniedError, InvalidQueryError
)


# ═══════════════════════════════════════════════════════
# USER SERVICE TESTS
# ═══════════════════════════════════════════════════════

class TestUserService:

    def setup_method(self):
        self.repo = InMemoryUserAccountRepository()
        self.service = UserService(self.repo)

    def test_create_user_returns_active_user(self):
        user = self.service.create_user("alice@corp.com", Role.HR_MANAGER)
        assert user.email == "alice@corp.com"
        assert user.role == Role.HR_MANAGER
        assert user.status == AccountStatus.ACTIVE

    def test_create_user_persists_to_repo(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        assert self.repo.find_by_id(user.user_id) is not None

    def test_create_user_raises_on_duplicate_email(self):
        self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        with pytest.raises(UserAlreadyExistsError):
            self.service.create_user("alice@corp.com", Role.HR_MANAGER)

    def test_get_user_returns_correct_user(self):
        created = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        fetched = self.service.get_user(created.user_id)
        assert fetched.user_id == created.user_id

    def test_get_user_raises_when_not_found(self):
        with pytest.raises(UserNotFoundError):
            self.service.get_user("nonexistent-id")

    def test_get_all_users_returns_all(self):
        self.service.create_user("a@corp.com", Role.EMPLOYEE)
        self.service.create_user("b@corp.com", Role.HR_MANAGER)
        assert len(self.service.get_all_users()) == 2

    def test_get_users_by_role_filters_correctly(self):
        self.service.create_user("a@corp.com", Role.HR_MANAGER)
        self.service.create_user("b@corp.com", Role.EMPLOYEE)
        self.service.create_user("c@corp.com", Role.HR_MANAGER)
        hr_users = self.service.get_users_by_role(Role.HR_MANAGER)
        assert len(hr_users) == 2

    def test_update_role_changes_role(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        updated = self.service.update_role(user.user_id, Role.FINANCE_OFFICER)
        assert updated.role == Role.FINANCE_OFFICER

    def test_update_role_raises_on_deleted_user(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        self.service.delete_user(user.user_id)
        with pytest.raises(InvalidOperationError):
            self.service.update_role(user.user_id, Role.HR_MANAGER)

    def test_deactivate_user_sets_deactivated_status(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        deactivated = self.service.deactivate_user(user.user_id)
        assert deactivated.status == AccountStatus.DEACTIVATED

    def test_deactivate_deleted_user_raises(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        self.service.delete_user(user.user_id)
        with pytest.raises(InvalidOperationError):
            self.service.deactivate_user(user.user_id)

    def test_delete_user_sets_deleted_status(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        self.service.delete_user(user.user_id)
        stored = self.repo.find_by_id(user.user_id)
        assert stored.status == AccountStatus.DELETED

    def test_unlock_user_resets_status(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        user.lock_account()
        self.repo.save(user)
        unlocked = self.service.unlock_user(user.user_id)
        assert unlocked.status == AccountStatus.ACTIVE
        assert unlocked.failed_login_attempts == 0

    def test_unlock_non_locked_user_raises(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        with pytest.raises(InvalidOperationError):
            self.service.unlock_user(user.user_id)

    def test_record_failed_login_locks_after_five(self):
        user = self.service.create_user("alice@corp.com", Role.EMPLOYEE)
        for _ in range(5):
            self.service.record_failed_login("alice@corp.com")
        stored = self.repo.find_by_id(user.user_id)
        assert stored.status == AccountStatus.LOCKED

    def test_count_users_returns_correct_count(self):
        self.service.create_user("a@corp.com", Role.EMPLOYEE)
        self.service.create_user("b@corp.com", Role.EMPLOYEE)
        assert self.service.count_users() == 2


# ═══════════════════════════════════════════════════════
# DOCUMENT SERVICE TESTS
# ═══════════════════════════════════════════════════════

class TestDocumentService:

    def setup_method(self):
        self.repo = InMemoryDocumentRepository()
        self.service = DocumentService(self.repo)

    def test_upload_valid_pdf_returns_pending_doc(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        assert doc.status == DocumentStatus.PENDING
        assert doc.namespace == NamespaceId.HR

    def test_upload_valid_docx_returns_pending_doc(self):
        doc = self.service.upload_document(
            "contract.docx", "DOCX", 2048, NamespaceId.LEGAL, "u1"
        )
        assert doc.status == DocumentStatus.PENDING

    def test_upload_invalid_file_type_raises(self):
        with pytest.raises(DocumentValidationError):
            self.service.upload_document(
                "data.xlsx", "XLSX", 1024, NamespaceId.FINANCE, "u1"
            )

    def test_upload_oversized_file_raises(self):
        with pytest.raises(DocumentValidationError):
            self.service.upload_document(
                "huge.pdf", "PDF", 60 * 1024 * 1024, NamespaceId.HR, "u1"
            )

    def test_upload_persists_document(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        assert self.repo.find_by_id(doc.document_id) is not None

    def test_get_document_returns_correct_doc(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        fetched = self.service.get_document(doc.document_id)
        assert fetched.document_id == doc.document_id

    def test_get_document_raises_when_not_found(self):
        with pytest.raises(DocumentNotFoundError):
            self.service.get_document("nonexistent-id")

    def test_get_documents_by_namespace_filters_correctly(self):
        self.service.upload_document("a.pdf", "PDF", 1024, NamespaceId.HR, "u1")
        self.service.upload_document("b.pdf", "PDF", 1024, NamespaceId.FINANCE, "u1")
        self.service.upload_document("c.pdf", "PDF", 1024, NamespaceId.HR, "u1")
        hr_docs = self.service.get_documents_by_namespace(NamespaceId.HR)
        assert len(hr_docs) == 2

    def test_mark_ready_changes_status(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        doc.status = DocumentStatus.PROCESSING
        self.repo.save(doc)
        updated = self.service.mark_ready(doc.document_id)
        assert updated.status == DocumentStatus.READY

    def test_mark_ready_raises_on_wrong_status(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        with pytest.raises(DocInvalidOp):
            self.service.mark_ready(doc.document_id)  # Still PENDING

    def test_mark_failed_sets_error_message(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        updated = self.service.mark_failed(doc.document_id, "Parse error")
        assert updated.status == DocumentStatus.FAILED
        assert updated.ingestion_error == "Parse error"

    def test_delete_document_sets_deleted_status(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        self.service.delete_document(doc.document_id)
        stored = self.repo.find_by_id(doc.document_id)
        assert stored.status == DocumentStatus.DELETED

    def test_delete_already_deleted_raises(self):
        doc = self.service.upload_document(
            "policy.pdf", "PDF", 1024, NamespaceId.HR, "u1"
        )
        self.service.delete_document(doc.document_id)
        with pytest.raises(DocInvalidOp):
            self.service.delete_document(doc.document_id)

    def test_count_documents_returns_correct_count(self):
        self.service.upload_document("a.pdf", "PDF", 1024, NamespaceId.HR, "u1")
        self.service.upload_document("b.pdf", "PDF", 1024, NamespaceId.LEGAL, "u1")
        assert self.service.count_documents() == 2


# ═══════════════════════════════════════════════════════
# QUERY SERVICE TESTS
# ═══════════════════════════════════════════════════════

class TestQueryService:

    def setup_method(self):
        self.user_repo = InMemoryUserAccountRepository()
        self.query_repo = InMemoryQuerySessionRepository()
        self.user_service = UserService(self.user_repo)
        self.query_service = QueryService(self.query_repo)
        self.hr_user = self.user_service.create_user("hr@corp.com", Role.HR_MANAGER)
        self.employee = self.user_service.create_user("emp@corp.com", Role.EMPLOYEE)

    def test_submit_query_saves_session(self):
        session = self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "What is the leave policy?"
        )
        assert self.query_repo.find_by_id(session.query_id) is not None

    def test_submit_query_raises_on_empty_text(self):
        with pytest.raises(InvalidQueryError):
            self.query_service.submit_query(self.hr_user, NamespaceId.HR, "   ")

    def test_submit_query_raises_on_namespace_not_permitted(self):
        with pytest.raises(NamespaceAccessDeniedError):
            self.query_service.submit_query(
                self.hr_user, NamespaceId.FINANCE, "What is the stock level?"
            )

    def test_employee_cannot_query_any_namespace(self):
        with pytest.raises(NamespaceAccessDeniedError):
            self.query_service.submit_query(
                self.employee, NamespaceId.HR, "What is the leave policy?"
            )

    def test_submit_query_scans_for_pii(self):
        session = self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "What about user@corp.com details?"
        )
        assert session.pii_detected is True

    def test_process_query_sets_completed_status(self):
        session = self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "What is the leave policy?"
        )
        processed = self.query_service.process_query(session.query_id)
        from src.models import QueryStatus
        assert processed.status == QueryStatus.COMPLETED

    def test_process_query_returns_response_text(self):
        session = self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "What is the leave policy?"
        )
        processed = self.query_service.process_query(session.query_id)
        assert processed.response_text is not None
        assert len(processed.response_text) > 0

    def test_get_query_raises_when_not_found(self):
        with pytest.raises(QueryNotFoundError):
            self.query_service.get_query("nonexistent-query-id")

    def test_get_queries_by_user_returns_correct_sessions(self):
        finance_user = self.user_service.create_user(
            "fin@corp.com", Role.FINANCE_OFFICER
        )
        self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "Question 1"
        )
        self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "Question 2"
        )
        self.query_service.submit_query(
            finance_user, NamespaceId.FINANCE, "Stock level?"
        )
        hr_sessions = self.query_service.get_queries_by_user(self.hr_user.user_id)
        assert len(hr_sessions) == 2

    def test_delete_query_removes_session(self):
        session = self.query_service.submit_query(
            self.hr_user, NamespaceId.HR, "Question?"
        )
        self.query_service.delete_query(session.query_id)
        with pytest.raises(QueryNotFoundError):
            self.query_service.get_query(session.query_id)

    def test_count_queries_returns_correct_count(self):
        self.query_service.submit_query(self.hr_user, NamespaceId.HR, "Q1")
        self.query_service.submit_query(self.hr_user, NamespaceId.HR, "Q2")
        assert self.query_service.count_queries() == 2
