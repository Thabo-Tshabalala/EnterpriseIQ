# Endpoints: submit query, process, retrieve, delete

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.models import NamespaceId, QueryStatus
from services.query_service import (
    QueryService, QueryNotFoundError,
    NamespaceAccessDeniedError, InvalidQueryError
)
from services.user_service import UserService, UserNotFoundError

router = APIRouter(prefix="/api/queries", tags=["Queries"])
service: QueryService = None       # Injected in main.py
user_service: UserService = None   # Injected in main.py


# ─── Pydantic Schemas ──────────────────────────────────────────────────────────

class SubmitQueryRequest(BaseModel):
    user_id: str = Field(..., example="user-uuid-here")
    namespace: NamespaceId = Field(..., example="HR")
    query_text: str = Field(..., example="What is the annual leave policy?")

class QueryResponse(BaseModel):
    query_id: str
    user_id: str
    namespace: str
    raw_query_text: str
    redacted_query_text: str
    pii_detected: bool
    status: str
    response_text: Optional[str]

    @classmethod
    def from_model(cls, session):
        return cls(
            query_id=session.query_id,
            user_id=session.user_id,
            namespace=session._namespace.value,
            raw_query_text=session._raw_query_text,
            redacted_query_text=session.redacted_query_text,
            pii_detected=session.pii_detected,
            status=session.status.value,
            response_text=session.response_text
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[QueryResponse],
    summary="Get all query sessions",
    description="Returns all stored query sessions."
)
def get_all_queries():
    sessions = service.get_all_queries()
    return [QueryResponse.from_model(s) for s in sessions]


@router.post(
    "/",
    response_model=QueryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new query",
    description=(
        "Submit a natural language query against a department namespace. "
        "The user must have permission to query the target namespace. "
        "PII is automatically scanned and redacted before processing."
    )
)
def submit_query(request: SubmitQueryRequest):
    try:
        user = user_service.get_user(request.user_id)
        session = service.submit_query(user, request.namespace, request.query_text)
        return QueryResponse.from_model(session)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NamespaceAccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{query_id}",
    response_model=QueryResponse,
    summary="Get query session by ID",
    description="Returns a single query session by its unique ID."
)
def get_query(query_id: str):
    try:
        session = service.get_query(query_id)
        return QueryResponse.from_model(session)
    except QueryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{query_id}/process",
    response_model=QueryResponse,
    summary="Process a query (run RAG pipeline)",
    description=(
        "Runs the full RAG pipeline on a submitted query: "
        "embed → retrieve → generate response. "
        "Only queries in INITIATED or SCANNING status can be processed."
    )
)
def process_query(query_id: str):
    try:
        session = service.process_query(query_id)
        return QueryResponse.from_model(session)
    except QueryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/user/{user_id}",
    response_model=List[QueryResponse],
    summary="Get queries by user",
    description="Returns all query sessions submitted by a specific user."
)
def get_queries_by_user(user_id: str):
    sessions = service.get_queries_by_user(user_id)
    return [QueryResponse.from_model(s) for s in sessions]


@router.get(
    "/namespace/{namespace}",
    response_model=List[QueryResponse],
    summary="Get queries by namespace",
    description="Returns all query sessions targeting a specific namespace."
)
def get_queries_by_namespace(namespace: NamespaceId):
    sessions = service.get_queries_by_namespace(namespace)
    return [QueryResponse.from_model(s) for s in sessions]


@router.delete(
    "/{query_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete query session",
    description="Deletes a query session record."
)
def delete_query(query_id: str):
    try:
        service.delete_query(query_id)
    except QueryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/count/total",
    summary="Count query sessions",
    description="Returns the total number of stored query sessions."
)
def count_queries():
    return {"count": service.count_queries()}
