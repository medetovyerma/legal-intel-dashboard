"""
API endpoints for document upload and query operations
"""
import os
import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.models.document import Document
from app.schemas.document import UploadResponse, QueryRequest, QueryResponse, DocumentResponse
from app.services.document_processor import DocumentProcessor
from app.services.metadata_extractor import MetadataExtractor
from app.services.query_service import QueryService

logger = logging.getLogger(__name__)

router = APIRouter()
metadata_extractor = MetadataExtractor()
query_service = QueryService()


@router.post("/upload-single")
async def upload_single_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a single document (for testing purposes)
    """
    logger.info(f"Single file upload: {file.filename}, content_type: {file.content_type}")
    
    try:
        # Process single file
        files = [file]
        result = await upload_documents(background_tasks, files, db)
        return result
    except Exception as e:
        logger.error(f"Single file upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple legal documents for processing
    
    Args:
        background_tasks: FastAPI background tasks
        files: List of uploaded files
        db: Database session
        
    Returns:
        Upload response with success/failure information
    """
    logger.info(f"Received upload request with {len(files) if files else 0} files")
    
    if not files or len(files) == 0:
        logger.warning("No files provided in upload request")
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Log file details for debugging
    for i, file in enumerate(files):
        logger.info(f"File {i}: name='{file.filename}', content_type='{file.content_type}', size={file.size if hasattr(file, 'size') else 'unknown'}")
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # Validate file
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in settings.allowed_extensions:
                failed_files.append({
                    "filename": file.filename,
                    "error": f"Unsupported file format: {file_extension}"
                })
                continue
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(settings.upload_dir, unique_filename)
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Validate file size
            file_size = len(content)
            if file_size > settings.max_file_size:
                os.remove(file_path)  # Clean up
                failed_files.append({
                    "filename": file.filename,
                    "error": f"File size ({file_size} bytes) exceeds maximum allowed size"
                })
                continue
            
            # Create database record
            document = Document(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                content_text="",  # Will be filled during processing
                processing_status="pending"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Schedule background processing
            background_tasks.add_task(process_document_background, document.id)
            
            uploaded_files.append(DocumentResponse.model_validate(document))
            
            logger.info(f"Successfully uploaded file: {file.filename} (ID: {document.id})")
            
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            failed_files.append({
                "filename": file.filename,
                "error": f"Upload failed: {str(e)}"
            })
    
    return UploadResponse(
        message=f"Successfully uploaded {len(uploaded_files)} files, {len(failed_files)} failed",
        uploaded_files=uploaded_files,
        failed_files=failed_files
    )


async def process_document_background(document_id: int):
    """
    Background task for processing uploaded documents
    
    Args:
        document_id: ID of the document to process
    """
    # Create new database session for background task
    db = SessionLocal()
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document not found for processing: {document_id}")
            return
        
        logger.info(f"Starting processing of document {document_id}: {document.original_filename}")
        
        # Update status
        document.processing_status = "processing"
        db.commit()
        
        # Extract text from document
        logger.info(f"Extracting text from document {document_id}")
        text_content, success = DocumentProcessor.process_document(document.file_path)
        
        if not success:
            document.processing_status = "failed"
            document.processing_error = "Failed to extract text from document"
            db.commit()
            logger.error(f"Failed to extract text from document {document_id}")
            return
        
        # Update document with extracted text
        document.content_text = text_content
        db.commit()
        logger.info(f"Successfully extracted {len(text_content)} characters from document {document_id}")
        
        # Extract metadata using AI
        logger.info(f"Extracting metadata from document {document_id}")
        metadata, confidence = await metadata_extractor.extract_metadata(
            text_content, 
            document.original_filename
        )
        
        # Update document with metadata
        document.agreement_type = metadata.agreement_type
        document.governing_law = metadata.governing_law
        document.jurisdiction = metadata.jurisdiction
        document.geography = metadata.geography
        document.industry_sector = metadata.industry_sector
        document.confidence_score = confidence
        document.processing_status = "completed"
        
        db.commit()
        
        logger.info(f"Successfully processed document {document_id}: {document.original_filename}")
        logger.info(f"Metadata: type={metadata.agreement_type}, law={metadata.governing_law}, industry={metadata.industry_sector}")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        try:
            if 'document' in locals() and document:
                document.processing_status = "failed"
                document.processing_error = str(e)
                db.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update document status after error: {commit_error}")
    finally:
        db.close()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Process natural language query across all documents
    
    Args:
        query_request: Query request with natural language question
        db: Database session
        
    Returns:
        Structured query response with matching documents
    """
    try:
        # Process the query
        results = await query_service.process_query(query_request.question, db)
        
        logger.info(f"Processed query '{query_request.question}' with {len(results)} results")
        
        return QueryResponse(
            question=query_request.question,
            results=results,
            total_matches=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error processing query '{query_request.question}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all uploaded documents with their processing status
    
    Args:
        skip: Number of documents to skip (for pagination)
        limit: Maximum number of documents to return
        db: Database session
        
    Returns:
        List of documents with metadata
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific document by ID
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Document with metadata
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse.model_validate(document)


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated file
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Success message
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        logger.info(f"Deleted document {document_id}: {document.original_filename}")
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )