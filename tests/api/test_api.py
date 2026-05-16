# Run with: pytest tests/api/test_api.py -v

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from api.main import app, user_service, document_service, query_service
from repositories.inmemory.inmemory_repositories import (
    InMemoryUserAccountRepository,
    InMemoryDocumentRepository,
    InMemoryQuerySessionRepository
)
from services.user_service import UserService
from services.document_service import DocumentService
from services.query_service import QueryService
from api.routers import users, documents, queries

# ─── Fresh in-memory state for each test session ──────────────────────────────

@pytest.fixture(autouse=True)
def reset_services():
    """Reset all repositories before each test to ensure isolation."""
    user_repo = InMemoryUserAccountRepository()
    doc_repo = InMemoryDocumentRepository()
    query_repo = InMemoryQuerySessionRepository()

    us = UserService(user_repo)
    ds = DocumentService(doc_repo)
    qs = QueryService(query_repo)

    users.service = us
    documents.service = ds
    queries.service = qs
    queries.user_service = us
    yield

client = TestClient(app)


# ═══════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ═══════════════════════════════════════════════════════
# USER API TESTS
# ═══════════════════════════════════════════════════════

def test_create_user_returns_201():
    response = client.post("/api/users/", json={
        "email": "alice@corp.com",
        "role": "HR_MANAGER"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@corp.com"
    assert data["role"] == "HR_MANAGER"
    assert data["status"] == "ACTIVE"

def test_create_user_returns_409_on_duplicate_email():
    client.post("/api/users/", json={"email": "alice@corp.com", "role": "EMPLOYEE"})
    response = client.post("/api/users/", json={"email": "alice@corp.com", "role": "HR_MANAGER"})
    assert response.status_code == 409

def test_get_all_users_returns_200():
    client.post("/api/users/", json={"email": "a@corp.com", "role": "EMPLOYEE"})
    client.post("/api/users/", json={"email": "b@corp.com", "role": "HR_MANAGER"})
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_user_by_id_returns_correct_user():
    create_resp = client.post("/api/users/", json={
        "email": "alice@corp.com", "role": "EMPLOYEE"
    })
    user_id = create_resp.json()["user_id"]
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id

def test_get_user_returns_404_for_unknown_id():
    response = client.get("/api/users/does-not-exist")
    assert response.status_code == 404

def test_update_role_returns_updated_user():
    create_resp = client.post("/api/users/", json={
        "email": "alice@corp.com", "role": "EMPLOYEE"
    })
    user_id = create_resp.json()["user_id"]
    response = client.put(f"/api/users/{user_id}/role", json={"role": "FINANCE_OFFICER"})
    assert response.status_code == 200
    assert response.json()["role"] == "FINANCE_OFFICER"

def test_deactivate_user_sets_deactivated():
    create_resp = client.post("/api/users/", json={
        "email": "alice@corp.com", "role": "EMPLOYEE"
    })
    user_id = create_resp.json()["user_id"]
    response = client.post(f"/api/users/{user_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["status"] == "DEACTIVATED"

def test_delete_user_returns_204():
    create_resp = client.post("/api/users/", json={
        "email": "alice@corp.com", "role": "EMPLOYEE"
    })
    user_id = create_resp.json()["user_id"]
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204

def test_count_users_returns_correct_number():
    client.post("/api/users/", json={"email": "a@corp.com", "role": "EMPLOYEE"})
    client.post("/api/users/", json={"email": "b@corp.com", "role": "HR_MANAGER"})
    response = client.get("/api/users/count/total")
    assert response.status_code == 200
    assert response.json()["count"] == 2


# ═══════════════════════════════════════════════════════
# DOCUMENT API TESTS
# ═══════════════════════════════════════════════════════

def test_upload_valid_document_returns_201():
    response = client.post("/api/documents/", json={
        "file_name": "policy.pdf",
        "file_type": "PDF",
        "file_size_bytes": 1024,
        "namespace": "HR",
        "uploaded_by": "u1"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "policy.pdf"
    assert data["status"] == "PENDING"

def test_upload_invalid_type_returns_422():
    response = client.post("/api/documents/", json={
        "file_name": "data.xlsx",
        "file_type": "XLSX",
        "file_size_bytes": 1024,
        "namespace": "FINANCE",
        "uploaded_by": "u1"
    })
    assert response.status_code == 422

def test_upload_oversized_file_returns_422():
    response = client.post("/api/documents/", json={
        "file_name": "huge.pdf",
        "file_type": "PDF",
        "file_size_bytes": 60 * 1024 * 1024,
        "namespace": "HR",
        "uploaded_by": "u1"
    })
    assert response.status_code == 422

def test_get_all_documents_returns_200():
    client.post("/api/documents/", json={
        "file_name": "a.pdf", "file_type": "PDF",
        "file_size_bytes": 1024, "namespace": "HR", "uploaded_by": "u1"
    })
    response = client.get("/api/documents/")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_document_by_id_returns_correct_doc():
    create_resp = client.post("/api/documents/", json={
        "file_name": "policy.pdf", "file_type": "PDF",
        "file_size_bytes": 1024, "namespace": "HR", "uploaded_by": "u1"
    })
    doc_id = create_resp.json()["document_id"]
    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["document_id"] == doc_id

def test_get_document_returns_404_for_unknown():
    response = client.get("/api/documents/does-not-exist")
    assert response.status_code == 404

def test_get_by_namespace_filters_correctly():
    client.post("/api/documents/", json={
        "file_name": "hr.pdf", "file_type": "PDF",
        "file_size_bytes": 1024, "namespace": "HR", "uploaded_by": "u1"
    })
    client.post("/api/documents/", json={
        "file_name": "fin.pdf", "file_type": "PDF",
        "file_size_bytes": 1024, "namespace": "FINANCE", "uploaded_by": "u1"
    })
    response = client.get("/api/documents/namespace/HR")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["namespace"] == "HR"

def test_delete_document_returns_204():
    create_resp = client.post("/api/documents/", json={
        "file_name": "policy.pdf", "file_type": "PDF",
        "file_size_bytes": 1024, "namespace": "HR", "uploaded_by": "u1"
    })
    doc_id = create_resp.json()["document_id"]
    response = client.delete(f"/api/documents/{doc_id}")
    assert response.status_code == 204

def test_count_documents_returns_correct_number():
    client.post("/api/documents/", json={
        "file_name": "a.pdf", "file_type": "PDF",
        "file_size_bytes": 1024, "namespace": "HR", "uploaded_by": "u1"
    })
    client.post("/api/documents/", json={
        "file_name": "b.docx", "file_type": "DOCX",
        "file_size_bytes": 2048, "namespace": "LEGAL", "uploaded_by": "u1"
    })
    response = client.get("/api/documents/count/total")
    assert response.status_code == 200
    assert response.json()["count"] == 2


# ═══════════════════════════════════════════════════════
# QUERY API TESTS
# ═══════════════════════════════════════════════════════

def _create_hr_user():
    resp = client.post("/api/users/", json={
        "email": "hr@corp.com", "role": "HR_MANAGER"
    })
    return resp.json()["user_id"]

def test_submit_query_returns_201():
    user_id = _create_hr_user()
    response = client.post("/api/queries/", json={
        "user_id": user_id,
        "namespace": "HR",
        "query_text": "What is the leave policy?"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["namespace"] == "HR"
    assert data["raw_query_text"] == "What is the leave policy?"

def test_submit_query_returns_403_on_wrong_namespace():
    user_id = _create_hr_user()
    response = client.post("/api/queries/", json={
        "user_id": user_id,
        "namespace": "FINANCE",
        "query_text": "Stock level?"
    })
    assert response.status_code == 403

def test_submit_query_returns_400_on_empty_text():
    user_id = _create_hr_user()
    response = client.post("/api/queries/", json={
        "user_id": user_id,
        "namespace": "HR",
        "query_text": "   "
    })
    assert response.status_code == 400

def test_submit_query_returns_404_on_unknown_user():
    response = client.post("/api/queries/", json={
        "user_id": "ghost-id",
        "namespace": "HR",
        "query_text": "Question?"
    })
    assert response.status_code == 404

def test_get_query_by_id_returns_correct_session():
    user_id = _create_hr_user()
    create_resp = client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR",
        "query_text": "Leave policy?"
    })
    query_id = create_resp.json()["query_id"]
    response = client.get(f"/api/queries/{query_id}")
    assert response.status_code == 200
    assert response.json()["query_id"] == query_id

def test_get_query_returns_404_for_unknown():
    response = client.get("/api/queries/nonexistent-id")
    assert response.status_code == 404

def test_process_query_sets_completed_status():
    user_id = _create_hr_user()
    create_resp = client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR",
        "query_text": "Leave policy?"
    })
    query_id = create_resp.json()["query_id"]
    process_resp = client.post(f"/api/queries/{query_id}/process")
    assert process_resp.status_code == 200
    assert process_resp.json()["status"] == "COMPLETED"
    assert process_resp.json()["response_text"] is not None

def test_get_queries_by_user_returns_correct_sessions():
    user_id = _create_hr_user()
    client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR", "query_text": "Q1"
    })
    client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR", "query_text": "Q2"
    })
    response = client.get(f"/api/queries/user/{user_id}")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_delete_query_returns_204():
    user_id = _create_hr_user()
    create_resp = client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR", "query_text": "Question?"
    })
    query_id = create_resp.json()["query_id"]
    response = client.delete(f"/api/queries/{query_id}")
    assert response.status_code == 204

def test_count_queries_returns_correct_number():
    user_id = _create_hr_user()
    client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR", "query_text": "Q1"
    })
    client.post("/api/queries/", json={
        "user_id": user_id, "namespace": "HR", "query_text": "Q2"
    })
    response = client.get("/api/queries/count/total")
    assert response.status_code == 200
    assert response.json()["count"] == 2
