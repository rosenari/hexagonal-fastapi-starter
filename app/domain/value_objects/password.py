"""Password value object."""

import re
from typing import Any

from app.domain.exceptions import ValidationError


class Password:
    """Password value object that ensures strong password requirements."""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    def __init__(self, value: str) -> None:
        self.value = self._validate(value)
    
    def _validate(self, value: str) -> str:
        """Validate the password according to security requirements."""
        if not isinstance(value, str):
            raise ValidationError("Password must be a string")
        
        # Check for empty or whitespace-only password
        if not value or not value.strip():
            raise ValidationError("Password cannot be empty")
        
        # Length requirements
        if len(value) < self.MIN_LENGTH:
            raise ValidationError(f"Password must be at least {self.MIN_LENGTH} characters")
        
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(f"Password must not exceed {self.MAX_LENGTH} characters")
        
        # Strength requirements
        if not re.search(r'[A-Z]', value):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[0-9]', value):
            raise ValidationError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character")
        
        return value
    
    def __eq__(self, other: Any) -> bool:
        """Two passwords are equal if they have the same value."""
        if not isinstance(other, Password):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash based on the password value."""
        return hash(self.value)
    
    def __str__(self) -> str:
        """String representation - password is masked for security."""
        return "Password(***)"
    
    def __repr__(self) -> str:
        """Detailed representation - password is masked for security."""
        return "Password(***)"