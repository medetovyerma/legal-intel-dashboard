"""
SQLAlchemy model for document storage
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    """
    Document model for storing legal document information and metadata
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_text = Column(Text, nullable=False)

    
    # Extracted metadata fields
    agreement_type = Column(String(100), index=True)
    governing_law = Column(String(100), index=True)
    jurisdiction = Column(String(100), index=True)
    geography = Column(String(200))
    industry_sector = Column(String(100), index=True)
    
    # Process metadata
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # AI confidence in metadata extraction
    
    #timestemp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type='{self.agreement_type}')>"