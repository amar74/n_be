import asyncio
import time
from typing import Dict, Any, Optional, List
from app.schemas.data_enrichment import (
    OrganizationNameRequest, OrganizationNameResponse,
    AccountEnhancementRequest, AccountEnhancementResponse,
    AddressValidationRequest, AddressValidationResponse,
    ContactValidationRequest, ContactValidationResponse,
    IndustrySuggestionRequest, IndustrySuggestionResponse,
    CompanySizeSuggestionRequest, CompanySizeSuggestionResponse,
    SuggestionValue
)
from app.utils.scraper import scrape_text_with_bs4
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.environment import environment
import google.generativeai as genai
from google.generativeai import types


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
    
    async def _call_gemini_with_timeout(self, prompt: str, max_retries: int = 1) -> Any:
        """Call Gemini API with timeout and better error handling"""
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Gemini API call attempt {attempt + 1}/{max_retries + 1}")
                # Use asyncio.wait_for to add timeout
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: self.model.generate_content(prompt)
                    ),
                    timeout=self.timeout
                )
                logger.info(f"Gemini API call successful on attempt {attempt + 1}")
                return response
            except asyncio.TimeoutError:
                logger.error(f"Gemini API call timed out after {self.timeout} seconds (attempt {attempt + 1})")
                if attempt == max_retries:
                    raise MegapolisHTTPException(
                        status_code=408,
                        message="AI processing timeout. Please try again.",
                        details=f"Request timed out after {self.timeout} seconds"
                    )
                else:
                    logger.info(f"Retrying Gemini API call (attempt {attempt + 2})")
                    await asyncio.sleep(2)  # Wait 2 seconds before retry
            except Exception as e:
                logger.error(f"Gemini API call failed: {e} (attempt {attempt + 1})")
                # Check for DNS/network issues
                if any(keyword in str(e).lower() for keyword in ["dns", "network", "unavailable", "connection"]):
                    logger.warning("Network connectivity issue detected, will use fallback")
                    raise MegapolisHTTPException(
                        status_code=503,
                        message="AI service temporarily unavailable. Using fallback data.",
                        details="Network connectivity issue with AI service"
                    )
                # Check if it's a specific Gemini API error
                elif "quota" in str(e).lower():
                    raise MegapolisHTTPException(
                        status_code=429,
                        message="AI service quota exceeded. Please try again later.",
                        details="API quota limit reached"
                    )
                elif "api" in str(e).lower() and "key" in str(e).lower():
                    raise MegapolisHTTPException(
                        status_code=500,
                        message="AI service configuration error. Please contact support.",
                        details="API key or configuration issue"
                    )
                elif attempt == max_retries:
                    raise MegapolisHTTPException(
                        status_code=500,
                        message="AI processing failed. Please try again.",
                        details=str(e)
                    )
                else:
                    logger.info(f"Retrying Gemini API call after error (attempt {attempt + 2})")
                    await asyncio.sleep(2)  # Wait 2 seconds before retry
    
    async def suggest_organization_name(
        self, 
        request: OrganizationNameRequest
    ) -> OrganizationNameResponse:
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
            Website: {request.website_url}
            Content: {scraped_data['text'][:3000]}
            
            Extract the company name from this website content.
            """
            
            response = await self._call_gemini_with_timeout(
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
    
    async def validate_address(
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
            
            prompt = f"""Analyze this website and extract company information:

Website: {request.company_website}
Content: {scraped_data['text'][:1500]}

Please provide:
1. Company name
2. Industry/sector
3. Company size (small/medium/large)
4. Contact email
5. Phone number
6. Address

Format as JSON with confidence scores (0-1). Be concise and accurate."""
            
            logger.info("Calling Gemini API for account enhancement")
            logger.info(f"Processing website: {request.company_website}")
            logger.info(f"Website content length: {len(scraped_data.get('text', ''))} characters")
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            # Try AI enhancement with retry mechanism
            try:
                response = await self._call_gemini_with_timeout(prompt)
                logger.info(f"Gemini API response received: {type(response)}")
                logger.info("AI processing completed successfully")
            except Exception as ai_error:
                logger.error(f"AI enhancement failed, using intelligent fallback: {ai_error}")
                
                # Use intelligent fallback extraction
                try:
                    basic_info = self._extract_basic_info_from_website(
                        scraped_data.get('text', ''), 
                        request.company_website
                    )
                    
                    fallback_data = {
                        "company_name": SuggestionValue(
                            value=basic_info.get("company_name") or request.partial_data.get("company_name") or "Unknown Company",
                            confidence=0.7,
                            source="intelligent_fallback",
                            reasoning="AI unavailable, extracted from website content"
                        ),
                        "industry": SuggestionValue(
                            value=basic_info.get("industry", "Technology"),
                            confidence=0.6,
                            source="intelligent_fallback",
                            reasoning="Industry detected from website keywords"
                        ),
                        "contact_email": SuggestionValue(
                            value=basic_info.get("contact_email", "Unknown"),
                            confidence=0.8 if basic_info.get("contact_email") != "Unknown" else 0.3,
                            source="intelligent_fallback",
                            reasoning="Email extracted from website content"
                        ),
                        "contact_phone": SuggestionValue(
                            value=basic_info.get("contact_phone", "Unknown"),
                            confidence=0.8 if basic_info.get("contact_phone") != "Unknown" else 0.3,
                            source="intelligent_fallback",
                            reasoning="Phone number extracted from website content"
                        ),
                        "address": SuggestionValue(
                            value=basic_info.get("address", "Unknown"),
                            confidence=0.6 if basic_info.get("address") != "Unknown" else 0.3,
                            source="intelligent_fallback",
                            reasoning="Address extracted from website content"
                        )
                    }
                    
                    logger.info("Using intelligent fallback extraction")
                    return AccountEnhancementResponse(
                        enhanced_data=fallback_data,
                        processing_time_ms=int((time.time() - start_time) * 1000),
                        warnings=[f"AI enhancement failed, using intelligent fallback: {str(ai_error)}"],
                        suggestions_applied=len([k for k, v in fallback_data.items() if v.confidence > 0.5])
                    )
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback extraction also failed: {fallback_error}")
                    # Final fallback - basic data
                    fallback_data = {
                        "company_name": SuggestionValue(
                            value=request.partial_data.get("company_name") or "Unknown Company",
                            confidence=0.3,
                            source="basic_fallback",
                            reasoning="AI and fallback extraction failed, using basic data"
                        )
                    }
                    
                    logger.info("Using basic fallback data")
                    return AccountEnhancementResponse(
                        enhanced_data=fallback_data,
                        processing_time_ms=int((time.time() - start_time) * 1000),
                        warnings=[f"AI enhancement failed: {str(ai_error)}", f"Fallback extraction failed: {str(fallback_error)}"],
                        suggestions_applied=0
                    )
            
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
            
            # Return fallback data instead of failing completely
            fallback_data = {
                "company_name": SuggestionValue(
                    value=request.partial_data.get("company_name") or "Unknown Company",
                    confidence=0.3,
                    source="fallback",
                    reasoning="AI enhancement failed, using fallback data"
                )
            }
            
            logger.info("Returning fallback data due to AI enhancement failure")
            return AccountEnhancementResponse(
                enhanced_data=fallback_data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                warnings=[f"AI enhancement failed: {str(e)}"],
                suggestions_applied=0
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
            
            response = await self._call_gemini_with_timeout(
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
            
            response = await self._call_gemini_with_timeout(
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
            Analyze this company website and extract opportunity-specific information for creating a sales opportunity.
            
            Website URL: {request.company_website}{partial_data_str}
            
            Website Content:
            {scraped_data['text'][:4000]}
            
            Instructions:
            1. Focus on identifying potential business opportunities and projects
            2. Look for services offered, case studies, project portfolios, or bidding opportunities
            3. Extract or infer opportunity-specific information:
               - Opportunity name from services, projects, or current offerings
               - Project value from pricing pages, case studies, or service descriptions
               - Project description from service offerings
               - Location from service areas, office locations, or project locations
               - Market sector from industries served or project types
               - Sales stage based on project status or business development stage
            4. Provide confidence scores for each field (0-1)
            5. Be conservative with confidence - only high confidence for clear information
            6. If information is not available, provide reasonable estimates or leave empty
            
            Focus on finding:
            - Current projects or services that could be opportunities
            - Pricing information or budget ranges
            - Service areas and locations
            - Target industries and market sectors
            - Project status or business development stage
            - Case studies or project portfolios
            - Bidding opportunities or RFP mentions
            
            Please return the information in the following JSON format:
            {{
                "opportunity_name": "suggested opportunity name",
                "project_value": "estimated project value or budget range",
                "project_description": "project description",
                "location": "primary service location",
                "market_sector": "primary market sector",
                "sales_stage": "suggested sales stage",
                "confidence_scores": {{
                    "opportunity_name": 0.8,
                    "project_value": 0.6,
                    "project_description": 0.7,
                    "location": 0.9,
                    "market_sector": 0.8,
                    "sales_stage": 0.5
                }},
                "warnings": ["any warnings about data quality or confidence"]
            }}
            """
            
            logger.info("Calling Gemini API for opportunity enhancement")
            response = await self._call_gemini_with_timeout(prompt)
            
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
                    reasoning="Based on service offerings",
                    should_auto_apply=project_desc_conf > 0.7
                )
                
                if enhanced_data["project_description"].should_auto_apply:
                    suggestions_applied += 1
                
                location_conf = safe_confidence("location")
                enhanced_data["location"] = SuggestionValue(
                    value=result.get("location", ""),
                    confidence=location_conf,
                    source="extracted from service areas",
                    reasoning="Based on service locations or project areas",
                    should_auto_apply=location_conf > 0.7
                )
                
                if enhanced_data["location"].should_auto_apply:
                    suggestions_applied += 1
                
                market_sector_conf = safe_confidence("market_sector")
                enhanced_data["market_sector"] = SuggestionValue(
                    value=result.get("market_sector", ""),
                    confidence=market_sector_conf,
                    source="inferred from industries served",
                    reasoning="Based on target industries or project types",
                    should_auto_apply=market_sector_conf > 0.7
                )
                
                if enhanced_data["market_sector"].should_auto_apply:
                    suggestions_applied += 1
                
                sales_stage_conf = safe_confidence("sales_stage")
                enhanced_data["sales_stage"] = SuggestionValue(
                    value=result.get("sales_stage", ""),
                    confidence=sales_stage_conf,
                    source="inferred from business stage",
                    reasoning="Based on project status or business development stage",
                    should_auto_apply=sales_stage_conf > 0.7
                )
                
                if enhanced_data["sales_stage"].should_auto_apply:
                    suggestions_applied += 1
                    
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


data_enrichment_service = DataEnrichmentService()