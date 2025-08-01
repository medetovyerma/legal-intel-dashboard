"""
Pydantic schemas for request/response validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Schema for extracted document metadata"""
    agreement_type: Optional[str] = None
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    geography: Optional[str] = None
    industry_sector: Optional[str] = None
    confidence_score: Optional[float] = None


class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    original_filename: str
    file_size: int


class DocumentCreate(DocumentBase):
    """Schema for creating a new document"""
    content_text: str
    file_path: str


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    processing_status: str
    processing_error: Optional[str] = None
    agreement_type: Optional[str] = None
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    geography: Optional[str] = None
    industry_sector: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    """Schema for upload response"""
    message: str
    uploaded_files: List[DocumentResponse]
    failed_files: List[Dict[str, str]] = []


class QueryRequest(BaseModel):
    """Schema for natural language query request"""
    question: str = Field(..., min_length=3, max_length=500)


class QueryResult(BaseModel):
    """Schema for individual query result row"""
    document: str
    data: Dict[str, Any]


class QueryResponse(BaseModel):
    """Schema for query response"""
    question: str
    results: List[QueryResult]
    total_matches: int


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    agreement_types: Dict[str, int]
    jurisdictions: Dict[str, int]
    industries: Dict[str, int]
    total_documents: int
    processing_status: Dict[str, int]