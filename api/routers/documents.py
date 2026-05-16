# Endpoints: upload, retrieve, status updates, flag expiry, delete

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.models import NamespaceId, DocumentStatus
from services.document_service import (
    DocumentService, DocumentNotFoundError,
    DocumentValidationError, InvalidOperationError
)

router = APIRouter(prefix="/api/documents", tags=["Documents"])
service: DocumentService = None  # Injected in main.py


# ─── Pydantic Schemas ──────────────────────────────────────────────────────────

class UploadDocumentRequest(BaseModel):
    file_name: str = Field(..., example="hr_policy_2025.pdf")
    file_type: str = Field(..., example="PDF", description="PDF or DOCX only")
    file_size_bytes: int = Field(..., example=204800, description="File size in bytes")
    namespace: NamespaceId = Field(..., example="HR")
    uploaded_by: str = Field(..., example="user-uuid-here")

class MarkFailedRequest(BaseModel):
    error_message: str = Field(..., example="Failed to extract text from scanned PDF.")

class DocumentResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    namespace: str
    status: str
    uploaded_by: str
    ingestion_error: Optional[str]

    @classmethod
    def from_model(cls, doc):
        return cls(
            document_id=doc.document_id,
            file_name=doc.file_name,
            file_type=doc.file_type,
            file_size_bytes=doc.file_size_bytes,
            namespace=doc.namespace.value,
            status=doc.status.value,
            uploaded_by=doc.uploaded_by,
            ingestion_error=doc.ingestion_error
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="Get all documents",
    description="Returns all documents across all namespaces."
)
def get_all_documents():
    docs = service.get_all_documents()
    return [DocumentResponse.from_model(d) for d in docs]


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description=(
        "Upload a new document to a department namespace. "
        "Only PDF and DOCX files under 50MB are accepted."
    )
)
def upload_document(request: UploadDocumentRequest):
    try:
        doc = service.upload_document(
            file_name=request.file_name,
            file_type=request.file_type,
            file_size_bytes=request.file_size_bytes,
            namespace=request.namespace,
            uploaded_by=request.uploaded_by
        )
        return DocumentResponse.from_model(doc)
    except DocumentValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
    description="Returns a single document by its unique ID."
)
def get_document(document_id: str):
    try:
        doc = service.get_document(document_id)
        return DocumentResponse.from_model(doc)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/namespace/{namespace}",
    response_model=List[DocumentResponse],
    summary="Get documents by namespace",
    description="Returns all documents in a specific department namespace."
)
def get_by_namespace(namespace: NamespaceId):
    docs = service.get_documents_by_namespace(namespace)
    return [DocumentResponse.from_model(d) for d in docs]


@router.post(
    "/{document_id}/ready",
    response_model=DocumentResponse,
    summary="Mark document as READY",
    description="Marks a PROCESSING document as READY (ingestion complete)."
)
def mark_ready(document_id: str):
    try:
        doc = service.mark_ready(document_id)
        return DocumentResponse.from_model(doc)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{document_id}/failed",
    response_model=DocumentResponse,
    summary="Mark document as FAILED",
    description="Marks a document ingestion as FAILED with an error message."
)
def mark_failed(document_id: str, request: MarkFailedRequest):
    try:
        doc = service.mark_failed(document_id, request.error_message)
        return DocumentResponse.from_model(doc)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{document_id}/review",
    response_model=DocumentResponse,
    summary="Mark document as reviewed",
    description="Marks a Legal namespace document as reviewed, clearing any expiry flag."
)
def mark_reviewed(document_id: str):
    try:
        doc = service.mark_reviewed(document_id)
        return DocumentResponse.from_model(doc)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/flagged/all",
    response_model=List[DocumentResponse],
    summary="Get flagged documents",
    description="Returns all documents currently flagged for review."
)
def get_flagged():
    docs = service.get_flagged_documents()
    return [DocumentResponse.from_model(d) for d in docs]


@router.post(
    "/flagged/run-check",
    response_model=List[DocumentResponse],
    summary="Run expiry check",
    description="Checks all LEGAL namespace documents and flags expired ones."
)
def run_expiry_check():
    flagged = service.flag_expired_documents()
    return [DocumentResponse.from_model(d) for d in flagged]


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Marks a document as DELETED. Cannot delete an already deleted document."
)
def delete_document(document_id: str):
    try:
        service.delete_document(document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/count/total",
    summary="Count documents",
    description="Returns the total number of documents."
)
def count_documents():
    return {"count": service.count_documents()}
