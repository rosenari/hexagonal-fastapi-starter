"""Domain-specific exceptions."""


class DomainError(Exception):
    """Base exception for all domain-related errors."""
    pass


class ValidationError(DomainError):
    """Raised when domain validation fails."""
    pass


class EntityNotFoundError(DomainError):
    """Raised when a requested entity cannot be found."""
    pass


class DuplicateEntityError(DomainError):
    """Raised when trying to create a duplicate entity."""
    pass


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated."""
    pass