from typing import List, Optional
from src.models import UserAccount, Role, AccountStatus
from repositories.interfaces import UserAccountRepository
import uuid


class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class InvalidOperationError(Exception):
    pass


class UserService:
    """
    Service class for UserAccount business operations.
    All persistence is delegated to the injected repository.
    Business rules are enforced here — not in the API or repository.
    """

    def __init__(self, user_repository: UserAccountRepository):
        self._repo = user_repository

    def create_user(self, email: str, role: Role) -> UserAccount:
        """
        Create a new user account.
        Business rule: Email must be unique across all accounts.
        """
        existing = self._repo.find_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError(
                f"A user with email '{email}' already exists."
            )
        user_id = str(uuid.uuid4())
        user = UserAccount(user_id, email, role)
        user.login()  # Activates the account on creation
        self._repo.save(user)
        return user

    def get_user(self, user_id: str) -> UserAccount:
        """Retrieve a user by ID. Raises UserNotFoundError if missing."""
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User '{user_id}' not found.")
        return user

    def get_all_users(self) -> List[UserAccount]:
        """Return all user accounts."""
        return self._repo.find_all()

    def get_users_by_role(self, role: Role) -> List[UserAccount]:
        """Return all users with a specific role."""
        return self._repo.find_by_role(role)

    def update_role(self, user_id: str, new_role: Role) -> UserAccount:
        """
        Update a user's role.
        Business rule: Cannot change the role of a DELETED account.
        """
        user = self.get_user(user_id)
        if user.status == AccountStatus.DELETED:
            raise InvalidOperationError(
                f"Cannot update role of a deleted account: {user_id}"
            )
        user.role = new_role
        self._repo.save(user)
        return user

    def deactivate_user(self, user_id: str) -> UserAccount:
        """
        Deactivate a user account.
        Business rule: Cannot deactivate an already DELETED account.
        """
        user = self.get_user(user_id)
        if user.status == AccountStatus.DELETED:
            raise InvalidOperationError(
                f"Cannot deactivate a deleted account: {user_id}"
            )
        user.deactivate()
        self._repo.save(user)
        return user

    def delete_user(self, user_id: str) -> None:
        """
        Permanently delete a user account.
        Business rule: User must exist.
        """
        user = self.get_user(user_id)
        user.delete()
        self._repo.save(user)

    def unlock_user(self, user_id: str) -> UserAccount:
        """
        Unlock a locked user account.
        Business rule: Only LOCKED accounts can be unlocked.
        """
        user = self.get_user(user_id)
        if user.status != AccountStatus.LOCKED:
            raise InvalidOperationError(
                f"Account '{user_id}' is not locked (status: {user.status.value})."
            )
        user.unlock_account()
        self._repo.save(user)
        return user

    def record_failed_login(self, email: str) -> UserAccount:
        """
        Record a failed login attempt by email.
        Business rule: Account locks after 5 consecutive failures.
        """
        user = self._repo.find_by_email(email)
        if user is None:
            raise UserNotFoundError(f"No user found with email '{email}'.")
        user.record_failed_login()
        self._repo.save(user)
        return user

    def count_users(self) -> int:
        """Return the total number of registered users."""
        return self._repo.count()
