from typing import List
from src.models import Document, DocumentStatus, NamespaceId
from repositories.interfaces import DocumentRepository
import uuid


class DocumentNotFoundError(Exception):
    pass

class DocumentValidationError(Exception):
    pass

class InvalidOperationError(Exception):
    pass


class DocumentService:
    """
    Service class for Document business operations.
    Enforces business rules: file type/size validation, status transitions,
    namespace assignment, and expiry flagging.
    """

    def __init__(self, document_repository: DocumentRepository):
        self._repo = document_repository

    def upload_document(self, file_name: str, file_type: str,
                        file_size_bytes: int, namespace: NamespaceId,
                        uploaded_by: str) -> Document:
        """
        Upload and validate a new document.
        Business rules:
          - Only PDF and DOCX are accepted.
          - File size must not exceed 50MB.
          - Document is set to PENDING after successful validation.
        """
        document_id = str(uuid.uuid4())
        doc = Document(document_id, file_name, file_type,
                       file_size_bytes, namespace, uploaded_by)

        if not doc.validate():
            raise DocumentValidationError(
                f"Document '{file_name}' failed validation. "
                "Only PDF/DOCX files under 50MB are accepted."
            )
        doc.start_ingestion()
        self._repo.save(doc)
        return doc

    def get_document(self, document_id: str) -> Document:
        """Retrieve a document by ID. Raises DocumentNotFoundError if missing."""
        doc = self._repo.find_by_id(document_id)
        if doc is None:
            raise DocumentNotFoundError(f"Document '{document_id}' not found.")
        return doc

    def get_all_documents(self) -> List[Document]:
        """Return all documents."""
        return self._repo.find_all()

    def get_documents_by_namespace(self, namespace: NamespaceId) -> List[Document]:
        """Return all documents in a specific namespace."""
        return self._repo.find_by_namespace(namespace)

    def get_flagged_documents(self) -> List[Document]:
        """Return all documents currently flagged for review."""
        return self._repo.find_flagged()

    def mark_ready(self, document_id: str) -> Document:
        """
        Mark a document as READY (ingestion complete).
        Business rule: Only PROCESSING documents can be marked READY.
        """
        doc = self.get_document(document_id)
        if doc.status != DocumentStatus.PROCESSING:
            raise InvalidOperationError(
                f"Document '{document_id}' is not in PROCESSING status "
                f"(current: {doc.status.value})."
            )
        doc.status = DocumentStatus.READY
        self._repo.save(doc)
        return doc

    def mark_failed(self, document_id: str, error_message: str) -> Document:
        """
        Mark a document as FAILED with an error description.
        Business rule: Only PROCESSING documents can be marked FAILED.
        """
        doc = self.get_document(document_id)
        if doc.status not in (DocumentStatus.PROCESSING, DocumentStatus.PENDING):
            raise InvalidOperationError(
                f"Document '{document_id}' cannot be marked FAILED "
                f"from status: {doc.status.value}."
            )
        doc.status = DocumentStatus.FAILED
        doc._ingestion_error = error_message
        self._repo.save(doc)
        return doc

    def mark_reviewed(self, document_id: str) -> Document:
        """
        Mark a Legal namespace document as reviewed, clearing any expiry flag.
        Business rule: Only documents in READY or FLAGGED status can be reviewed.
        """
        doc = self.get_document(document_id)
        if doc.status not in (DocumentStatus.READY, DocumentStatus.FLAGGED):
            raise InvalidOperationError(
                f"Document '{document_id}' cannot be marked reviewed "
                f"from status: {doc.status.value}."
            )
        doc.mark_reviewed()
        self._repo.save(doc)
        return doc

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document.
        Business rule: DELETED documents cannot be deleted again.
        """
        doc = self.get_document(document_id)
        if doc.status == DocumentStatus.DELETED:
            raise InvalidOperationError(
                f"Document '{document_id}' is already deleted."
            )
        doc.delete()
        self._repo.save(doc)

    def flag_expired_documents(self) -> List[Document]:
        """
        Check all READY Legal namespace documents and flag expired ones.
        Business rule: Documents not reviewed in 12 months are flagged.
        Returns the list of newly flagged documents.
        """
        flagged = []
        all_docs = self._repo.find_by_namespace(NamespaceId.LEGAL)
        for doc in all_docs:
            if doc.status == DocumentStatus.READY and doc.is_expired():
                doc.status = DocumentStatus.FLAGGED
                self._repo.save(doc)
                flagged.append(doc)
        return flagged

    def count_documents(self) -> int:
        """Return the total number of documents."""
        return self._repo.count()
