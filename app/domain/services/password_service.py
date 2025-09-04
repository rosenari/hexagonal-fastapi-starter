"""Password hashing and verification service."""

import bcrypt

from app.domain.value_objects import Password


class PasswordService:
    """Domain service for password hashing and verification."""
    
    def __init__(self, rounds: int = 12) -> None:
        """
        Initialize the password service.
        
        Args:
            rounds: Number of salt rounds for bcrypt (default: 12)
        """
        self.rounds = rounds
    
    def hash_password(self, password: Password) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: The password value object to hash
            
        Returns:
            The hashed password as a string
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.value.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: Password, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: The password value object to verify
            hashed_password: The stored password hash
            
        Returns:
            True if the password matches the hash, False otherwise
        """
        if not hashed_password:
            return False
        
        try:
            return bcrypt.checkpw(
                password.value.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except (ValueError, TypeError):
            # Invalid hash format or other bcrypt errors
            return False