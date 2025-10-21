#!/usr/bin/env python3
"""
Test script to check if opportunity service is working
"""
import asyncio
import sys
import os
import uuid

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.opportunity_tabs import OpportunityTabsService
from app.db.session import get_session

async def test_opportunity_service():
    """Test the opportunity tabs service"""
    print("🔍 Testing opportunity tabs service...")
    
    try:
        async with get_session() as db:
            service = OpportunityTabsService(db)
            print("✅ Service created successfully")
            
            # Test with a valid UUID
            test_opportunity_id = uuid.UUID("2c63974b-5fa6-4bd0-b830-7aadd4b45a24")
            print(f"✅ Test opportunity ID: {test_opportunity_id}")
            
            # Test get_stakeholders
            print("\n🔍 Testing get_stakeholders...")
            try:
                stakeholders = await service.get_stakeholders(test_opportunity_id)
                print(f"✅ Stakeholders retrieved: {len(stakeholders)} items")
                print(f"   Type: {type(stakeholders)}")
            except Exception as e:
                print(f"❌ Error getting stakeholders: {e}")
            
            # Test get_drivers
            print("\n🔍 Testing get_drivers...")
            try:
                drivers = await service.get_drivers(test_opportunity_id)
                print(f"✅ Drivers retrieved: {len(drivers)} items")
            except Exception as e:
                print(f"❌ Error getting drivers: {e}")
                
    except Exception as e:
        print(f"❌ Error creating service: {e}")

if __name__ == "__main__":
    asyncio.run(test_opportunity_service())