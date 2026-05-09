# All entity-specific repositories extend this base.

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    """
    Generic repository interface defining standard CRUD operations.

    T  = entity type  (e.g. UserAccount, Document)
    ID = identifier type (e.g. str)

    Justification: Using generics avoids duplicating CRUD method signatures
    across every entity repository. Each concrete class only implements
    these operations for its specific entity — no boilerplate repetition.
    """

    @abstractmethod
    def save(self, entity: T) -> None:
        """Create or update an entity in the store."""
        pass

    @abstractmethod
    def find_by_id(self, entity_id: ID) -> Optional[T]:
        """Retrieve a single entity by its unique ID. Returns None if not found."""
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """Retrieve all stored entities."""
        pass

    @abstractmethod
    def delete(self, entity_id: ID) -> None:
        """Remove an entity from the store by its ID."""
        pass

    @abstractmethod
    def exists(self, entity_id: ID) -> bool:
        """Return True if an entity with the given ID exists."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the total number of stored entities."""
        pass
