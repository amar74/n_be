#!/usr/bin/env python3
"""
Test script to check if Gemini API is working properly
"""
import asyncio
import sys
import os
import time

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.data_enrichment import DataEnrichmentService
from app.schemas.data_enrichment import AccountEnhancementRequest

async def test_gemini():
    """Test the Gemini API with a simple request"""
    print("🔍 Testing Gemini API...")
    
    # Create a simple test request
    test_request = AccountEnhancementRequest(
        company_website="https://www.google.com",
        company_name="Google",
        partial_data={}
    )
    
    service = DataEnrichmentService()
    
    print("📡 Making request to Gemini API...")
    start_time = time.time()
    
    try:
        result = await service.enhance_account_data(test_request)
        end_time = time.time()
        
        print(f"✅ Success! Response received in {end_time - start_time:.2f} seconds")
        print(f"📊 Enhanced data keys: {list(result.enhanced_data.keys())}")
        print(f"⏱️ Processing time: {result.processing_time_ms}ms")
        print(f"⚠️ Warnings: {result.warnings}")
        
    except Exception as e:
        end_time = time.time()
        print(f"❌ Error after {end_time - start_time:.2f} seconds: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())