"""
API endpoints for dashboard statistics
"""
import logging
from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DashboardStats

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics and analytics for all processed documents
    
    Args:
        db: Database session
        
    Returns:
        Dashboard statistics including counts and aggregations
    """
    try:
        # Get all completed documents
        documents = db.query(Document).filter(
            Document.processing_status == "completed"
        ).all()
        
        # Initialize counters
        agreement_types = defaultdict(int)
        jurisdictions = defaultdict(int)
        industries = defaultdict(int)
        processing_status = defaultdict(int)
        
        # Count all documents by processing status
        all_documents = db.query(Document).all()
        for doc in all_documents:
            processing_status[doc.processing_status] += 1
        
        # Aggregate metadata for completed documents
        for doc in documents:
            if doc.agreement_type:
                agreement_types[doc.agreement_type] += 1
            
            if doc.governing_law:
                jurisdictions[doc.governing_law] += 1
            elif doc.jurisdiction:
                jurisdictions[doc.jurisdiction] += 1
            
            if doc.industry_sector:
                industries[doc.industry_sector] += 1
        
        # Convert defaultdicts to regular dicts and sort by count (descending)
        agreement_types_sorted = dict(sorted(
            agreement_types.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        jurisdictions_sorted = dict(sorted(
            jurisdictions.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        industries_sorted = dict(sorted(
            industries.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        processing_status_dict = dict(processing_status)
        
        total_documents = len(all_documents)
        
        logger.info(f"Generated dashboard stats for {total_documents} total documents")
        
        return DashboardStats(
            agreement_types=agreement_types_sorted,
            jurisdictions=jurisdictions_sorted,
            industries=industries_sorted,
            total_documents=total_documents,
            processing_status=processing_status_dict
        )
        
    except Exception as e:
        logger.error(f"Error generating dashboard stats: {str(e)}")
        # Return empty stats rather than failing
        return DashboardStats(
            agreement_types={},
            jurisdictions={},
            industries={},
            total_documents=0,
            processing_status={}
        )


@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get a quick summary of key dashboard metrics
    
    Args:
        db: Database session
        
    Returns:
        Summary statistics
    """
    try:
        # Get counts using database aggregation for better performance
        total_documents = db.query(func.count(Document.id)).scalar()
        completed_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == "completed"
        ).scalar()
        
        pending_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == "pending"
        ).scalar()
        
        processing_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == "processing"
        ).scalar()
        
        failed_documents = db.query(func.count(Document.id)).filter(
            Document.processing_status == "failed"
        ).scalar()
        
        # Get unique counts
        unique_agreement_types = db.query(func.count(func.distinct(Document.agreement_type))).filter(
            Document.agreement_type.isnot(None),
            Document.processing_status == "completed"
        ).scalar()
        
        unique_jurisdictions = db.query(func.count(func.distinct(Document.governing_law))).filter(
            Document.governing_law.isnot(None),
            Document.processing_status == "completed"
        ).scalar()
        
        unique_industries = db.query(func.count(func.distinct(Document.industry_sector))).filter(
            Document.industry_sector.isnot(None),
            Document.processing_status == "completed"
        ).scalar()
        
        return {
            "total_documents": total_documents,
            "completed_documents": completed_documents,
            "pending_documents": pending_documents,
            "processing_documents": processing_documents,
            "failed_documents": failed_documents,
            "completion_rate": round((completed_documents / total_documents * 100), 2) if total_documents > 0 else 0,
            "unique_agreement_types": unique_agreement_types,
            "unique_jurisdictions": unique_jurisdictions,
            "unique_industries": unique_industries
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        return {
            "total_documents": 0,
            "completed_documents": 0,
            "pending_documents": 0,
            "processing_documents": 0,
            "failed_documents": 0,
            "completion_rate": 0,
            "unique_agreement_types": 0,
            "unique_jurisdictions": 0,
            "unique_industries": 0
        }


@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent document processing activity
    
    Args:
        limit: Number of recent documents to return
        db: Database session
        
    Returns:
        List of recently processed documents
    """
    try:
        recent_documents = db.query(Document).order_by(
            Document.created_at.desc()
        ).limit(limit).all()
        
        activity_list = []
        for doc in recent_documents:
            activity_list.append({
                "id": doc.id,
                "filename": doc.original_filename,
                "status": doc.processing_status,
                "agreement_type": doc.agreement_type,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
            })
        
        return {"recent_activity": activity_list}
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return {"recent_activity": []}