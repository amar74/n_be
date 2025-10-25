import time
import asyncio
from typing import Dict, Any, List, Optional
from app.schemas.data_enrichment import (
    AccountEnhancementRequest, AccountEnhancementResponse, 
    SuggestionValue, AddressValidationRequest, AddressValidationResponse,
    IndustrySuggestionRequest, IndustrySuggestionResponse
)
from app.utils.scraper import scrape_text_with_bs4
from app.utils.exceptions import MegapolisHTTPException
from app.utils.logger import logger
from app.environment import environment


class DataEnrichmentService:
    
    def __init__(self):
        # Disable AI by default due to DNS/network issues
        self.ai_enabled = False
        self.cache = {}
        self.timeout = 10  # 10 seconds timeout for scraper-only approach
        logger.info("AI enhancement disabled, using scraper-only approach")
    
    def disable_ai_enhancement(self):
        self.ai_enabled = False
        logger.info("AI enhancement disabled, will use fallback data")
    
    def enable_ai_enhancement(self):
        self.ai_enabled = True
        logger.info("AI enhancement enabled")
    
    def _extract_basic_info_from_website(self, website_content: str, website_url: str) -> Dict[str, Any]:
        """Enhanced scraper-only data extraction without AI"""
        import re
        from urllib.parse import urlparse
        
        # Extract company name from title, h1, or domain
        company_name = "Unknown Company"
        
        # Try to get from title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', website_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title_text = title_match.group(1).strip()
            # Clean up the title - remove common suffixes
            title_text = re.sub(r'\s*[-|]\s*(Home|Welcome|Official|Website|Site).*$', '', title_text, flags=re.IGNORECASE)
            company_name = re.sub(r'[^\w\s-]', '', title_text).strip()
            if len(company_name) > 50:
                company_name = company_name[:50] + "..."
        
        # If no good title, try h1 tag
        if company_name == "Unknown Company" or len(company_name) < 3:
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', website_content, re.IGNORECASE | re.DOTALL)
            if h1_match:
                h1_text = h1_match.group(1).strip()
                company_name = re.sub(r'[^\w\s-]', '', h1_text).strip()
                if len(company_name) > 50:
                    company_name = company_name[:50] + "..."
        
        # If still no good name, use domain
        if company_name == "Unknown Company" or len(company_name) < 3:
            domain = urlparse(website_url).netloc
            if domain:
                company_name = domain.replace('www.', '').replace('.com', '').replace('.org', '').replace('.net', '')
                company_name = company_name.replace('-', ' ').replace('_', ' ').title()
        
        # Extract email addresses with better patterns
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        ]
        emails = []
        for pattern in email_patterns:
            emails.extend(re.findall(pattern, website_content, re.IGNORECASE))
        
        # Filter out common non-business emails
        business_emails = [email for email in emails if not any(domain in email.lower() for domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])]
        contact_email = business_emails[0] if business_emails else (emails[0] if emails else "Unknown")
        
        # Extract phone numbers with multiple formats
        phone_patterns = [
            r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'(\+1\s?)?([0-9]{3})[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\(([0-9]{3})\)\s?([0-9]{3})[-.\s]?([0-9]{4})',
        ]
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, website_content))
        
        contact_phone = "Unknown"
        if phones:
            phone_match = phones[0]
            if len(phone_match) >= 3:
                contact_phone = f"({phone_match[-3]}) {phone_match[-2]}-{phone_match[-1]}"
        
        # Extract address with better patterns
        address_patterns = [
            r'(\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Circle|Ct|Place|Pl))',
            r'(\d+\s+[A-Za-z0-9\s,.-]+(?:Suite|Ste|Unit|Apt|#)\s*\d*)',
            r'([A-Za-z0-9\s,.-]+,\s*[A-Za-z]{2}\s+\d{5}(?:-\d{4})?)',  # City, State ZIP
        ]
        addresses = []
        for pattern in address_patterns:
            addresses.extend(re.findall(pattern, website_content, re.IGNORECASE))
        
        address = addresses[0] if addresses else "Unknown"
        
        # Enhanced industry detection
        industry = "Technology"
        content_lower = website_content.lower()
        
        industry_keywords = {
            "Sports & Fitness": ['sports', 'fitness', 'athletic', 'gym', 'workout', 'training', 'exercise'],
            "Healthcare": ['health', 'medical', 'hospital', 'clinic', 'doctor', 'physician', 'healthcare'],
            "Finance": ['finance', 'banking', 'investment', 'financial', 'bank', 'credit', 'loan'],
            "Education": ['education', 'school', 'university', 'learning', 'academy', 'college', 'student'],
            "Retail": ['retail', 'shop', 'store', 'commerce', 'shopping', 'market', 'buy'],
            "Technology": ['tech', 'software', 'app', 'digital', 'computer', 'programming', 'development'],
            "Real Estate": ['real estate', 'property', 'housing', 'home', 'apartment', 'rental'],
            "Food & Beverage": ['restaurant', 'food', 'cafe', 'dining', 'catering', 'chef', 'kitchen'],
            "Automotive": ['auto', 'car', 'vehicle', 'automotive', 'garage', 'repair', 'mechanic'],
            "Legal": ['law', 'legal', 'attorney', 'lawyer', 'court', 'justice', 'legal services'],
        }
        
        for industry_name, keywords in industry_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                industry = industry_name
                break
        
        # Extract company size based on content analysis
        company_size = "Small"
        if any(word in content_lower for word in ['enterprise', 'corporation', 'global', 'international', 'worldwide']):
            company_size = "Large"
        elif any(word in content_lower for word in ['team', 'employees', 'staff', 'company', 'organization']):
            company_size = "Medium"
        
        return {
            "company_name": company_name,
            "industry": industry,
            "company_size": company_size,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "address": address
        }
    
    async def enhance_account_data(
        self, 
        request: AccountEnhancementRequest
    ) -> AccountEnhancementResponse:
        start_time = time.time()
        
        logger.info("Using enhanced scraper-only approach for data extraction")
        logger.info(f"Processing website: {request.company_website}")
        
        try:
            # Scrape website content
            scraped_data = await scrape_text_with_bs4(str(request.company_website))
            if "error" in scraped_data:
                raise MegapolisHTTPException(
                    status_code=400,
                    message=f"Failed to scrape website: {scraped_data['error']}"
                )
            
            logger.info(f"Website content length: {len(scraped_data.get('text', ''))} characters")
            
            # Use enhanced scraper extraction
            basic_info = self._extract_basic_info_from_website(
                scraped_data.get('text', ''), 
                request.company_website
            )
            
            # Create enhanced data with confidence scores
            enhanced_data = {
                "company_name": SuggestionValue(
                    value=basic_info.get("company_name") or request.partial_data.get("company_name") or "Unknown Company",
                    confidence=0.8 if basic_info.get("company_name") != "Unknown Company" else 0.3,
                    source="enhanced_scraper",
                    reasoning="Company name extracted from website title/domain"
                ),
                "industry": SuggestionValue(
                    value=basic_info.get("industry", "Technology"),
                    confidence=0.7,
                    source="enhanced_scraper",
                    reasoning="Industry detected from website keywords"
                ),
                "company_size": SuggestionValue(
                    value=basic_info.get("company_size", "Small"),
                    confidence=0.6,
                    source="enhanced_scraper",
                    reasoning="Company size estimated from content analysis"
                ),
                "contact_email": SuggestionValue(
                    value=basic_info.get("contact_email", "Unknown"),
                    confidence=0.8 if basic_info.get("contact_email") != "Unknown" else 0.3,
                    source="enhanced_scraper",
                    reasoning="Email extracted from website content"
                ),
                "contact_phone": SuggestionValue(
                    value=basic_info.get("contact_phone", "Unknown"),
                    confidence=0.8 if basic_info.get("contact_phone") != "Unknown" else 0.3,
                    source="enhanced_scraper",
                    reasoning="Phone number extracted from website content"
                ),
                "address": SuggestionValue(
                    value=basic_info.get("address", "Unknown"),
                    confidence=0.6 if basic_info.get("address") != "Unknown" else 0.3,
                    source="enhanced_scraper",
                    reasoning="Address extracted from website content"
                )
            }
            
            # Count suggestions applied
            suggestions_applied = len([k for k, v in enhanced_data.items() if v.confidence > 0.5])
            
            logger.info(f"Enhanced scraper extraction completed: {suggestions_applied} fields extracted")
            
            return AccountEnhancementResponse(
                enhanced_data=enhanced_data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                warnings=[],
                suggestions_applied=suggestions_applied
            )
            
        except Exception as e:
            logger.error(f"Enhanced scraper extraction failed: {e}")
            # Final fallback - basic data
            fallback_data = {
                "company_name": SuggestionValue(
                    value=request.partial_data.get("company_name") or "Unknown Company",
                    confidence=0.3,
                    source="basic_fallback",
                    reasoning="Enhanced scraper extraction failed, using basic data"
                )
            }
            
            return AccountEnhancementResponse(
                enhanced_data=fallback_data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                warnings=[f"Enhanced scraper extraction failed: {str(e)}"],
                suggestions_applied=0
            )


# Create singleton instance
data_enrichment_service = DataEnrichmentService()