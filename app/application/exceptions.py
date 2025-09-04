"""Application layer exceptions."""


class ApplicationError(Exception):
    """Base exception for application layer."""
    pass


class UserNotFoundError(ApplicationError):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(ApplicationError):
    """Raised when trying to create a user that already exists."""
    pass