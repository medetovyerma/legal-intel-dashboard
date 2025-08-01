#!/usr/bin/env python3
"""
Simple test to verify backend is working
"""
import sys
import os

# Add the app directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported without errors"""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Config imported successfully")
        
        from app.core.database import get_db, SessionLocal, create_tables
        print("✅ Database imported successfully")
        
        from app.models.document import Document
        print("✅ Models imported successfully")
        
        from app.schemas.document import DocumentResponse, UploadResponse
        print("✅ Schemas imported successfully")
        
        from app.services.document_processor import DocumentProcessor
        print("✅ Document processor imported successfully")
        
        from app.services.metadata_extractor import MetadataExtractor
        print("✅ Metadata extractor imported successfully")
        
        from app.api.documents import router
        print("✅ API endpoints imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database():
    """Test database connection and table creation"""
    print("\nTesting database...")
    
    try:
        from app.core.database import create_tables, SessionLocal
        from app.models.document import Document
        
        # Create tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Test database session
        db = SessionLocal()
        result = db.query(Document).count()
        db.close()
        print(f"✅ Database connection successful (found {result} documents)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Upload dir: {settings.upload_dir}")
        print(f"✅ Max file size: {settings.max_file_size / (1024*1024):.1f} MB")
        print(f"✅ OpenAI configured: {'Yes' if settings.openai_api_key else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Legal Intel Dashboard Backend\n")
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_config():
        tests_passed += 1
        
    if test_database():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Backend is ready to run.")
        print("\nTo start the server:")
        print("uvicorn app.main:app --reload")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)