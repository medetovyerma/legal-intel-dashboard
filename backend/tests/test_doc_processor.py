"""
Unit tests for document processor service
"""
import os
import pytest
from unittest.mock import patch, mock_open
from app.services.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class"""
    
    def test_validate_file_success(self, tmp_path):
        """Test successful file validation"""
        # Create a test file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")
        
        is_valid, error = DocumentProcessor.validate_file(
            str(test_file), 
            max_size=1024 * 1024  # 1MB
        )
        
        assert is_valid is True
        assert error is None
    
    def test_validate_file_size_exceeded(self, tmp_path):
        """Test file size validation failure"""
        # Create a test file
        test_file = tmp_path / "large.pdf"
        test_file.write_bytes(b"x" * 1000)  # 1KB file
        
        is_valid, error = DocumentProcessor.validate_file(
            str(test_file), 
            max_size=500  # 500 bytes max
        )
        
        assert is_valid is False
        assert "exceeds maximum allowed size" in error
    