#!/usr/bin/env python3
"""
Test script to verify frontend integration with AI enhancement
"""
import asyncio
import json
import httpx

async def test_ai_enhancement():
    """Test the AI enhancement endpoint"""
    
    # Test data
    test_data = {
        "company_website": "https://www.google.com",
        "partial_data": {"company_name": "Google"}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Y2E4OGJiMy00MDljLTRhYTAtYTUzNS05MWQ0OWEyMjQ0NGUiLCJ1c2VyX2lkIjoiNGNhODhiYjMtNDA5Yy00YWEwLWE1MzUtOTFkNDlhMjI0NDRlIiwiZXhwIjoxNzYxMTk1NzAzfQ.L8ch1rXrlwpHdiESiP-QFSa0PtDm77pucYWRAngWYjw"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("🔍 Testing AI enhancement endpoint...")
            response = await client.post(
                "http://localhost:8000/ai/enhance-account-data",
                json=test_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ AI enhancement successful!")
                print(f"📊 Processing time: {data.get('processing_time_ms', 0)}ms")
                print(f"📈 Suggestions applied: {data.get('suggestions_applied', 0)}")
                
                enhanced_data = data.get('enhanced_data', {})
                print("\n📋 Extracted data:")
                
                for field, suggestion in enhanced_data.items():
                    if suggestion.get('confidence', 0) >= 0.5:
                        print(f"  ✅ {field}: {suggestion.get('value')} (confidence: {suggestion.get('confidence')})")
                    else:
                        print(f"  ⚠️  {field}: {suggestion.get('value')} (confidence: {suggestion.get('confidence')}) - Low confidence")
                
                # Test frontend mapping
                print("\n🎯 Frontend field mapping test:")
                frontend_mapping = {
                    'company_name': 'name',
                    'contact_email': 'contact.email', 
                    'contact_phone': 'contact.phone',
                    'address': 'address.line1'
                }
                
                for backend_field, frontend_field in frontend_mapping.items():
                    if backend_field in enhanced_data:
                        suggestion = enhanced_data[backend_field]
                        if suggestion.get('confidence', 0) >= 0.5:
                            print(f"  ✅ {backend_field} -> {frontend_field}: {suggestion.get('value')}")
                        else:
                            print(f"  ⚠️  {backend_field} -> {frontend_field}: {suggestion.get('value')} (low confidence)")
                
                return True
            else:
                print(f"❌ AI enhancement failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing AI enhancement: {e}")
            return False

async def test_frontend_connectivity():
    """Test if frontend is accessible"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:5173", timeout=5.0)
            if response.status_code == 200:
                print("✅ Frontend is accessible")
                return True
            else:
                print(f"❌ Frontend returned status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

async def main():
    print("🚀 Testing Frontend Integration with AI Enhancement")
    print("=" * 60)
    
    # Test frontend connectivity
    print("\n1. Testing frontend connectivity...")
    frontend_ok = await test_frontend_connectivity()
    
    # Test AI enhancement
    print("\n2. Testing AI enhancement...")
    ai_ok = await test_ai_enhancement()
    
    print("\n" + "=" * 60)
    if frontend_ok and ai_ok:
        print("🎉 All tests passed! Frontend integration should work.")
        print("\n📝 Next steps:")
        print("1. Open http://localhost:5173/organization/create")
        print("2. Enter a website URL (e.g., https://www.google.com)")
        print("3. Check browser console for AI suggestion logs")
        print("4. Verify that form fields are auto-populated")
    else:
        print("❌ Some tests failed. Check the issues above.")
    
    return frontend_ok and ai_ok

if __name__ == "__main__":
    asyncio.run(main())