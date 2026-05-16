# Swagger UI available at http://localhost:8000/docs
# OpenAPI JSON available at http://localhost:8000/openapi.json

from fastapi import FastAPI
from api.routers import users, documents, queries
from repositories.inmemory.inmemory_repositories import (
    InMemoryUserAccountRepository,
    InMemoryDocumentRepository,
    InMemoryQuerySessionRepository
)
from services.user_service import UserService
from services.document_service import DocumentService
from services.query_service import QueryService

# ─── Create shared repository instances 
user_repo = InMemoryUserAccountRepository()
document_repo = InMemoryDocumentRepository()
query_repo = InMemoryQuerySessionRepository()

# ─── Create shared service instances
user_service = UserService(user_repo)
document_service = DocumentService(document_repo)
query_service = QueryService(query_repo)

# ─── FastAPI app ─────────
app = FastAPI(
    title="EnterpriseIQ API",
    description=(
        "REST API for EnterpriseIQ — an Intelligent Retrieval-Augmented Generation "
        "system for Enterprise Knowledge Management. "
        "Provides endpoints for user management, document ingestion, and RAG query sessions."
    ),
    version="1.0.0",
    contact={
        "name": "Thabo Tshabalala",
        "url": "https://github.com/Thabo-Tshabalala/ENTERPRISEQ"
    },
    license_info={
        "name": "MIT"
    }
)

# ─── Inject services into routers ────
users.service = user_service
documents.service = document_service
queries.service = query_service
queries.user_service = user_service

# ─── Register routers ───
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(queries.router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint — confirms the API is running."""
    return {"status": "ok", "system": "EnterpriseIQ API", "version": "1.0.0"}
