"""Email value object."""

import re
from typing import Any

from app.domain.exceptions import ValidationError


class Email:
    """Email value object that ensures valid email format."""
    
    # More strict email regex that prevents consecutive dots
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9._%-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, value: str) -> None:
        self.value = self._validate_and_normalize(value)
    
    def _validate_and_normalize(self, value: str) -> str:
        """Validate and normalize the email address."""
        if not isinstance(value, str):
            raise ValidationError("Email must be a string")
        
        # Strip whitespace and convert to lowercase
        normalized = value.strip().lower()
        
        if not normalized:
            raise ValidationError("Invalid email format")
        
        # Additional validation checks
        if normalized.startswith('.') or normalized.startswith('@'):
            raise ValidationError("Invalid email format")
        
        if normalized.endswith('.') or normalized.endswith('@'):
            raise ValidationError("Invalid email format")
        
        if '..' in normalized:
            raise ValidationError("Invalid email format")
        
        # Check basic structure
        if '@' not in normalized:
            raise ValidationError("Invalid email format")
        
        parts = normalized.split('@')
        if len(parts) != 2:
            raise ValidationError("Invalid email format")
        
        local_part, domain_part = parts
        if not local_part or not domain_part:
            raise ValidationError("Invalid email format")
        
        # Domain must have at least one dot
        if '.' not in domain_part:
            raise ValidationError("Invalid email format")
        
        if not self.EMAIL_PATTERN.match(normalized):
            raise ValidationError("Invalid email format")
        
        return normalized
    
    def __eq__(self, other: Any) -> bool:
        """Two emails are equal if they have the same value."""
        if not isinstance(other, Email):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash based on the email value."""
        return hash(self.value)
    
    def __str__(self) -> str:
        """String representation of the email."""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation of the email."""
        return f"Email('{self.value}')"