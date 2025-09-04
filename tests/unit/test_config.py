import os
from unittest.mock import patch

import pytest

from app.infrastructure.config import Settings


class TestSettings:
    def test_settings_default_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.environment == "development"
            assert settings.debug is True
            assert settings.api_version == "v1"

    def test_settings_from_env(self) -> None:
        env_vars = {
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "API_VERSION": "v2",
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
            "SECRET_KEY": "test-secret-key",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.environment == "production"
            assert settings.debug is False
            assert settings.api_version == "v2"
            assert settings.database_url == "postgresql://test:test@localhost:5432/test"
            assert settings.secret_key == "test-secret-key"

    def test_settings_database_url_required_in_production(self) -> None:
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "test-secret",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL must be set"):
                Settings()

    def test_settings_secret_key_required_in_production(self) -> None:
        env_vars = {
            "ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="SECRET_KEY must be set"):
                Settings()