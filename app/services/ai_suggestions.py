import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.schemas.ai_suggestions import (
    OrganizationNameRequest, OrganizationNameResponse,
    AccountEnhancementRequest, AccountEnhancementResponse,
    AddressValidationRequest, AddressValidationResponse,
    ContactValidationRequest, ContactValidationResponse,
    IndustrySuggestionRequest, IndustrySuggestionResponse,
    CompanySizeSuggestionRequest, CompanySizeSuggestionResponse,
    SuggestionValue, AISuggestionRequest, AISuggestionResponse
)
from app.utils.scraper import scrape_text_with_bs4
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.environment import environment
import google.generativeai as genai
from google.generativeai import types


class DataEnrichmentService:
    """Service for enriching company data from web sources"""
    
    def __init__(self):
        genai.configure(api_key=environment.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.cache = {}  # Simple in-memory cache for demo
    
    async def discover_and_extract_opportunities(self, base_url: str) -> dict:
        """
        Advanced auto-scraper that:
        1. Scrapes main website to find project/opportunity pages
        2. Follows links to individual project pages
        3. Extracts detailed data from each project
        4. Returns multiple opportunities
        """
        import re
        from urllib.parse import urljoin, urlparse
        
        logger.info(f"Starting opportunity discovery for: {base_url}")
        
        # Step 1: Scrape main page
        main_page_data = await scrape_text_with_bs4(base_url)
        if "error" in main_page_data:
            return {"error": f"Failed to scrape main page: {main_page_data['error']}"}
        
        # Step 2: Find project listing pages and individual project URLs
        project_keywords = [
            'projects', 'programs', 'opportunities', 'tenders', 'rfp', 'bids', 
            'contracts', 'freeway', 'construction', 'in-progress', 'ongoing'
        ]
        
        # Extract all links from main page
        all_links = re.findall(r'href=["\'](https?://[^"\']+|/[^"\']+)["\']', main_page_data.get('html', ''))
        
        # Filter for project-related URLs
        project_urls = []
        for link in all_links:
            full_url = urljoin(base_url, link)
            # Check if URL contains project keywords
            if any(keyword in full_url.lower() for keyword in project_keywords):
                # Avoid duplicate URLs
                if full_url not in project_urls and urlparse(full_url).netloc == urlparse(base_url).netloc:
                    project_urls.append(full_url)
        
        logger.info(f"Found {len(project_urls)} potential project URLs")
        
        # Step 3: Scrape each project page (limit to first 10 to avoid overload)
        opportunities = []
        for project_url in project_urls[:10]:
            try:
                logger.info(f"Scraping project page: {project_url}")
                project_data = await scrape_text_with_bs4(project_url)
                
                if "error" not in project_data:
                    # Extract opportunity data from this project page
                    opportunity = await self._extract_opportunity_from_page(project_url, project_data)
                    if opportunity:
                        opportunities.append(opportunity)
            except Exception as e:
                logger.error(f"Error scraping {project_url}: {e}")
                continue
        
        return {
            "base_url": base_url,
            "opportunities_found": len(opportunities),
            "opportunities": opportunities
        }
    
    async def _extract_opportunity_from_page(self, page_url: str, page_data: dict) -> dict:
        """Extract comprehensive opportunity data from a single project page for CRM"""
        import re
        
        content = page_data.get('text', '')
        html = page_data.get('html', '')
        
        # === OPPORTUNITY NAME ===
        # Extract from H1, H2, or title tag
        opportunity_name = ""
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
        h2_match = re.search(r'<h2[^>]*>([^<]+)</h2>', html, re.IGNORECASE)
        title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        
        if h1_match:
            opportunity_name = h1_match.group(1).strip()
        elif h2_match:
            opportunity_name = h2_match.group(1).strip()
        elif title_match:
            opportunity_name = title_match.group(1).split('|')[0].strip()
        
        # === PROJECT DESCRIPTION (Project Overview) ===
        # Look for "Project Overview" section
        project_description = ""
        overview_patterns = [
            r'(?:Project Overview|Overview)(.*?)(?:Project Details|Project Milestones|Contact|$)',
            r'(?:<h2[^>]*>Project Overview</h2>)(.*?)(?:<h2|<div class)',
            r'(?:##\s*Project Overview)(.*?)(?:##|$)'
        ]
        for pattern in overview_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                project_description = match.group(1).strip()[:2000]  # Limit to 2000 chars
                break
        
        # If no overview found, use first 1000 characters
        if not project_description:
            project_description = content[:1000].strip()
        
        # === PROJECT SCOPE (Project Details/Milestones) ===
        # Extract milestones table or project details section
        project_scope = ""
        scope_patterns = [
            r'(?:Project Details|Project Milestones)(.*?)(?:Back to Top|Contact|$)',
            r'(?:<h2[^>]*>Project Details</h2>)(.*?)(?:<h2|<div class)',
            r'(?:##\s*Project Details)(.*?)(?:##|$)'
        ]
        for pattern in scope_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                project_scope = match.group(1).strip()[:3000]  # Limit to 3000 chars
                break
        
        # Extract milestones/timeline data
        milestones = []
        milestone_pattern = r'(?:Timeline|TIMELINE)[:\s]*([^\n]+)'
        milestone_matches = re.findall(milestone_pattern, content, re.IGNORECASE)
        milestones = milestone_matches[:10] if milestone_matches else []
        
        # === CONTACT DETAILS ===
        # Extract phone numbers
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, content)
        phone_numbers = [f"({p[0]}) {p[1]}-{p[2]}" for p in phones[:3]]
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        
        # Extract contact section
        contact_info = ""
        contact_patterns = [
            r'(?:Contact|Contact Us|Contact Information|Contact the Project Team)(.*?)(?:\n\n|Back to Top|$)',
            r'(?:<h2[^>]*>Contact</h2>)(.*?)(?:<h2|<div class)',
        ]
        for pattern in contact_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                contact_info = match.group(1).strip()[:500]
                break
        
        # === DOCUMENTS (PDFs, DOCs, etc.) ===
        documents = []
        doc_patterns = [
            r'href=["\'](https?://[^"\']*\.(?:pdf|doc|docx|xls|xlsx|ppt|pptx))["\']',
            r'href=["\'](https?://[^"\']*(?:document|download|report|attachment)[^"\']*)["\']'
        ]
        for pattern in doc_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            documents.extend(matches)
        
        # === IMAGES ===
        image_pattern = r'src=["\'](https?://[^"\']*\.(?:jpg|jpeg|png|gif|svg|webp))["\']'
        images = re.findall(image_pattern, html, re.IGNORECASE)
        
        # === PROJECT STATUS ===
        status = "Lead"  # Default
        status_keywords = {
            "In Progress": ["in progress", "ongoing", "under construction", "active", "currently"],
            "Planned": ["planned", "upcoming", "future", "proposed", "estimated"],
            "Completed": ["completed", "finished", "done", "ended"]
        }
        for status_name, keywords in status_keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                status = status_name
                break
        
        # === DATES (Start/End) ===
        date_pattern = r'(?:Spring|Summer|Fall|Winter|Early|Late|Mid)?\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*\d{1,2}?,?\s*\d{4}|20\d{2}'
        dates = re.findall(date_pattern, content, re.IGNORECASE)
        
        start_date = dates[0] if len(dates) > 0 else "Not available"
        end_date = dates[-1] if len(dates) > 1 else "Not available"
        
        # === PROJECT VALUE ===
        value_pattern = r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B|K|thousand))?'
        values = re.findall(value_pattern, content, re.IGNORECASE)
        project_value = values[0] if values else "Not available"
        
        # === LOCATION ===
        location = self._extract_address_from_content(content)
        
        # === MARKET SECTOR ===
        # Infer from content
        sector_keywords = {
            "Infrastructure": ["freeway", "highway", "bridge", "road", "transportation", "transit"],
            "Construction": ["construction", "building", "development"],
            "Technology": ["technology", "software", "IT", "digital"],
            "Healthcare": ["healthcare", "medical", "hospital"],
            "Energy": ["energy", "power", "utilities"]
        }
        market_sector = "Infrastructure"  # Default
        for sector, keywords in sector_keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                market_sector = sector
                break
        
        return {
            # === FOR CREATE OPPORTUNITY MODAL ===
            "opportunity_name": opportunity_name or "Unnamed Project",
            "project_value": project_value,
            "location": location if location else "",
            "market_sector": market_sector,
            "sales_stage": "Prospecting",
            
            # === FOR OPPORTUNITY DETAILS PAGE (Overview & Scope) ===
            "project_description": project_description,
            "project_scope": project_scope,
            "project_status": status,
            "milestones": milestones,
            
            # === CONTACT DETAILS ===
            "contact_phone": phone_numbers[0] if phone_numbers else "",
            "contact_emails": emails[:3],
            "contact_info": contact_info,
            
            # === RESOURCES ===
            "documents": list(set(documents))[:20],  # Limit to 20 docs
            "images": list(set(images))[:10],  # Limit to 10 images
            
            # === METADATA ===
            "project_url": page_url,
            "start_date": start_date,
            "end_date": end_date,
            "extracted_dates": dates[:5],
            "tag": "in-progress" if status == "In Progress" else "lead"
        }
    
    def _extract_address_from_content(self, content: str) -> str:
        """Extract full address from website content using comprehensive regex patterns"""
        import re
        
        # Enhanced address patterns for various formats
        address_patterns = [
            # Indian address format: Building, Block, Sector, City, State, Pincode
            r'([A-Z]-?\d+[^,]*,\s*(?:Block\s+[A-Z0-9][^,]*,\s*)?[A-Z0-9-]+[^,]*,\s*(?:Sector\s*\d+[^,]*,\s*)?[A-Z][^,]*,\s*[A-Z]{2,}[^,]*,\s*(?:India[^,]*)?\d{6})',
            # Standard address with building number, street, city, state, zip
            r'(\d+[^,]*,\s*[A-Z][^,]*,\s*[A-Z][^,]*,\s*[A-Z]{2,}[^,]*\d{5,6})',
            # Address in contact section
            r'(?:address|located|office|headquarters)[:\s]*([A-Z0-9][^<>\n]{20,200}(?:India|USA|UK|Canada|Australia)[^<>\n]*)',
            # Building + area + city pattern
            r'([A-Z]-?\d+[^,]{0,100},\s*[^,]+,\s*[^,]+,\s*[A-Z]{2,}[^,]*\d{5,6})',
            # Simple format: Street, City, State, Zip
            r'([A-Z][^,]+,\s*[A-Z][^,]+,\s*[A-Z]{2,}[^,]*\d{5,6})',
            # Contact section with full address
            r'(?:contact|reach|visit)[^:]*:([A-Z0-9][^<>\n]{30,200}(?:India|USA|UK)[^<>\n]*)'
        ]
        
        for i, pattern in enumerate(address_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                for match in matches:
                    # Clean up the address
                    address = match.strip()
                    # Remove HTML tags
                    address = re.sub(r'<[^>]+>', '', address)
                    # Remove extra whitespace and newlines
                    address = ' '.join(address.split())
                    # Remove common prefixes
                    address = re.sub(r'^(address|located|office|headquarters)[:\s]*', '', address, flags=re.IGNORECASE)
                    
                    # Validate address quality
                    if (len(address) > 20 and  # Minimum length
                        any(char.isdigit() for char in address) and  # Contains numbers
                        any(char.isalpha() for char in address) and  # Contains letters
                        not address.lower().startswith(('email', 'phone', 'tel', 'fax'))):  # Not contact info
                        print(f"Pattern {i+1} found address: {address}")
                        return address
        
        return "Address not available"
    
    async def suggest_organization_name(
        self, 
        request: OrganizationNameRequest
    ) -> OrganizationNameResponse:
        """
        Extract company name from website content.
        """
        start_time = time.time()
        
        try:
            cache_key = f"org_name:{request.website_url}"
            if cache_key in self.cache:
                logger.info(f"Cache hit for organization name: {request.website_url}")
                return OrganizationNameResponse(**self.cache[cache_key])
            
            scraped_data = await scrape_text_with_bs4(str(request.website_url))
            if "error" in scraped_data:
                raise MegapolisHTTPException(
                    status_code=400, 
                    message=f"Failed to scrape website: {scraped_data['error']}"
                )
            
            extract_name_function = {
                "name": "extract_organization_name",
                "description": "Extract official organization name from website content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "official_name": {
                            "type": "string",
                            "description": "The official, full organization name as it appears in legal documents"
                        },
                        "common_name": {
                            "type": "string",
                            "description": "Common or shortened name used in marketing"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Confidence in the name extraction (0-1)"
                        },
                        "alternatives": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Alternative names or variations found",
                            "maxItems": 3
                        },
                        "source": {
                            "type": "string",
                            "description": "Where the name was found (meta_tags, homepage_title, about_page, footer, etc.)"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation of why this name was chosen"
                        }
                    },
                    "required": ["official_name", "confidence", "source"]
                }
            }
            
            tools = types.Tool(function_declarations=[extract_name_function])
            config = types.GenerateContentConfig(tools=[tools])
            
            context_info = ""
            if request.context:
                context_info = f"\nAdditional Context: {request.context}"
            
            prompt = f"""
            Analyze this website and extract the official organization name.
            
            Website URL: {request.website_url}{context_info}
            
            Website Content:
            {scraped_data['text'][:3000]}
            
            Instructions:
            1. Look for the official company/organization name
            2. Check meta tags, page title, about section, footer
            3. Provide confidence score based on clarity and consistency
            4. List any alternative names found
            5. Explain where you found the name and why it's the best choice
            
            Important:
            - Extract the full legal name, not just a shortened version
            - Be conservative with confidence scores
            - If uncertain, provide lower confidence and explain why
            """
            
            response = self.model.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(parts=[{"text": prompt}])],
                config=config
            )
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    args = part.function_call.args
                    
                    result = OrganizationNameResponse(
                        suggested_name=args["official_name"],
                        confidence=float(args["confidence"]),
                        alternatives=args.get("alternatives", []),
                        source=args["source"],
                        reasoning=args.get("reasoning", f"Found in {args['source']} with {float(args['confidence'])*100:.0f}% confidence")
                    )
                    
                    self.cache[cache_key] = result.model_dump()
                    
                    processing_time = int((time.time() - start_time) * 1000)
                    logger.info(f"Organization name suggestion completed in {processing_time}ms")
                    
                    return result
            
            raise Exception("AI did not return structured response")
            
        except Exception as e:
            logger.error(f"Organization name suggestion failed: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to suggest organization name",
                details=str(e)
            )
    
    async def enhance_account_data(
        self, 
        request: AccountEnhancementRequest
    ) -> AccountEnhancementResponse:
        """
        Fill account fields from website data.
        """
        start_time = time.time()
        
        try:
            scraped_data = await scrape_text_with_bs4(str(request.company_website))
            if "error" in scraped_data:
                raise MegapolisHTTPException(
                    status_code=400,
                    message=f"Failed to scrape website: {scraped_data['error']}"
                )
            
            enhance_account_function = {
                "name": "enhance_account_data",
                "description": "Extract company information from website content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Official company name"
                        },
                        "industry": {
                            "type": "string",
                            "description": "Primary industry sector"
                        },
                        "company_size": {
                            "type": "string",
                            "description": "Estimated company size"
                        },
                        "contact_name": {
                            "type": "string",
                            "description": "Primary contact person name"
                        },
                        "contact_email": {
                            "type": "string",
                            "description": "Primary contact email"
                        },
                        "contact_phone": {
                            "type": "string",
                            "description": "Primary contact phone in E.164 format (e.g., +917404664714, no hyphens or spaces)"
                        },
                        "address_line1": {
                            "type": "string",
                            "description": "Address line 1"
                        },
                        "address_city": {
                            "type": "string",
                            "description": "City"
                        },
                        "address_state": {
                            "type": "string",
                            "description": "State"
                        },
                        "address_pincode": {
                            "type": "string",
                            "description": "Postal code"
                        },
                        "confidence_scores": {
                            "type": "object",
                            "properties": {
                                "company_name": {"type": "number"},
                                "industry": {"type": "number"},
                                "contact_info": {"type": "number"},
                                "address": {"type": "number"}
                            }
                        },
                        "warnings": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["company_name", "industry", "confidence_scores"]
                }
            }
            
            partial_data_str = ""
            if request.partial_data:
                partial_data_str = f"\nAlready entered data: {request.partial_data}"
            
            prompt = f"""
            Analyze this company website and enhance account data based on the content.
            
            Website URL: {request.company_website}{partial_data_str}
            
            Website Content:
            {scraped_data['text'][:4000]}
            
            Enhancement Options: {request.enhancement_options}
            
            Instructions:
            1. Extract comprehensive company information
            2. Provide confidence scores for each field (0-1)
            3. Be conservative with confidence - only high confidence for clear information
            4. Analyze the company's main services, target market, and stage
            5. Extract contact information with validation
            6. Format phone numbers in E.164 format (+917404664714, no hyphens or spaces)
            7. Provide warnings for any uncertain data
            
            Focus on:
            - Official company name (check meta tags, about page)
            - Primary industry sector
            - Company size estimation
            - Contact information (look for contact page, about page, footer)
            - Clean phone numbers in international E.164 format
            - Business address (check contact page, footer)
            - Main services and target market
            """
            
            logger.info("Calling Gemini API for account enhancement")
            response = self.model.generate_content(prompt)
            logger.info(f"Gemini API response received: {type(response)}")
            
            enhanced_data = {}
            warnings = []
            suggestions_applied = 0
            
            logger.info(f"Response structure: {dir(response)}")
            if hasattr(response, 'candidates'):
                logger.info(f"Candidates: {response.candidates}")
            else:
                logger.info("No candidates attribute in response")
                
            if not response or not response.candidates or len(response.candidates) == 0:
                raise Exception("No candidates returned from Gemini API")
            
            candidate = response.candidates[0]
            logger.info(f"Candidate structure: {dir(candidate)}")
            if hasattr(candidate, 'content'):
                logger.info(f"Content: {candidate.content}")
            else:
                logger.info("No content attribute in candidate")
                
            if hasattr(candidate, 'finish_reason'):
                logger.info(f"Finish reason: {candidate.finish_reason}")
                if candidate.finish_reason and str(candidate.finish_reason) == "FinishReason.MALFORMED_FUNCTION_CALL":
                    raise Exception("Gemini API returned MALFORMED_FUNCTION_CALL - function schema is invalid")
                elif candidate.finish_reason and str(candidate.finish_reason) == "FinishReason.SAFETY":
                    raise Exception("Gemini API blocked request due to safety concerns")
                elif candidate.finish_reason and str(candidate.finish_reason) == "FinishReason.RECITATION":
                    raise Exception("Gemini API blocked request due to recitation concerns")
                
            if not candidate or not candidate.content:
                raise Exception("No content returned from Gemini API")
            
            if not candidate.content.parts or len(candidate.content.parts) == 0:
                raise Exception("No parts returned from Gemini API")
            
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    args = part.function_call.args
                    confidence_scores = args.get("confidence_scores", {})
                    warnings = args.get("warnings", [])
                    
                    if request.enhancement_options.get("suggest_contact", True):
                        enhanced_data["company_name"] = SuggestionValue(
                            value=args.get("company_name", ""),
                            confidence=confidence_scores.get("company_name", 0.5),
                            source="scraped from website",
                            reasoning="Extracted from website meta tags and content",
                            should_auto_apply=confidence_scores.get("company_name", 0.5) > 0.85
                        )
                        
                        if enhanced_data["company_name"].should_auto_apply:
                            suggestions_applied += 1
                    
                    if request.enhancement_options.get("suggest_industry", True):
                        enhanced_data["industry"] = SuggestionValue(
                            value=args.get("industry", ""),
                            confidence=confidence_scores.get("industry", 0.5),
                            source="inferred from website content",
                            reasoning="Analyzed website content to determine primary industry",
                            should_auto_apply=confidence_scores.get("industry", 0.5) > 0.85
                        )
                        
                        if enhanced_data["industry"].should_auto_apply:
                            suggestions_applied += 1
                    
                    if request.enhancement_options.get("suggest_company_size", True):
                        enhanced_data["company_size"] = SuggestionValue(
                            value=args.get("company_size", ""),
                            confidence=0.7,  # Always moderate confidence for size estimation
                            source="estimated from website content",
                            reasoning="Estimated based on website complexity and content",
                            should_auto_apply=False  # Never auto-apply size estimates
                        )
                    
                    if request.enhancement_options.get("suggest_contact", True):
                        contact_name = args.get("contact_name", "")
                        contact_email = args.get("contact_email", "")
                        contact_phone = args.get("contact_phone", "")
                        
                        if contact_phone:
                            contact_phone = contact_phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                        
                        if contact_name or contact_email or contact_phone:
                            primary_contact = {
                                "name": contact_name,
                                "email": contact_email,
                                "phone": contact_phone
                            }
                            
                            enhanced_data["primary_contact"] = SuggestionValue(
                                value=primary_contact,
                                confidence=confidence_scores.get("contact_info", 0.5),
                                source="scraped from contact page",
                                reasoning="Found in website contact information",
                                should_auto_apply=confidence_scores.get("contact_info", 0.5) > 0.85
                            )
                            
                            if enhanced_data["primary_contact"].should_auto_apply:
                                suggestions_applied += 1
                    
                    if request.enhancement_options.get("suggest_address", True):
                        address_line1 = args.get("address_line1", "")
                        address_city = args.get("address_city", "")
                        address_state = args.get("address_state", "")
                        address_pincode = args.get("address_pincode", "")
                        
                        if address_line1 or address_city or address_state or address_pincode:
                            address = {
                                "line1": address_line1,
                                "city": address_city,
                                "state": address_state,
                                "pincode": address_pincode
                            }
                            
                            enhanced_data["address"] = SuggestionValue(
                                value=address,
                                confidence=confidence_scores.get("address", 0.5),
                                source="scraped from contact page",
                                reasoning="Found in website contact information",
                                should_auto_apply=confidence_scores.get("address", 0.5) > 0.85
                            )
                            
                            if enhanced_data["address"].should_auto_apply:
                                suggestions_applied += 1
                    
                    break
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Account enhancement completed in {processing_time}ms")
            
            return AccountEnhancementResponse(
                enhanced_data=enhanced_data,
                processing_time_ms=processing_time,
                warnings=warnings,
                suggestions_applied=suggestions_applied
            )
            
        except Exception as e:
            logger.error(f"Account enhancement failed: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to enhance account data",
                details=str(e)
            )
    
    async def validate_address(
        self, 
        request: AddressValidationRequest
    ) -> AddressValidationResponse:
        """
        Validate address using AI and suggest corrections.
        """
        try:
            validate_address_function = {
                "name": "validate_address",
                "description": "Validate and correct address information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_valid": {"type": "boolean"},
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {"type": "string"},
                                    "current_value": {"type": "string"},
                                    "suggested_value": {"type": "string"},
                                    "issue_type": {"type": "string"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                                }
                            }
                        },
                        "corrected_address": {
                            "type": "object",
                            "properties": {
                                "line1": {"type": "string"},
                                "line2": {"type": "string"},
                                "city": {"type": "string"},
                                "state": {"type": "string"},
                                "country": {"type": "string"},
                                "pincode": {"type": "string"}
                            }
                        },
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["is_valid", "issues", "corrected_address", "confidence"]
                }
            }
            
            tools = types.Tool(function_declarations=[validate_address_function])
            config = types.GenerateContentConfig(tools=[tools])
            
            prompt = f"""
            Validate and correct this address for {request.country_code}:
            
            Address: {request.address}
            
            Instructions:
            1. Check for spelling errors, format issues, missing fields
            2. Standardize format according to {request.country_code} standards
            3. Provide confidence scores for corrections
            4. Identify specific issues and suggest fixes
            
            Focus on:
            - Correct spelling of city names
            - Proper state/province abbreviations
            - Valid postal/zip code formats
            - Complete address components
            """
            
            response = self.model.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(parts=[{"text": prompt}])],
                config=config
            )
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    args = part.function_call.args
                    
                    return AddressValidationResponse(
                        is_valid=args["is_valid"],
                        issues=args["issues"],
                        corrected_address=args["corrected_address"],
                        confidence=args["confidence"]
                    )
            
            raise Exception("AI did not return structured response")
            
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to validate address",
                details=str(e)
            )
    
    async def suggest_industry(
        self, 
        request: IndustrySuggestionRequest
    ) -> IndustrySuggestionResponse:
        """
        Suggest industry/sector based on website, name, or description.
        """
        try:
            context_parts = []
            
            if request.website_url:
                scraped_data = await scrape_text_with_bs4(str(request.website_url))
                if "text" in scraped_data:
                    context_parts.append(f"Website content: {scraped_data['text'][:2000]}")
            
            if request.company_name:
                context_parts.append(f"Company name: {request.company_name}")
            
            if request.description:
                context_parts.append(f"Description: {request.description}")
            
            if not context_parts:
                raise MegapolisHTTPException(
                    status_code=400,
                    message="At least one of website_url, company_name, or description must be provided"
                )
            
            suggest_industry_function = {
                "name": "suggest_industry",
                "description": "Suggest primary industry sector",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "suggested_industry": {
                            "type": "string",
                            "description": "Primary industry sector"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "alternatives": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Alternative industry classifications"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explanation for the industry suggestion"
                        }
                    },
                    "required": ["suggested_industry", "confidence", "reasoning"]
                }
            }
            
            tools = types.Tool(function_declarations=[suggest_industry_function])
            config = types.GenerateContentConfig(tools=[tools])
            
            prompt = f"""
            Analyze the following information and suggest the primary industry sector:
            
            {chr(10).join(context_parts)}
            
            Instructions:
            1. Identify the primary industry sector
            2. Provide confidence score based on clarity
            3. List alternative industry classifications if applicable
            4. Explain your reasoning
            
            Common industries: Technology, Healthcare, Finance, Retail, Manufacturing, 
            Education, Government, Non-profit, Real Estate, Transportation, etc.
            """
            
            response = self.model.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(parts=[{"text": prompt}])],
                config=config
            )
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    args = part.function_call.args
                    
                    return IndustrySuggestionResponse(
                        suggested_industry=args["suggested_industry"],
                        confidence=args["confidence"],
                        alternatives=args.get("alternatives", []),
                        reasoning=args["reasoning"]
                    )
            
            raise Exception("AI did not return structured response")
            
        except Exception as e:
            logger.error(f"Industry suggestion failed: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to suggest industry",
                details=str(e)
            )

    async def enhance_opportunity_data(self, request) -> AccountEnhancementResponse:
        """
        Enhance opportunity data using AI based on company website.
        Focuses on opportunity-specific fields like project values, descriptions, stages, etc.
        """
        try:
            start_time = time.time()
            
            scraped_data = await scrape_text_with_bs4(str(request.company_website))
            if "error" in scraped_data:
                raise Exception(f"Failed to scrape website: {scraped_data['error']}")
            
            # Use the new API format without function declarations
            
            partial_data_str = ""
            if hasattr(request, 'partial_data') and request.partial_data:
                partial_data_str = f"\nAlready entered data: {request.partial_data}"
            
            prompt = f"""
You are an expert Business Data Analyst AI trained to analyze company websites and extract **high-value business opportunities, projects, and leads** with 90%+ accuracy.

Your task is to analyze the following website and identify **in-progress or potential opportunities**, along with all relevant project details.

🌐 Website URL:
{request.company_website}{partial_data_str}

📄 Website Content:
{scraped_data['text'][:4000]}

---

### 🎯 OBJECTIVE
Your goal is to:
1. Detect all **in-progress, active, or upcoming projects/opportunities**.
2. Extract detailed project and company data.
3. Generate structured, high-confidence JSON output.
4. Tag and categorize opportunities for **automatic dumping into our CRM**.

---

### 🧩 EXTRACTION RULES

#### 🏗️ 1. OPPORTUNITY & PROJECT DETECTION
- Look for sections or pages mentioning:
  - "Projects", "Programs", "Opportunities", "RFPs", "Tenders", "Contracts", "Bids"
  - Status tags like "In Progress", "Ongoing", "Active", "Under Construction", "Upcoming"
- If the website contains URLs or subpages like `/projects/`, `/programs/`, `/tenders/`, `/rfp/`, or `/contracts/` — note them for crawling.
- Extract the following:
  - Project/Opportunity Name
  - Current Status (In-progress, Planned, Completed)
  - Project Scope or Description
  - Budget, Value, or Funding Amount
  - Start Date, End Date (if available)
  - Key Documents or Reports (links to PDFs or attachments)
  - Related Stakeholders, Contractors, or Departments

Example:
- Website: `https://octa.net/programs-projects/projects/freeway-projects/overview`
  - Found: "I-5 County Line to Avenida Pico Improvement Project"
  - Extract details: Description, status (in progress), documents, and other available metadata.

---

#### 📍 2. LOCATION EXTRACTION
- Identify full company or project address from:
  - Footer, Contact page, About page, or Project details page.
- Look for keywords: "Address:", "Location:", "Headquarters:", "Contact:"
- Extract complete structured address:
  **Building/Street + City + State + Zip + Country**
- Example: "B-6, Block E, E-59, Noida Sector 3, Noida, UP, India-201301"
- If not found → return "Address not available" with low confidence (0.2).

---

#### 💼 3. MARKET SECTOR ANALYSIS
Determine the **primary business sector** of the company:
- **Technology** → SaaS, IT, AI, software, web/app development
- **Infrastructure** → Roads, bridges, public works, transportation
- **Construction** → Buildings, real estate, contracting
- **Energy** → Utilities, renewable energy, oil & gas
- **Healthcare** → Medical, pharma, clinical services
- **Finance** → Banking, insurance, fintech
- **Education** → Universities, training, e-learning
- **Manufacturing** → Production, industrial
Return only the **most relevant** sector name.

---

#### 📈 4. SALES STAGE IDENTIFICATION
Based on project or content wording:
- **Prospecting** → Default for new opportunities
- **Qualification** → If company is "evaluating", "reviewing", or "shortlisting"
- **Proposal** → If "bidding", "tender submitted", or "proposal stage"
- **Negotiation** → If "negotiating", "finalizing", or "awarding"
- **Closed Won** → If "contract awarded", "project executed", or "completed successfully"
- **Closed Lost** → If "unsuccessful", "not selected", or "cancelled"

---

#### 💰 5. PROJECT VALUE ESTIMATION
- Identify or infer project value or range from:
  - Budget, funding, cost, or tender value.
- Use these standard ranges:
  - "<$50K", "$50K-$100K", "$100K-$500K", "$500K-$2M", "$2M+"
- If not mentioned, estimate based on company or project type.

---

#### 🧾 6. PROJECT DESCRIPTION
Write a detailed, professional, and concise description covering:
- Objective or goal of the project
- Scope of work
- Technologies or methodologies (if mentioned)
- Key deliverables or milestones
- Target beneficiaries or industries

---

#### 🏷️ 7. TAGGING & STATUS
Add an internal tag for dumping into CRM:
- `"tag": "in-progress"` → for ongoing opportunities
- `"tag": "planned"` → for upcoming projects
- `"tag": "completed"` → for closed or finished projects
- `"tag": "lead"` → for potential opportunities

---

### 🧮 CONFIDENCE SCORING
For each extracted element, assign confidence levels:
- 0.9–1.0 → Explicitly mentioned
- 0.7–0.8 → Strongly inferred
- 0.5–0.6 → Moderately inferred
- 0.3–0.4 → Weak inference
- 0.1–0.2 → Very uncertain / not found

---

### 📦 RETURN FORMAT (STRICT JSON)
Return a **valid JSON object** only:

{{
    "opportunity_name": "Project/Opportunity Name",
    "project_status": "In Progress / Planned / Completed",
    "project_value": "$100K-$500K",
    "project_description": "Detailed professional description of the project or opportunity.",
    "documents": ["list of document URLs if available"],
    "start_date": "YYYY-MM-DD or 'Not available'",
    "end_date": "YYYY-MM-DD or 'Not available'",
    "location": "Complete company or project address",
    "market_sector": "Primary sector (e.g., Infrastructure, Technology, Construction)",
    "sales_stage": "Prospecting / Proposal / Negotiation / Closed Won",
    "tag": "in-progress / planned / completed / lead",
    "confidence_scores": {{
        "opportunity_name": 0.9,
        "project_value": 0.7,
        "project_description": 0.8,
        "location": 0.9,
        "market_sector": 0.9,
        "sales_stage": 0.6
    }},
    "warnings": []
}}
"""
            
            logger.info("Calling Gemini API for opportunity enhancement")
            response = self.model.generate_content(prompt)
            
            enhanced_data = {}
            warnings = []
            suggestions_applied = 0
            
            try:
                import json
                response_text = response.text.strip()
                
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                result = json.loads(response_text)
                
                confidence_scores = result.get("confidence_scores", {}) or {}
                warnings = result.get("warnings", []) or []
                
                def safe_confidence(key: str, default: float = 0.5) -> float:
                    value = confidence_scores.get(key, default)
                    return float(value) if value is not None else default
                
                opportunity_name_conf = safe_confidence("opportunity_name")
                enhanced_data["opportunity_name"] = SuggestionValue(
                    value=result.get("opportunity_name", ""),
                    confidence=opportunity_name_conf,
                    source="extracted from website content",
                    reasoning="Based on services offered or current projects",
                    should_auto_apply=opportunity_name_conf > 0.7
                )
                
                if enhanced_data["opportunity_name"].should_auto_apply:
                    suggestions_applied += 1
                
                project_value_conf = safe_confidence("project_value")
                enhanced_data["project_value"] = SuggestionValue(
                    value=result.get("project_value", ""),
                    confidence=project_value_conf,
                    source="inferred from pricing or case studies",
                    reasoning="Estimated based on pricing information or project examples",
                    should_auto_apply=project_value_conf > 0.7
                )
                
                if enhanced_data["project_value"].should_auto_apply:
                    suggestions_applied += 1
                
                project_desc_conf = safe_confidence("project_description")
                enhanced_data["project_description"] = SuggestionValue(
                    value=result.get("project_description", ""),
                    confidence=project_desc_conf,
                    source="extracted from service descriptions",
                    reasoning="Based on detailed service offerings or case studies",
                    should_auto_apply=project_desc_conf > 0.7
                )
                
                if enhanced_data["project_description"].should_auto_apply:
                    suggestions_applied += 1
                
                location_conf = safe_confidence("location")
                location_value = result.get("location", "")
                # If location is empty or generic, try to extract from scraped data
                if not location_value or location_value == "Address not available":
                    location_value = self._extract_address_from_content(scraped_data['text'])
                # If still not found, leave blank (not "Address not available")
                if location_value == "Address not available":
                    location_value = ""
                enhanced_data["location"] = SuggestionValue(
                    value=location_value,
                    confidence=location_conf if location_value else 0.1,
                    source="extracted from website footer, contact, or about pages",
                    reasoning="Complete address with street, city, state, zip code extracted from website",
                    should_auto_apply=location_conf > 0.6 and location_value != ""
                )
                
                if enhanced_data["location"].should_auto_apply:
                    suggestions_applied += 1
                
                market_sector_conf = safe_confidence("market_sector")
                market_sector_value = result.get("market_sector", "Technology")  # Default to Technology for tech companies
                if not market_sector_value or market_sector_value.strip() == "":
                    market_sector_value = "Technology"
                enhanced_data["market_sector"] = SuggestionValue(
                    value=market_sector_value,
                    confidence=market_sector_conf if market_sector_value != "Technology" else 0.7,
                    source="analyzed from company's primary business focus and services",
                    reasoning="Based on company's main business activities, services offered, and target market",
                    should_auto_apply=market_sector_conf > 0.6
                )
                
                if enhanced_data["market_sector"].should_auto_apply:
                    suggestions_applied += 1
                
                sales_stage_conf = safe_confidence("sales_stage")
                sales_stage_value = result.get("sales_stage", "Prospecting")  # Default to Prospecting
                if not sales_stage_value or sales_stage_value.strip() == "":
                    sales_stage_value = "Prospecting"
                enhanced_data["sales_stage"] = SuggestionValue(
                    value=sales_stage_value,
                    confidence=sales_stage_conf if sales_stage_value != "Prospecting" else 0.6,
                    source="inferred from business stage or defaulted to Prospecting",
                    reasoning="Based on project status indicators or defaulted to Prospecting for new opportunities",
                    should_auto_apply=sales_stage_conf > 0.6
                )
                
                if enhanced_data["sales_stage"].should_auto_apply:
                    suggestions_applied += 1
                
                # Add new fields from enhanced prompt
                project_status_value = result.get("project_status", "Not available")
                enhanced_data["project_status"] = SuggestionValue(
                    value=project_status_value,
                    confidence=safe_confidence("project_status", 0.5),
                    source="extracted from project status indicators",
                    reasoning="Based on project timeline and status mentions",
                    should_auto_apply=False  # For display only
                )
                
                documents_value = result.get("documents", [])
                enhanced_data["documents"] = SuggestionValue(
                    value=documents_value if documents_value else [],
                    confidence=safe_confidence("documents", 0.5),
                    source="extracted document links from website",
                    reasoning="PDFs, reports, and attachments found on website",
                    should_auto_apply=False  # For display only
                )
                
                start_date_value = result.get("start_date", "Not available")
                enhanced_data["start_date"] = SuggestionValue(
                    value=start_date_value,
                    confidence=safe_confidence("start_date", 0.5),
                    source="extracted from project timeline",
                    reasoning="Project start date if explicitly mentioned",
                    should_auto_apply=False  # For display only
                )
                
                end_date_value = result.get("end_date", "Not available")
                enhanced_data["end_date"] = SuggestionValue(
                    value=end_date_value,
                    confidence=safe_confidence("end_date", 0.5),
                    source="extracted from project timeline",
                    reasoning="Project end/completion date if mentioned",
                    should_auto_apply=False  # For display only
                )
                
                tag_value = result.get("tag", "lead")
                enhanced_data["tag"] = SuggestionValue(
                    value=tag_value,
                    confidence=safe_confidence("tag", 0.7),
                    source="categorized based on project status",
                    reasoning="Tag for CRM dumping: in-progress, planned, completed, or lead",
                    should_auto_apply=False  # For display only
                )
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text}")
                raise Exception(f"Failed to parse AI response: {e}")
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Opportunity enhancement completed in {processing_time}ms")
            
            return AccountEnhancementResponse(
                enhanced_data=enhanced_data,
                processing_time_ms=processing_time,
                warnings=warnings,
                suggestions_applied=suggestions_applied
            )
            
        except Exception as e:
            logger.error(f"Opportunity enhancement failed: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to enhance opportunity data",
                details=str(e)
            )


class AISuggestionService:
    """AI Suggestion Service for generating AI-powered suggestions"""
    
    def __init__(self):
        self.logger = logger
    
    async def get_suggestions(self, request: AISuggestionRequest) -> AISuggestionResponse:
        """Generate AI suggestions based on context"""
        try:
            # Mock implementation - replace with actual AI logic
            suggestion_id = f"suggestion_{int(time.time())}"
            
            return AISuggestionResponse(
                id=suggestion_id,
                suggestion=f"AI suggestion for: {request.context[:50]}...",
                confidence_score=0.85,
                suggestion_type=request.suggestion_type,
                context=request.context,
                created_at=datetime.utcnow(),
                user_id=request.user_id,
                account_id=request.account_id,
                opportunity_id=request.opportunity_id
            )
        except Exception as e:
            self.logger.error(f"Error generating AI suggestions: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to generate AI suggestions",
                details=str(e)
            )
    
    async def get_suggestion_by_id(self, suggestion_id: str) -> AISuggestionResponse:
        """Get a specific AI suggestion by ID"""
        try:
            # Mock implementation - replace with actual database lookup
            return AISuggestionResponse(
                id=suggestion_id,
                suggestion="Retrieved AI suggestion",
                confidence_score=0.90,
                suggestion_type="general",
                context="Retrieved context",
                created_at=datetime.utcnow()
            )
        except Exception as e:
            self.logger.error(f"Error retrieving AI suggestion: {e}")
            raise MegapolisHTTPException(
                status_code=500,
                message="Failed to retrieve AI suggestion",
                details=str(e)
            )


data_enrichment_service = DataEnrichmentService()
ai_suggestion_service = AISuggestionService()