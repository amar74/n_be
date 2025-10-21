#!/usr/bin/env python3
"""
Debug script to check the data enrichment service step by step
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.data_enrichment import DataEnrichmentService
from app.schemas.data_enrichment import AccountEnhancementRequest
from app.utils.scraper import scrape_text_with_bs4

async def debug_service():
    """Debug the data enrichment service step by step"""
    print("🔍 Debugging data enrichment service...")
    
    # Create the service
    service = DataEnrichmentService()
    print(f"✅ Service created, AI enabled: {service.ai_enabled}")
    
    # Create test request
    request = AccountEnhancementRequest(
        company_website="https://www.google.com/",
        company_name="Google",
        partial_data={}
    )
    print(f"✅ Request created: {request.company_website}")
    
    # Test scraper directly in the same context
    print("\n🔍 Testing scraper in service context:")
    scraped_data = await scrape_text_with_bs4(str(request.company_website))
    print(f"   Scraped data keys: {list(scraped_data.keys())}")
    print(f"   Text length: {len(scraped_data.get('text', ''))}")
    print(f"   Has error: {'error' in scraped_data}")
    if 'error' in scraped_data:
        print(f"   Error: {scraped_data['error']}")
    else:
        print(f"   First 200 chars: {scraped_data.get('text', '')[:200]}")
    
    # Test the prompt creation
    print("\n🔍 Testing prompt creation:")
    prompt = f"""Extract company data from this website:

URL: {request.company_website}
Content: {scraped_data['text'][:2000]}

Extract: company name, industry, size, contact email, phone (E.164 format), address.
Return JSON with confidence scores (0-1) for each field.
Be conservative with confidence scores."""
    
    print(f"   Prompt length: {len(prompt)}")
    print(f"   Content in prompt: {len(scraped_data['text'][:2000])} characters")
    
    # Test if AI is disabled
    if not service.ai_enabled:
        print("\n✅ AI is disabled, should return fallback data")
        try:
            result = await service.enhance_account_data(request)
            print(f"   Result type: {type(result)}")
            print(f"   Enhanced data keys: {list(result.enhanced_data.keys())}")
            print(f"   Processing time: {result.processing_time_ms}ms")
            print(f"   Warnings: {result.warnings}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("\n⚠️ AI is enabled, this might timeout")

if __name__ == "__main__":
    asyncio.run(debug_service())