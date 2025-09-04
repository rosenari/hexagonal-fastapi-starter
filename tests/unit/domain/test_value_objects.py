import pytest

from app.domain.exceptions import ValidationError
from app.domain.value_objects import Email, Password


class TestEmail:
    def test_create_valid_email(self) -> None:
        email = Email("test@example.com")
        assert email.value == "test@example.com"
    
    def test_create_email_with_different_domains(self) -> None:
        emails = [
            "user@gmail.com",
            "admin@company.org",
            "test@subdomain.example.com",
            "user.name@domain-name.co.uk",
        ]
        
        for email_str in emails:
            email = Email(email_str)
            assert email.value == email_str
    
    def test_email_validation_invalid_format(self) -> None:
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            "",
            "   ",
        ]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError, match="Invalid email format"):
                Email(invalid_email)
    
    def test_email_normalization(self) -> None:
        # Email should be normalized to lowercase
        email = Email("TEST@EXAMPLE.COM")
        assert email.value == "test@example.com"
    
    def test_email_strip_whitespace(self) -> None:
        email = Email("  test@example.com  ")
        assert email.value == "test@example.com"
    
    def test_email_equality(self) -> None:
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")
        
        assert email1 == email2
        assert email1 != email3
    
    def test_email_hash(self) -> None:
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        
        # Same emails should have same hash
        assert hash(email1) == hash(email2)
        
        # Can be used in sets
        email_set = {email1, email2}
        assert len(email_set) == 1
    
    def test_email_string_representation(self) -> None:
        email = Email("test@example.com")
        assert str(email) == "test@example.com"
        assert repr(email) == "Email('test@example.com')"


class TestPassword:
    def test_create_valid_password(self) -> None:
        password = Password("ValidPassword123!")
        assert password.value == "ValidPassword123!"
    
    def test_password_minimum_length(self) -> None:
        with pytest.raises(ValidationError, match="Password must be at least 8 characters"):
            Password("short")
    
    def test_password_maximum_length(self) -> None:
        long_password = "a" * 129  # 129 characters
        with pytest.raises(ValidationError, match="Password must not exceed 128 characters"):
            Password(long_password)
    
    def test_password_requires_uppercase(self) -> None:
        with pytest.raises(ValidationError, match="Password must contain at least one uppercase letter"):
            Password("lowercase123!")
    
    def test_password_requires_lowercase(self) -> None:
        with pytest.raises(ValidationError, match="Password must contain at least one lowercase letter"):
            Password("UPPERCASE123!")
    
    def test_password_requires_digit(self) -> None:
        with pytest.raises(ValidationError, match="Password must contain at least one digit"):
            Password("NoDigitsHere!")
    
    def test_password_requires_special_character(self) -> None:
        with pytest.raises(ValidationError, match="Password must contain at least one special character"):
            Password("NoSpecialChar123")
    
    def test_empty_password(self) -> None:
        with pytest.raises(ValidationError, match="Password cannot be empty"):
            Password("")
    
    def test_whitespace_password(self) -> None:
        with pytest.raises(ValidationError, match="Password cannot be empty"):
            Password("   ")
    
    def test_valid_passwords(self) -> None:
        valid_passwords = [
            "ValidPass123!",
            "AnotherGood1@",
            "Strong#Pass9",
            "MySecure$Pass2",
        ]
        
        for pwd in valid_passwords:
            password = Password(pwd)
            assert password.value == pwd
    
    def test_password_equality(self) -> None:
        password1 = Password("SamePass123!")
        password2 = Password("SamePass123!")
        password3 = Password("DifferentPass456@")
        
        assert password1 == password2
        assert password1 != password3
    
    def test_password_hash(self) -> None:
        password1 = Password("SamePass123!")
        password2 = Password("SamePass123!")
        
        # Same passwords should have same hash
        assert hash(password1) == hash(password2)
    
    def test_password_string_representation(self) -> None:
        password = Password("MyPassword123!")
        # Password value should be masked in string representation
        assert str(password) == "Password(***)"
        assert repr(password) == "Password(***)"
    
    def test_password_no_whitespace_trim(self) -> None:
        # Passwords should preserve leading/trailing whitespace if they exist
        # and still pass validation
        password = Password(" ValidPass123! ")
        assert password.value == " ValidPass123! "