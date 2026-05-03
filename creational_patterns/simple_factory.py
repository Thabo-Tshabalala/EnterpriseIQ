# Pattern: Factory Method
# Use Case: Document ingestion — different parsers for PDF vs DOCX files.
# Justification: PDF and DOCX documents require different parsing libraries
# (PyMuPDF vs python-docx). The Factory Method lets each concrete parser subclass
# decide how to extract text, while the base class defines the ingestion contract.
# New file types (e.g., TXT, XLSX) can be added without modifying existing code.

from abc import ABC, abstractmethod
from src.models import Document, DocumentStatus


class DocumentParser(ABC):
    """
    Abstract base class defining the factory method contract.
    Subclasses implement parse() for their specific file type.
    """

    def ingest(self, document: Document) -> str:
        """
        Template method: validates, then delegates parsing to the subclass factory method.
        """
        if not document.validate():
            document.status = DocumentStatus.FAILED
            raise ValueError(f"Document {document.file_name} failed validation.")

        document.status = DocumentStatus.PROCESSING
        text = self.parse(document)
        document.status = DocumentStatus.READY
        return text

    @abstractmethod
    def parse(self, document: Document) -> str:
        """Factory method — subclasses implement type-specific parsing logic."""
        pass


class PDFParser(DocumentParser):
    """Concrete parser for PDF documents using PyMuPDF (stubbed)."""

    def parse(self, document: Document) -> str:
        # Stub: production uses PyMuPDF (fitz)
        print(f"[PDFParser] Parsing PDF: {document.file_name}")
        return f"Extracted text from PDF: {document.file_name}"


class DOCXParser(DocumentParser):
    """Concrete parser for DOCX documents using python-docx (stubbed)."""

    def parse(self, document: Document) -> str:
        # Stub: production uses python-docx
        print(f"[DOCXParser] Parsing DOCX: {document.file_name}")
        return f"Extracted text from DOCX: {document.file_name}"


class DocumentParserFactory:
    """
    Factory that returns the correct DocumentParser based on file type.
    """

    @staticmethod
    def get_parser(file_type: str) -> DocumentParser:
        file_type = file_type.upper()
        if file_type == "PDF":
            return PDFParser()
        elif file_type == "DOCX":
            return DOCXParser()
        else:
            raise ValueError(f"No parser available for file type: {file_type}")
