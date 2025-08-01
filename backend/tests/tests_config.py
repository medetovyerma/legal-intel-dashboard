"""
Unit tests for configuration module
"""
import os
import pytest
from app.core.config import Settings


def test_default_settings():
    """Test default configuration values"""
    settings = Settings()
    
    assert settings.app_name == "Legal Intel Dashboard"
    assert settings.app_version == "1.0.0"
    assert settings.debug is False
    assert settings.database_url == "sqlite:///./legal_documents.db"
    assert settings.openai_model == "gpt-4o"
    assert settings.max_file_size == 50 * 1024 * 1024
    assert ".pdf" in settings.allowed_extensions
    assert ".docx" in settings.allowed_extensions


def test_settings_from_env(monkeypatch):
    """Test configuration from environment variables"""
    # Set environment variables
    monkeypatch.setenv("APP_NAME", "Test Legal App")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("MAX_FILE_SIZE", "10485760")  # 10MB
    
    settings = Settings()
    
    assert settings.app_name == "Test Legal App"
    assert settings.debug is True
    assert settings.openai_api_key == "test-key-123"
    assert settings.max_file_size == 10485760


def test_upload_directory_creation(tmp_path, monkeypatch):
    """Test that upload directory is created"""
    upload_dir = str(tmp_path / "test_uploads")
    monkeypatch.setenv("UPLOAD_DIR", upload_dir)
    
    # Import after setting env var
    from app.core.config import Settings
    settings = Settings()
    
    assert os.path.exists(upload_dir)