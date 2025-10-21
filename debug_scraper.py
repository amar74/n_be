#!/usr/bin/env python3
"""
Debug script to check why scraper fails in service context
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.scraper import scrape_text_with_bs4
from app.schemas.data_enrichment import AccountEnhancementRequest

async def debug_scraper():
    """Debug the scraper in service context"""
    print("🔍 Debugging scraper in service context...")
    
    # Test the scraper directly
    print("\n1. Testing scraper directly:")
    result = await scrape_text_with_bs4("https://www.google.com")
    print(f"   Result keys: {list(result.keys())}")
    print(f"   Has 'text': {'text' in result}")
    print(f"   Has 'content': {'content' in result}")
    print(f"   Text length: {len(result.get('text', ''))}")
    print(f"   Content length: {len(result.get('content', ''))}")
    
    # Test with the same URL format as in the service
    print("\n2. Testing with service URL format:")
    service_url = "https://www.google.com/"
    result2 = await scrape_text_with_bs4(service_url)
    print(f"   URL: {service_url}")
    print(f"   Text length: {len(result2.get('text', ''))}")
    print(f"   First 100 chars: {result2.get('text', '')[:100]}")
    
    # Test the AccountEnhancementRequest
    print("\n3. Testing AccountEnhancementRequest:")
    request = AccountEnhancementRequest(
        company_website="https://www.google.com/",
        company_name="Google",
        partial_data={}
    )
    print(f"   Website: {request.company_website}")
    print(f"   Type: {type(request.company_website)}")
    print(f"   String conversion: {str(request.company_website)}")

if __name__ == "__main__":
    asyncio.run(debug_scraper())