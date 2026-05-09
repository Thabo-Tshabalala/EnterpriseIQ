# Swapping from MEMORY to DATABASE requires only changing the factory config.
# No domain classes or service classes need any modification.

from typing import List, Optional
from repositories.interfaces import UserAccountRepository, DocumentRepository
from src.models import (
    UserAccount, Document,
    Role, AccountStatus, DocumentStatus, NamespaceId
)


class DatabaseUserAccountRepository(UserAccountRepository):
    """
    STUB: PostgreSQL implementation of UserAccountRepository.
    Production implementation would use SQLAlchemy ORM sessions.

    Example production methods:
        def save(self, entity):
            self._session.merge(entity)
            self._session.commit()

        def find_by_id(self, entity_id):
            return self._session.query(UserAccount).filter_by(user_id=entity_id).first()
    """

    def __init__(self):
        # STUB: Production would inject a SQLAlchemy Session here
        # self._session = session
        print("[DatabaseUserAccountRepository] STUB — no DB connected.")

    def save(self, entity: UserAccount) -> None:
        raise NotImplementedError("DatabaseUserAccountRepository.save() not yet implemented.")

    def find_by_id(self, entity_id: str) -> Optional[UserAccount]:
        raise NotImplementedError("DatabaseUserAccountRepository.find_by_id() not yet implemented.")

    def find_all(self) -> List[UserAccount]:
        raise NotImplementedError("DatabaseUserAccountRepository.find_all() not yet implemented.")

    def delete(self, entity_id: str) -> None:
        raise NotImplementedError("DatabaseUserAccountRepository.delete() not yet implemented.")

    def exists(self, entity_id: str) -> bool:
        raise NotImplementedError("DatabaseUserAccountRepository.exists() not yet implemented.")

    def count(self) -> int:
        raise NotImplementedError("DatabaseUserAccountRepository.count() not yet implemented.")

    def find_by_email(self, email: str) -> Optional[UserAccount]:
        raise NotImplementedError("DatabaseUserAccountRepository.find_by_email() not yet implemented.")

    def find_by_role(self, role: Role) -> List[UserAccount]:
        raise NotImplementedError("DatabaseUserAccountRepository.find_by_role() not yet implemented.")

    def find_by_status(self, status: AccountStatus) -> List[UserAccount]:
        raise NotImplementedError("DatabaseUserAccountRepository.find_by_status() not yet implemented.")


class DatabaseDocumentRepository(DocumentRepository):
    """
    STUB: PostgreSQL implementation of DocumentRepository.
    Production implementation would use SQLAlchemy ORM.
    """

    def __init__(self):
        print("[DatabaseDocumentRepository] STUB — no DB connected.")

    def save(self, entity: Document) -> None:
        raise NotImplementedError("DatabaseDocumentRepository.save() not yet implemented.")

    def find_by_id(self, entity_id: str) -> Optional[Document]:
        raise NotImplementedError("DatabaseDocumentRepository.find_by_id() not yet implemented.")

    def find_all(self) -> List[Document]:
        raise NotImplementedError("DatabaseDocumentRepository.find_all() not yet implemented.")

    def delete(self, entity_id: str) -> None:
        raise NotImplementedError("DatabaseDocumentRepository.delete() not yet implemented.")

    def exists(self, entity_id: str) -> bool:
        raise NotImplementedError("DatabaseDocumentRepository.exists() not yet implemented.")

    def count(self) -> int:
        raise NotImplementedError("DatabaseDocumentRepository.count() not yet implemented.")

    def find_by_namespace(self, namespace: NamespaceId) -> List[Document]:
        raise NotImplementedError("DatabaseDocumentRepository.find_by_namespace() not yet implemented.")

    def find_by_status(self, status: DocumentStatus) -> List[Document]:
        raise NotImplementedError("DatabaseDocumentRepository.find_by_status() not yet implemented.")

    def find_by_uploader(self, user_id: str) -> List[Document]:
        raise NotImplementedError("DatabaseDocumentRepository.find_by_uploader() not yet implemented.")

    def find_flagged(self) -> List[Document]:
        raise NotImplementedError("DatabaseDocumentRepository.find_flagged() not yet implemented.")
