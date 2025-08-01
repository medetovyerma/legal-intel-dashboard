"""
Natural language query service for searching and analyzing legal documents
"""
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.models.document import Document
from app.schemas.document import QueryResult

logger = logging.getLogger(__name__)


class QueryService:
    """Service for processing natural language queries against legal documents"""
    
    def __init__(self):
        """Initialize the query service with OpenAI client"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. Queries will use fallback method.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def process_query(self, question: str, db: Session) -> List[QueryResult]:
        """
        Process natural language query and return structured results
        
        Args:
            question: Natural language question
            db: Database session
            
        Returns:
            List of QueryResult objects
        """
        # Get all documents from database
        documents = db.query(Document).filter(Document.processing_status == "completed").all()
        
        if not documents:
            logger.warning("No processed documents found for query")
            return []
        
        if self.client and settings.openai_api_key:
            return await self._process_with_openai(question, documents)
        else:
            return await self._process_with_fallback(question, documents)
    
    async def _process_with_openai(self, question: str, documents: List[Document]) -> List[QueryResult]:
        """
        Process query using OpenAI GPT-4o
        
        Args:
            question: Natural language question
            documents: List of documents to search
            
        Returns:
            List of QueryResult objects
        """
        try:
            # Prepare document context for AI
            document_context = self._prepare_document_context(documents)
            
            system_prompt = """You are a legal document analyst. You help users find information across a collection of legal documents by answering natural language questions.

Given a question and a collection of legal documents with their metadata, analyze which documents are relevant and extract the requested information.

Return your response as a JSON array where each object represents a matching document with the following structure:
{
  "document": "filename",
  "data": {
    "key1": "value1",
    "key2": "value2"
  }
}

The "data" object should contain the specific information requested in the question. Use clear, descriptive keys that match what was asked.

Examples:
- For "Which agreements are governed by UAE law?": {"governing_law": "UAE", "agreement_type": "NDA"}
- For "What industries are covered?": {"industry_sector": "Technology", "agreement_type": "Service Agreement"}
- For "Show all NDAs": {"agreement_type": "NDA", "jurisdiction": "Delaware"}

Only include documents that actually match the question. If no documents match, return an empty array."""

            user_prompt = f"""Question: {question}

Available documents:
{document_context}

Analyze the documents and return matching results in JSON format:"""

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                
                results_data = json.loads(response_text)
                
                # Convert to QueryResult objects
                query_results = []
                for result in results_data:
                    if isinstance(result, dict) and "document" in result and "data" in result:
                        query_results.append(QueryResult(
                            document=result["document"],
                            data=result["data"]
                        ))
                
                logger.info(f"Successfully processed query with {len(query_results)} results")
                return query_results
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from OpenAI response: {e}")
                logger.debug(f"Raw response: {response_text}")
                return await self._process_with_fallback(question, documents)
                
        except Exception as e:
            logger.error(f"Error in OpenAI query processing: {e}")
            return await self._process_with_fallback(question, documents)
    
    async def _process_with_fallback(self, question: str, documents: List[Document]) -> List[QueryResult]:
        """
        Fallback query processing using keyword matching
        
        Args:
            question: Natural language question
            documents: List of documents to search
            
        Returns:
            List of QueryResult objects
        """
        logger.info("Using fallback query processing")
        
        question_lower = question.lower()
        results = []
        
        # Analyze question to determine what information to return
        return_fields = self._analyze_question_intent(question_lower)
        
        for doc in documents:
            if self._document_matches_query(doc, question_lower):
                data = {}
                
                # Include requested fields
                for field in return_fields:
                    value = getattr(doc, field, None)
                    if value:
                        # Convert field name to human-readable format
                        readable_key = field.replace('_', ' ').title()
                        data[readable_key] = value
                
                if data:  # Only include if we have relevant data
                    results.append(QueryResult(
                        document=doc.original_filename,
                        data=data
                    ))
        
        return results
    
    def _prepare_document_context(self, documents: List[Document]) -> str:
        """
        Prepare document context for AI processing
        
        Args:
            documents: List of documents
            
        Returns:
            Formatted string with document information
        """
        context_lines = []
        
        for doc in documents:
            doc_info = f"Filename: {doc.original_filename}"
            
            metadata_parts = []
            if doc.agreement_type:
                metadata_parts.append(f"Type: {doc.agreement_type}")
            if doc.governing_law:
                metadata_parts.append(f"Governing Law: {doc.governing_law}")
            if doc.jurisdiction:
                metadata_parts.append(f"Jurisdiction: {doc.jurisdiction}")
            if doc.geography:
                metadata_parts.append(f"Geography: {doc.geography}")
            if doc.industry_sector:
                metadata_parts.append(f"Industry: {doc.industry_sector}")
            
            if metadata_parts:
                doc_info += f" | {' | '.join(metadata_parts)}"
            
            # Include a snippet of content for context (first 200 chars)
            content_snippet = doc.content_text[:200].replace('\n', ' ').strip()
            if len(doc.content_text) > 200:
                content_snippet += "..."
            doc_info += f" | Content: {content_snippet}"
            
            context_lines.append(doc_info)
        
        return "\n".join(context_lines)
    
    def _analyze_question_intent(self, question: str) -> List[str]:
        """
        Analyze question to determine what fields to return
        
        Args:
            question: Lowercased question
            
        Returns:
            List of field names to include in response
        """
        # Default fields to always include
        base_fields = ["agreement_type"]
        
        # Field mapping based on question keywords
        field_keywords = {
            "governing_law": ["law", "governed", "governing", "jurisdiction", "legal"],
            "jurisdiction": ["jurisdiction", "court", "dispute", "legal"],
            "geography": ["geography", "region", "location", "country", "where"],
            "industry_sector": ["industry", "sector", "business", "field"],
            "agreement_type": ["type", "agreement", "contract", "kind"]
        }
        
        detected_fields = set(base_fields)
        
        for field, keywords in field_keywords.items():
            if any(keyword in question for keyword in keywords):
                detected_fields.add(field)
        
        return list(detected_fields)
    
    def _document_matches_query(self, document: Document, question: str) -> bool:
        """
        Check if document matches the query using keyword matching
        
        Args:
            document: Document to check
            question: Lowercased question
            
        Returns:
            True if document matches the query
        """
        # Check for specific filters in the question
        
        # Governing law filters
        if any(term in question for term in ["uae", "emirates", "dubai"]):
            if not document.governing_law or "uae" not in document.governing_law.lower():
                return False
        
        if any(term in question for term in ["uk", "england", "british"]):
            if not document.governing_law or "uk" not in document.governing_law.lower():
                return False
        
        # Agreement type filters
        if "nda" in question or "non-disclosure" in question:
            if not document.agreement_type or "nda" not in document.agreement_type.lower():
                return False
        
        if "msa" in question or "master service" in question:
            if not document.agreement_type or "msa" not in document.agreement_type.lower():
                return False
        
        # Industry filters
        if any(term in question for term in ["technology", "tech", "software"]):
            if not document.industry_sector or "technology" not in document.industry_sector.lower():
                return False
        
        if any(term in question for term in ["oil", "gas", "energy"]):
            if not document.industry_sector or not any(term in document.industry_sector.lower() for term in ["oil", "gas", "energy"]):
                return False
        
        return True