import time
import asyncio
from typing import Dict, Any, List, Optional
from app.schemas.data_enrichment import (
    AccountEnhancementRequest, AccountEnhancementResponse,
    SuggestionValue, AddressValidationRequest, AddressValidationResponse,
    IndustrySuggestionRequest, IndustrySuggestionResponse
)
from app.utils.scraper import scrape_text_with_bs4
from fastapi import HTTPException
from app.utils.logger import logger
from app.environment import environment


class DataEnrichmentService:
    
    def __init__(self):
        # Enable AI if GEMINI_API_KEY is configured
        gemini_key = getattr(environment, 'GEMINI_API_KEY', None)
        self.ai_enabled = bool(gemini_key and gemini_key.strip())
        self.cache = {}
        self.timeout = 10  # 10 seconds timeout for scraper-only approach
        
        if self.ai_enabled:
            logger.info("✅ AI enhancement ENABLED with Gemini API")
        else:
            logger.warning("⚠️ AI enhancement DISABLED - GEMINI_API_KEY not configured, using scraper-only approach")
    
    def disable_ai_enhancement(self):
        self.ai_enabled = False
        logger.info("AI enhancement disabled, will use fallback data")
    
    def enable_ai_enhancement(self):
        self.ai_enabled = True
        logger.info("AI enhancement enabled")
    
    def _extract_basic_info_from_website(self, website_content: str, website_url: str) -> Dict[str, Any]:
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
        
        # Extract address with comprehensive patterns - capture real addresses
        address_patterns = [
            # Full US address: Street number + Street name, City, State ZIP
            r'(\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Circle|Ct|Place|Pl|Court|Highway|Hwy)[^,]*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)',
            # Address with suite/unit
            r'(\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)[^,]*,\s*(?:Suite|Ste|Unit|Apt|#)\s*\d+[^,]*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})',
            # Address in contact/footer sections
            r'(?:address|location|office|headquarters|contact)[:\s]*([A-Z0-9][^<>\n]{15,150}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Circle|Ct|Place|Pl)[^<>\n]*,\s*[^<>\n]{5,50},\s*[A-Z]{2}\s+\d{5})',
            # Indian address format
            r'([A-Z]-?\d+[^,]*,\s*(?:Block\s+[A-Z0-9][^,]*,\s*)?[A-Z0-9-]+[^,]*,\s*(?:Sector\s*\d+[^,]*,\s*)?[A-Z][^,]*,\s*[A-Z]{2,}[^,]*,\s*(?:India[^,]*)?\d{6})',
            # Generic address with zip code (less strict)
            r'(\d+[^,]{5,80},\s*[A-Za-z\s]{3,50},\s*[A-Z]{2,}\s+\d{5,6})',
        ]
        
        addresses = []
        for pattern in address_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Clean up the address
                address = match.strip()
                # Remove HTML tags
                address = re.sub(r'<[^>]+>', '', address)
                # Remove extra whitespace
                address = ' '.join(address.split())
                # Remove common prefixes
                address = re.sub(r'^(address|location|office|headquarters|contact)[:\s]*', '', address, flags=re.IGNORECASE)
                
                # Filter out invalid addresses
                if (len(address) > 20 and 
                    any(char.isdigit() for char in address) and 
                    any(char.isalpha() for char in address) and
                    # Must not start with invalid prefixes
                    not address.lower().startswith(('email', 'phone', 'tel', 'fax', 'www', 'http', 'https')) and
                    # Must not contain marketing/tech jargon as main content
                    not any(word in address.lower() for word in [
                        'customer support', 'automate responses', 'enhance user', 'platforms natural',
                        'ultimate way experience', 'innovation technology solutions'
                    ]) and
                    # Must contain street indicator OR city/state/zip pattern
                    (any(word in address.lower() for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'boulevard', 'blvd', 'way', 'circle', 'ct', 'place', 'pl', 'court', 'highway', 'hwy']) or
                     re.search(r',\s*[A-Z]{2}\s+\d{5}', address))):
                    addresses.append(address)
        
        # Extract zip code separately
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        zip_codes = re.findall(zip_pattern, website_content)
        zip_code = zip_codes[0] if zip_codes else None
        
        # Clean up the best address
        address = "Unknown"
        if addresses:
            # Take the first valid address and clean it up
            best_address = addresses[0].strip()
            # Remove extra whitespace and newlines
            best_address = re.sub(r'\s+', ' ', best_address)
            # Limit length to avoid too long addresses
            if len(best_address) > 100:
                best_address = best_address[:100] + "..."
            address = best_address
        
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
            "address": address,
            "zip_code": zip_code
        }
    
    def _detect_bid_opportunities(self, website_content: str, website_url: str, basic_info: dict) -> list:
        import re
        from datetime import datetime, timedelta
        
        opportunities = []
        content_lower = website_content.lower()
        
        # Bid/opportunity keywords for construction/contractor websites
        bid_keywords = [
            'bid', 'bidding', 'tender', 'tendering', 'rfp', 'request for proposal',
            'rfi', 'request for information', 'rfq', 'request for quote',
            'opportunity', 'project', 'contract', 'construction', 'development',
            'infrastructure', 'building', 'renovation', 'maintenance', 'upgrade',
            'procurement', 'solicitation', 'award', 'contractor', 'subcontractor'
        ]
        
        # Check if website contains bid-related content
        bid_content_found = any(keyword in content_lower for keyword in bid_keywords)
        
        if not bid_content_found:
            return opportunities
        
        # Extract potential project names/titles
        project_patterns = [
            r'(?:project|opportunity|bid|tender|contract)[\s:]*([A-Z][^.!?]*(?:construction|development|building|renovation|upgrade|maintenance)[^.!?]*)',
            r'(?:new|upcoming|current)[\s]+([A-Z][^.!?]*(?:project|opportunity|bid)[^.!?]*)',
            r'([A-Z][^.!?]*(?:construction|development|infrastructure|building)[^.!?]*)',
        ]
        
        detected_projects = []
        for pattern in project_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE)
            detected_projects.extend(matches)
        
        # Extract potential values/amounts
        value_patterns = [
            r'\$[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?',
            r'[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?\s*(?:dollars?|USD)',
            r'budget[:\s]*\$?[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?',
            r'value[:\s]*\$?[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?'
        ]
        
        detected_values = []
        for pattern in value_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE)
            detected_values.extend(matches)
        
        # Extract potential locations
        location_patterns = [
            r'(?:location|site|address)[:\s]*([A-Z][^.!?\n]*(?:Street|Avenue|Road|Drive|Lane|Boulevard|Way|Circle|Place)[^.!?\n]*)',
            r'(?:in|at|located)[\s]+([A-Z][^.!?\n]*(?:City|Town|County|State|Province)[^.!?\n]*)',
            r'([A-Z][^.!?\n]*(?:City|Town|County|State|Province)[^.!?\n]*)'
        ]
        
        detected_locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE)
            detected_locations.extend(matches)
        
        # Extract potential dates
        date_patterns = [
            r'(?:deadline|due|closing|submission)[:\s]*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(?:deadline|due|closing|submission)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:by|before|until)[:\s]*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(?:by|before|until)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        detected_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE)
            detected_dates.extend(matches)
        
        # Create opportunity objects based on detected information
        if detected_projects or bid_content_found:
            # Enhanced opportunity detection with better value extraction
            project_value = self._extract_project_value(detected_values, content_lower)
            sales_stage = self._determine_sales_stage(content_lower, detected_dates)
            market_sector = self._determine_construction_sector(content_lower)
            project_description = self._generate_project_description(website_content, basic_info)
            
            # Default opportunity based on website analysis
            opportunity = {
                "opportunity_name": detected_projects[0] if detected_projects else f"{basic_info.get('company_name', 'Company')} Project Opportunity",
                "location": detected_locations[0] if detected_locations else basic_info.get('address', 'Unknown'),
                "project_value": project_value,
                "sales_stage": sales_stage,
                "market_sector": market_sector,
                "project_description": project_description,
                "date": datetime.now().strftime("%Y-%m-%d"),  # Current date
                "approver_name": "Current User",  # Will be set by frontend
                "confidence_score": self._calculate_confidence_score(website_content, detected_projects, detected_values)
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def _determine_construction_sector(self, content_lower: str) -> str:
        """Determine construction sector based on website content"""
        sector_keywords = {
            "Transportation": ['transportation', 'transit', 'railway', 'highway', 'bridge', 'tunnel', 'metro', 'subway'],
            "Energy": ['energy', 'power', 'electrical', 'solar', 'wind', 'renewable', 'utility'],
            "Utilities": ['utilities', 'water', 'sewer', 'waste', 'treatment', 'infrastructure'],
            "Real Estate": ['real estate', 'residential', 'commercial', 'housing', 'apartment', 'office'],
            "Healthcare": ['healthcare', 'hospital', 'medical', 'clinic', 'health'],
            "Education": ['education', 'school', 'university', 'college', 'campus'],
            "Technology": ['technology', 'data center', 'telecommunications', 'IT', 'digital'],
            "General Construction": ['construction', 'building', 'renovation', 'maintenance', 'development']
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return sector
        
        return "General Construction"
    
    def _generate_project_description(self, website_content: str, basic_info: dict) -> str:
        """Generate project description based on website content"""
        # Extract relevant sentences that might describe projects
        sentences = website_content.split('.')
        project_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in ['project', 'construction', 'development', 'building', 'infrastructure']):
                project_sentences.append(sentence.strip())
        
        if project_sentences:
            return '. '.join(project_sentences[:3]) + '.'
        
        return f"Construction and development opportunities with {basic_info.get('company_name', 'the company')}."
    
    def _calculate_confidence_score(self, website_content: str, projects: list, values: list) -> float:
        """Calculate confidence score for detected opportunities"""
        score = 0.0
        
        # Base score for bid-related content
        bid_keywords = ['bid', 'bidding', 'tender', 'rfp', 'opportunity', 'contract']
        if any(keyword in website_content.lower() for keyword in bid_keywords):
            score += 0.3
        
        # Bonus for detected projects
        if projects:
            score += 0.3
        
        # Bonus for detected values
        if values:
            score += 0.2
        
        # Bonus for construction-related content
        construction_keywords = ['construction', 'building', 'development', 'infrastructure', 'contractor']
        if any(keyword in website_content.lower() for keyword in construction_keywords):
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_opportunity_fields(self, website_content: str, website_url: str, basic_info: dict) -> dict:
        """Extract opportunity-specific fields from website content"""
        import re
        from datetime import datetime
        
        content_lower = website_content.lower()
        
        # Extract project value from content
        project_value = self._extract_project_value_from_content(website_content, content_lower)
        
        # Determine sales stage based on content
        sales_stage = self._determine_sales_stage_from_content(content_lower)
        
        # Determine market sector
        market_sector = self._determine_construction_sector(content_lower)
        
        # Generate project description
        project_description = self._generate_enhanced_project_description(website_content, basic_info)
        
        # Extract location
        location = self._extract_location_from_content(website_content, basic_info)
        
        # Calculate confidence for project description based on quality
        project_desc_confidence = 0.7
        if len(project_description) > 200:  # Longer descriptions are usually better
            project_desc_confidence = 0.85
        elif len(project_description) > 100:
            project_desc_confidence = 0.75
        elif len(project_description) < 50:  # Very short descriptions are less reliable
            project_desc_confidence = 0.5
        
        # Calculate confidence for location based on completeness
        location_confidence = 0.3
        if location != "Unknown":
            # Check if it's a full address (has street, city, state, zip)
            has_street = any(word in location.lower() for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'boulevard', 'blvd', 'way', 'circle', 'ct', 'place', 'pl'])
            has_zip = bool(re.search(r'\d{5}(?:-\d{4})?', location))
            has_city_state = bool(re.search(r',\s*[A-Z]{2}\s+\d{5}', location))
            
            if has_street and has_zip and has_city_state:
                location_confidence = 0.9  # Complete address
            elif has_zip and has_city_state:
                location_confidence = 0.8  # City, state, zip
            elif has_zip or has_city_state:
                location_confidence = 0.6  # Partial address
            else:
                location_confidence = 0.5  # Basic location info
        
        return {
            "project_value": SuggestionValue(
                value=project_value,
                confidence=0.8 if project_value != "TBD" else 0.3,
                source="opportunity_analysis",
                reasoning="Project value estimated from website content and company size"
            ),
            "sales_stage": SuggestionValue(
                value=sales_stage,
                confidence=0.9,
                source="opportunity_analysis",
                reasoning="Sales stage determined from website content analysis"
            ),
            "market_sector": SuggestionValue(
                value=market_sector,
                confidence=0.8,
                source="opportunity_analysis",
                reasoning="Market sector determined from website content and services"
            ),
            "project_description": SuggestionValue(
                value=project_description,
                confidence=project_desc_confidence,
                source="opportunity_analysis",
                reasoning="Project description extracted from website content using AI-enhanced analysis" if self.ai_enabled else "Project description generated from website content and company services"
            ),
            "location": SuggestionValue(
                value=location,
                confidence=location_confidence,
                source="opportunity_analysis",
                reasoning="Complete address extracted from website content" if location_confidence > 0.7 else "Location information extracted from website content"
            )
        }
    
    def _extract_project_value_from_content(self, website_content: str, content_lower: str) -> str:
        """Extract project value from website content"""
        import re
        
        # Look for specific value patterns
        value_patterns = [
            r'\$[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?',
            r'budget[:\s]*\$?[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?',
            r'value[:\s]*\$?[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?',
            r'cost[:\s]*\$?[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?',
            r'price[:\s]*\$?[\d,]+(?:\.\d{2})?(?:[KMB]|thousand|million|billion)?'
        ]
        
        for pattern in value_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Estimate based on company size and industry
        if any(word in content_lower for word in ['enterprise', 'corporation', 'large', 'major', 'global']):
            return "$500K - $2M"
        elif any(word in content_lower for word in ['medium', 'mid-size', 'growing', 'established']):
            return "$100K - $500K"
        elif any(word in content_lower for word in ['startup', 'small', 'local', 'regional']):
            return "$50K - $100K"
        else:
            return "$100K - $500K"  # Default for tech companies
    
    def _determine_sales_stage_from_content(self, content_lower: str) -> str:
        """Determine sales stage from website content"""
        if any(word in content_lower for word in ['rfp', 'request for proposal', 'solicitation', 'bidding', 'tender']):
            return "Proposal"
        elif any(word in content_lower for word in ['qualification', 'pre-qualification', 'shortlist', 'evaluation']):
            return "Qualification"
        elif any(word in content_lower for word in ['negotiation', 'contract', 'award', 'agreement']):
            return "Negotiation"
        elif any(word in content_lower for word in ['closed', 'won', 'awarded', 'successful', 'completed']):
            return "Closed Won"
        elif any(word in content_lower for word in ['lost', 'unsuccessful', 'declined', 'rejected']):
            return "Closed Lost"
        else:
            return "Prospecting"  # Default for new opportunities
    
    def _extract_location_from_content(self, website_content: str, basic_info: dict) -> str:
        """Extract full address from website content with comprehensive parsing"""
        import re
        
        # First try to get from basic_info (already extracted address)
        if basic_info.get('address') and basic_info.get('address') != 'Unknown':
            address = basic_info.get('address')
            # If it's a full address, return it
            if len(address) > 30 and any(char.isdigit() for char in address):
                return address
        
        # Enhanced address extraction patterns
        address_patterns = [
            # Full US address: Street number + Street name, City, State ZIP
            r'(\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Circle|Ct|Place|Pl|Court|Highway|Hwy)[^,]*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)',
            # Address with suite/unit
            r'(\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)[^,]*,\s*(?:Suite|Ste|Unit|Apt|#)\s*\d+[^,]*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})',
            # Address in contact section
            r'(?:address|location|office|headquarters|contact)[:\s]*([A-Z0-9][^<>\n]{20,150}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)[^<>\n]*,\s*[^<>\n]{5,50},\s*[A-Z]{2}\s+\d{5})',
            # City, State ZIP format (when street is on previous line)
            r'([A-Za-z\s]{3,50},\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)',
            # Indian address format
            r'([A-Z]-?\d+[^,]*,\s*(?:Block\s+[A-Z0-9][^,]*,\s*)?[A-Z0-9-]+[^,]*,\s*(?:Sector\s*\d+[^,]*,\s*)?[A-Z][^,]*,\s*[A-Z]{2,}[^,]*,\s*(?:India[^,]*)?\d{6})',
            # Generic address with zip code
            r'(\d+[^,]{5,80},\s*[A-Za-z\s]{3,50},\s*[A-Z]{2,}\s+\d{5,6})',
        ]
        
        found_addresses = []
        for pattern in address_patterns:
            matches = re.findall(pattern, website_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                address = match.strip()
                # Clean up HTML tags
                address = re.sub(r'<[^>]+>', '', address)
                # Remove extra whitespace
                address = ' '.join(address.split())
                # Remove common prefixes
                address = re.sub(r'^(address|location|office|headquarters|contact)[:\s]*', '', address, flags=re.IGNORECASE)
                
                # Validate address quality
                if (len(address) > 20 and 
                    any(char.isdigit() for char in address) and 
                    any(char.isalpha() for char in address) and
                    not address.lower().startswith(('email', 'phone', 'tel', 'fax', 'www', 'http')) and
                    # Must contain street indicator or city/state/zip pattern
                    (any(word in address.lower() for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'boulevard', 'blvd', 'way', 'circle', 'ct', 'place', 'pl']) or
                     re.search(r',\s*[A-Z]{2}\s+\d{5}', address))):
                    found_addresses.append(address)
        
        # Return the best address (prefer longer, more complete addresses)
        if found_addresses:
            # Sort by length (longer = more complete) and return the best one
            found_addresses.sort(key=len, reverse=True)
            return found_addresses[0]
        
        # Fallback: Try to extract city, state from content
        city_state_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2})\s+(\d{5})'
        city_state_match = re.search(city_state_pattern, website_content)
        if city_state_match:
            city, state, zip_code = city_state_match.groups()
            return f"{city}, {state} {zip_code}"
        
        # Final fallback: Check basic_info for city/state
        if basic_info.get('zip_code'):
            zip_code = basic_info.get('zip_code')
            # Try to find city/state near the zip code
            zip_context_pattern = rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{{2}})\s+{zip_code}'
            zip_match = re.search(zip_context_pattern, website_content)
            if zip_match:
                city, state = zip_match.groups()
                return f"{city}, {state} {zip_code}"
        
        return "Unknown"
    
    def _generate_enhanced_project_description(self, website_content: str, basic_info: dict) -> str:
        """Generate enhanced project description from website content using AI when available"""
        import re
        
        # Try to use AI if available
        if self.ai_enabled:
            try:
                import google.generativeai as genai
                from app.environment import environment
                
                genai.configure(api_key=environment.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-pro')
                
                # Truncate content to avoid token limits
                content_snippet = website_content[:8000] if len(website_content) > 8000 else website_content
                
                prompt = f"""Analyze the following website content and extract a comprehensive project description. 
Focus on identifying:
1. Project/opportunity details (what the project is about)
2. Objectives and goals
3. Scope of work or deliverables
4. Key features or components
5. Timeline or phases if mentioned
6. Stakeholders or beneficiaries
7. Technologies or methodologies involved

Return a detailed, professional project description (150-400 words) that would be useful for a business opportunity. 
If no specific project is mentioned, describe the type of opportunities this company typically engages in.

Website Content:
{content_snippet}

Return ONLY the project description text, no additional commentary or formatting."""

                response = model.generate_content(prompt)
                description = response.text.strip()
                
                # Clean up the response
                if description.startswith('```'):
                    description = description.strip('`').strip()
                    if '\n' in description:
                        description = description.split('\n', 1)[1] if description.split('\n')[0].lower() in ['json', 'text', 'markdown'] else description
                
                # Validate description quality
                if len(description) > 100 and not description.lower().startswith(('error', 'sorry', 'i cannot')):
                    return description
            except Exception as e:
                logger.warning(f"AI project description generation failed, using fallback: {e}")
        
        # Fallback: Enhanced pattern-based extraction
        company_name = basic_info.get('company_name', 'the company')
        
        # Look for project-specific content
        project_keywords = [
            'project', 'opportunity', 'program', 'initiative', 'construction', 
            'development', 'infrastructure', 'improvement', 'upgrade', 'renovation'
        ]
        
        # Extract sentences containing project-related keywords
        sentences = re.split(r'[.!?]+', website_content)
        project_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in project_keywords):
                # Avoid very short or generic sentences
                if len(sentence) > 50 and not sentence.lower().startswith(('click', 'visit', 'learn more', 'read more')):
                    project_sentences.append(sentence)
        
        # Build description from extracted sentences
        if project_sentences:
            # Take up to 5 most relevant sentences
            selected_sentences = project_sentences[:5]
            description = '. '.join(selected_sentences)
            if not description.endswith('.'):
                description += '.'
            
            # Ensure minimum length
            if len(description) < 100:
                description += f" This opportunity involves working with {company_name} on significant projects and initiatives."
            
            return description
        
        # Final fallback: Generic description based on company type
        services = []
        content_lower = website_content.lower()
        
        if any(word in content_lower for word in ['construction', 'building', 'infrastructure', 'contractor']):
            return f"Construction and infrastructure project opportunity with {company_name}. This opportunity involves delivering comprehensive construction services, infrastructure development, and project management solutions."
        elif any(word in content_lower for word in ['transportation', 'transit', 'railway', 'highway', 'bridge']):
            return f"Transportation infrastructure project opportunity with {company_name}. This opportunity focuses on transportation system improvements, infrastructure development, and enhancing public transit services."
        elif any(word in content_lower for word in ['web development', 'software', 'saas', 'app', 'digital']):
            services_text = ', '.join(['web development', 'SaaS solutions', 'digital transformation']) if not services else ', '.join(services)
            return f"Technology project opportunity with {company_name} involving {services_text}. This opportunity focuses on delivering innovative digital solutions and cutting-edge technology services."
        else:
            return f"Business opportunity with {company_name}. This opportunity involves delivering comprehensive services and solutions to enhance business operations and achieve strategic objectives."
    
    def _extract_project_value(self, detected_values: list, content_lower: str) -> str:
        """Extract and format project value from detected values"""
        import re
        
        if not detected_values:
            # Try to estimate value based on company size and industry
            if any(word in content_lower for word in ['enterprise', 'corporation', 'large', 'major']):
                return "$500K - $2M"
            elif any(word in content_lower for word in ['medium', 'mid-size', 'growing']):
                return "$100K - $500K"
            else:
                return "$50K - $100K"
        
        # Clean and format the first detected value
        value = detected_values[0].strip()
        
        # Remove common prefixes and clean up
        value = re.sub(r'^(budget|value|cost)[:\s]*', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\s*(dollars?|USD)\s*$', '', value, flags=re.IGNORECASE)
        
        # Ensure it starts with $ if it contains numbers
        if re.search(r'\d', value) and not value.startswith('$'):
            value = '$' + value
        
        return value
    
    def _determine_sales_stage(self, content_lower: str, detected_dates: list) -> str:
        """Determine appropriate sales stage based on content and dates"""
        # Check for specific stage indicators
        if any(word in content_lower for word in ['rfp', 'request for proposal', 'solicitation', 'bidding']):
            return "Proposal"
        elif any(word in content_lower for word in ['qualification', 'pre-qualification', 'shortlist']):
            return "Qualification"
        elif any(word in content_lower for word in ['negotiation', 'contract', 'award']):
            return "Negotiation"
        elif any(word in content_lower for word in ['closed', 'won', 'awarded', 'successful']):
            return "Closed Won"
        elif any(word in content_lower for word in ['lost', 'unsuccessful', 'declined']):
            return "Closed Lost"
        elif detected_dates:
            # If there are deadlines, it's likely in proposal stage
            return "Proposal"
        else:
            # Default to prospecting for new opportunities
            return "Prospecting"
    
    async def enhance_opportunity_data(
        self, 
        request: AccountEnhancementRequest
    ) -> AccountEnhancementResponse:
        start_time = time.time()
        
        logger.info("Using AI-powered opportunity and bid detection")
        logger.info(f"Processing website: {request.company_website}")
        
        try:
            # Scrape website content
            website_url = str(request.company_website)
            scraped_data = await scrape_text_with_bs4(website_url)
            if "error" in scraped_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to scrape website: {scraped_data['error']}"
                )
            
            logger.info(f"Website content length: {len(scraped_data.get('text', ''))} characters")
            
            # Extract basic company info
            basic_info = self._extract_basic_info_from_website(
                scraped_data.get('text', ''), 
                website_url
            )
            
            # Enhanced bid/opportunity detection for contractor websites
            bid_opportunities = self._detect_bid_opportunities(
                scraped_data.get('text', ''),
                website_url,
                basic_info
            )
            
            # Create enhanced data with bid-specific information
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
                ),
                "zip_code": SuggestionValue(
                    value=basic_info.get("zip_code", "Unknown"),
                    confidence=0.8 if basic_info.get("zip_code") else 0.3,
                    source="enhanced_scraper",
                    reasoning="ZIP code extracted from website content"
                )
            }
            
            # Add bid-specific opportunities if detected
            if bid_opportunities:
                enhanced_data["detected_opportunities"] = SuggestionValue(
                    value=bid_opportunities,
                    confidence=0.9,
                    source="bid_detection",
                    reasoning="Active bid opportunities detected on contractor website"
                )
            
            # Add enhanced opportunity-specific fields
            enhanced_data.update(self._extract_opportunity_fields(
                scraped_data.get('text', ''),
                website_url,
                basic_info
            ))
            
            # Count suggestions applied
            suggestions_applied = len([k for k, v in enhanced_data.items() if v.confidence > 0.5])
            
            logger.info(f"Enhanced opportunity detection completed: {suggestions_applied} fields extracted, {len(bid_opportunities) if bid_opportunities else 0} opportunities detected")
            
            return AccountEnhancementResponse(
                enhanced_data=enhanced_data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                warnings=[],
                suggestions_applied=suggestions_applied
            )
            
        except Exception as e:
            logger.error(f"Enhanced opportunity detection failed: {e}")
            # Fallback to basic account enhancement
            return await self.enhance_account_data(request)
    
    async def enhance_account_data(
        self, 
        request: AccountEnhancementRequest
    ) -> AccountEnhancementResponse:
        start_time = time.time()
        
        logger.info("Using enhanced scraper-only approach for data extraction")
        logger.info(f"Processing website: {request.company_website}")
        
        try:
            # Scrape website content
            website_url = str(request.company_website)
            scraped_data = await scrape_text_with_bs4(website_url)
            if "error" in scraped_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to scrape website: {scraped_data['error']}"
                )
            
            logger.info(f"Website content length: {len(scraped_data.get('text', ''))} characters")
            
            # Use enhanced scraper extraction
            basic_info = self._extract_basic_info_from_website(
                scraped_data.get('text', ''), 
                website_url
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
                ),
                "zip_code": SuggestionValue(
                    value=basic_info.get("zip_code", "Unknown"),
                    confidence=0.8 if basic_info.get("zip_code") else 0.3,
                    source="enhanced_scraper",
                    reasoning="ZIP code extracted from website content"
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