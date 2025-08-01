"""
metadata extraction service (using OpenAI GPT-4o)
"""
import json
import logging
from typing import Dict, Optional, Tuple
from openai import OpenAI

from app.core.config import settings
from app.schemas.document import DocumentMetadata

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Service for extracting structured metadata from legal documents using AI"""
    
    def __init__(self):
        """Initialize the metadata extractor with OpenAI client"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. Metadata extraction will use fallback method.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def extract_metadata(self, document_text: str, filename: str) -> Tuple[DocumentMetadata, float]:
        """
        Extract metadata from document text using AI or fallback method
        
        Args:
            document_text: Full text content of the document
            filename: Original filename for context
            
        Returns:
            Tuple of (DocumentMetadata, confidence_score)
        """
        if self.client and settings.openai_api_key:
            return await self._extract_with_openai(document_text, filename)
        else:
            return await self._extract_with_fallback(document_text, filename)
    
    async def _extract_with_openai(self, document_text: str, filename: str) -> Tuple[DocumentMetadata, float]:
        """
        Extract metadata using OpenAI GPT-4o
        
        Args:
            document_text: Document content
            filename: Document filename
            
        Returns:
            Tuple of (DocumentMetadata, confidence_score)
        """
        try:
            # Truncate text if too long (keep first 6000 chars to stay within token limits)
            truncated_text = document_text[:6000] + "..." if len(document_text) > 6000 else document_text
            
            system_prompt = """You are a legal document analyst. Extract structured metadata from legal documents.

Analyze the provided legal document and extract the following information in JSON format:
- agreement_type: Type of legal agreement (e.g., "NDA", "MSA", "Service Agreement", "Franchise Agreement", "Employment Contract", "Licensing Agreement")
- governing_law: Governing law or jurisdiction (e.g., "UAE", "UK", "Delaware", "New York", "California")
- jurisdiction: Legal jurisdiction for disputes (e.g., "UAE", "England and Wales", "Delaware Courts")
- geography: Geographic regions mentioned (e.g., "Middle East", "Europe", "North America", "Asia-Pacific")
- industry_sector: Industry or business sector (e.g., "Technology", "Oil & Gas", "Healthcare", "Financial Services", "Real Estate")

Return ONLY a valid JSON object with these fields. If information is not clearly stated, use null for that field.
Be precise and use standardized terms. For governing_law and jurisdiction, prefer country/state names over city names."""

            user_prompt = f"""Document filename: {filename}

Document content:
{truncated_text}

Extract the metadata in JSON format:"""

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=300
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Remove any markdown formatting
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                
                metadata_dict = json.loads(response_text)
                
                # Validate and create DocumentMetadata
                metadata = DocumentMetadata(
                    agreement_type=metadata_dict.get("agreement_type"),
                    governing_law=metadata_dict.get("governing_law"),
                    jurisdiction=metadata_dict.get("jurisdiction"),
                    geography=metadata_dict.get("geography"),
                    industry_sector=metadata_dict.get("industry_sector"),
                    confidence_score=0.85  # High confidence for AI extraction
                )
                
                logger.info(f"Successfully extracted metadata for {filename}")
                return metadata, 0.85
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from OpenAI response for {filename}: {e}")
                logger.debug(f"Raw response: {response_text}")
                return await self._extract_with_fallback(document_text, filename)
                
        except Exception as e:
            logger.error(f"Error in OpenAI metadata extraction for {filename}: {e}")
            return await self._extract_with_fallback(document_text, filename)
    
    async def _extract_with_fallback(self, document_text: str, filename: str) -> Tuple[DocumentMetadata, float]:
        """
        Fallback metadata extraction using keyword matching
        
        Args:
            document_text: Document content
            filename: Document filename
            
        Returns:
            Tuple of (DocumentMetadata, confidence_score)
        """
        logger.info(f"Using fallback metadata extraction for {filename}")
        
        text_lower = document_text.lower()
        
        # Agreement type detection
        agreement_type = self._detect_agreement_type(text_lower, filename.lower())
        
        # Governing law detection
        governing_law = self._detect_governing_law(text_lower)
        
        # Geography detection
        geography = self._detect_geography(text_lower)
        
        # Industry sector detection
        industry_sector = self._detect_industry_sector(text_lower)
        
        metadata = DocumentMetadata(
            agreement_type=agreement_type,
            governing_law=governing_law,
            jurisdiction=governing_law,  # Use same as governing law for simplicity
            geography=geography,
            industry_sector=industry_sector,
            confidence_score=0.6  # Lower confidence for keyword-based extraction
        )
        
        return metadata, 0.6
    
    def _detect_agreement_type(self, text: str, filename: str) -> Optional[str]:
        """Detect agreement type using keywords"""
        agreement_patterns = {
            "NDA": ["non-disclosure", "confidentiality", "nda"],
            "MSA": ["master service", "msa", "master agreement"],
            "Service Agreement": ["service agreement", "services agreement"],
            "Employment Contract": ["employment", "employee", "employment agreement"],
            "Franchise Agreement": ["franchise", "franchisee", "franchisor"],
            "Licensing Agreement": ["license", "licensing", "licensed"],
            "Supply Agreement": ["supply", "supplier", "procurement"],
            "Partnership Agreement": ["partnership", "partner", "joint venture"]
        }
        
        # Check filename first
        for agreement_type, keywords in agreement_patterns.items():
            if any(keyword in filename for keyword in keywords):
                return agreement_type
        
        # Check document content
        for agreement_type, keywords in agreement_patterns.items():
            if any(keyword in text for keyword in keywords):
                return agreement_type
        
        return None
    
    def _detect_governing_law(self, text: str) -> Optional[str]:
        """Detect governing law using keywords"""
        law_patterns = {
            "UAE": ["uae", "united arab emirates", "dubai", "abu dhabi"],
            "UK": ["england", "wales", "united kingdom", "english law"],
            "Delaware": ["delaware", "delaware law"],
            "New York": ["new york", "ny law", "new york law"],
            "California": ["california", "california law", "ca law"],
            "Singapore": ["singapore", "singapore law"],
            "Germany": ["germany", "german law", "deutschland"]
        }
        
        for jurisdiction, keywords in law_patterns.items():
            if any(f"governed by {keyword}" in text or f"laws of {keyword}" in text 
                   for keyword in keywords):
                return jurisdiction
            # Also check for general mentions
            if any(keyword in text for keyword in keywords):
                return jurisdiction
        
        return None
    
    def _detect_geography(self, text: str) -> Optional[str]:
        """Detect geographic regions mentioned"""
        geo_patterns = {
            "Middle East": ["middle east", "gulf", "gcc", "arab"],
            "Europe": ["europe", "european", "eu"],
            "North America": ["north america", "usa", "canada", "united states"],
            "Asia-Pacific": ["asia", "pacific", "apac", "asian"]
        }
        
        for region, keywords in geo_patterns.items():
            if any(keyword in text for keyword in keywords):
                return region
        
        return None
    
    def _detect_industry_sector(self, text: str) -> Optional[str]:
        """Detect industry sector using keywords"""
        industry_patterns = {
            "Technology": ["software", "technology", "tech", "digital", "it", "saas"],
            "Oil & Gas": ["oil", "gas", "petroleum", "energy", "drilling"],
            "Healthcare": ["health", "medical", "pharma", "hospital", "healthcare"],
            "Financial Services": ["bank", "finance", "financial", "investment", "credit"],
            "Real Estate": ["real estate", "property", "construction", "building"],
            "Manufacturing": ["manufacturing", "production", "factory", "industrial"],
            "Retail": ["retail", "commerce", "shopping", "consumer goods"]
        }
        
        for industry, keywords in industry_patterns.items():
            if any(keyword in text for keyword in keywords):
                return industry
        
        return None