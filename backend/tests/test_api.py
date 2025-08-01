"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

# test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#  tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Legal Intel Dashboard API"
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "ai_enabled" in data
    
    def test_upload_no_files(self):
        """Test upload endpoint with no files"""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422  # Validation error
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        files = {"files": ("test.txt", b"text content", "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert len(data["failed_files"]) > 0
        assert "Unsupported file format" in data["failed_files"][0]["error"]
    
    def test_query_empty_question(self):
        """Test query endpoint with empty question"""
        response = client.post("/api/v1/query", json={"question": ""})
        assert response.status_code == 422  # Validation error
    
    def test_query_valid_question(self):
        """Test query endpoint with valid question"""
        response = client.post("/api/v1/query", json={
            "question": "What are the agreement types?"
        })
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert "results" in data
        assert "total_matches" in data
    
    def test_get_documents(self):
        """Test get documents endpoint"""
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_nonexistent_document(self):
        """Test get specific document that doesn't exist"""
        response = client.get("/api/v1/documents/999")
        assert response.status_code == 404
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "agreement_types" in data
        assert "jurisdictions" in data
        assert "industries" in data
        assert "total_documents" in data
        assert "processing_status" in data
    
    def test_dashboard_summary(self):
        """Test dashboard summary endpoint"""
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "completed_documents" in data
        assert "completion_rate" in data
    
    def test_recent_activity(self):
        """Test recent activity endpoint"""
        response = client.get("/api/v1/dashboard/recent-activity")
        assert response.status_code == 200
        data = response.json()
        assert "recent_activity" in data
        assert isinstance(data["recent_activity"], list)