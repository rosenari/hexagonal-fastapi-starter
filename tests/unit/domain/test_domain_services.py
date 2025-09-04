import pytest

from app.domain.services.password_service import PasswordService
from app.domain.value_objects import Password


class TestPasswordService:
    def test_hash_password(self) -> None:
        password_service = PasswordService()
        password = Password("TestPassword123!")
        
        hashed = password_service.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
    
    def test_hash_password_different_results(self) -> None:
        password_service = PasswordService()
        password = Password("TestPassword123!")
        
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)
        
        # Should produce different hashes due to salt
        assert hash1 != hash2
    
    def test_verify_password_correct(self) -> None:
        password_service = PasswordService()
        password = Password("TestPassword123!")
        
        hashed = password_service.hash_password(password)
        is_valid = password_service.verify_password(password, hashed)
        
        assert is_valid is True
    
    def test_verify_password_incorrect(self) -> None:
        password_service = PasswordService()
        correct_password = Password("TestPassword123!")
        wrong_password = Password("WrongPassword456@")
        
        hashed = password_service.hash_password(correct_password)
        is_valid = password_service.verify_password(wrong_password, hashed)
        
        assert is_valid is False
    
    def test_verify_password_invalid_hash(self) -> None:
        password_service = PasswordService()
        password = Password("TestPassword123!")
        invalid_hash = "not-a-valid-hash"
        
        is_valid = password_service.verify_password(password, invalid_hash)
        
        assert is_valid is False
    
    def test_verify_password_empty_hash(self) -> None:
        password_service = PasswordService()
        password = Password("TestPassword123!")
        
        is_valid = password_service.verify_password(password, "")
        
        assert is_valid is False
    
    def test_hash_multiple_passwords(self) -> None:
        password_service = PasswordService()
        passwords = [
            Password("Password1!"),
            Password("AnotherPass2@"),
            Password("ThirdPassword3#"),
        ]
        
        hashes = []
        for password in passwords:
            hashed = password_service.hash_password(password)
            hashes.append(hashed)
        
        # All hashes should be different
        assert len(set(hashes)) == len(hashes)
        
        # Each password should verify against its own hash
        for password, hashed in zip(passwords, hashes):
            assert password_service.verify_password(password, hashed) is True
        
        # Each password should NOT verify against other hashes
        for i, password in enumerate(passwords):
            for j, hashed in enumerate(hashes):
                if i != j:
                    assert password_service.verify_password(password, hashed) is False