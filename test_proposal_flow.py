#!/usr/bin/env python3
"""
Quick test script for proposal flow endpoints
Tests: Create proposal, Upload document, Get proposal
"""
import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_BASE = f"{BASE_URL}/api"

# Test credentials - UPDATE THESE
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "test123")

def get_auth_token():
    """Login and get auth token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None
    data = response.json()
    token = data.get("access_token") or data.get("token")
    if not token:
        print(f"❌ No token in response: {data}")
        return None
    print("✅ Login successful")
    return token

def create_test_proposal(token):
    """Create a test proposal"""
    print("\n📝 Creating test proposal...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": "Test Proposal - Flow Test",
        "proposal_type": "proposal",
        "currency": "USD"
    }
    response = requests.post(
        f"{API_BASE}/proposals/create",
        headers=headers,
        json=payload
    )
    if response.status_code not in [200, 201]:
        print(f"❌ Proposal creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    data = response.json()
    proposal_id = data.get("id")
    print(f"✅ Proposal created: {proposal_id}")
    return proposal_id

def create_test_file():
    """Create a test file for upload"""
    test_file = Path("test_upload.txt")
    test_file.write_text("This is a test file for proposal document upload testing.")
    return test_file

def upload_document(token, proposal_id, test_file):
    """Upload a document to the proposal"""
    print(f"\n📤 Uploading document to proposal {proposal_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(test_file, "rb") as f:
        files = {"file": (test_file.name, f, "text/plain")}
        data = {"category": "attachment"}
        response = requests.post(
            f"{API_BASE}/proposals/{proposal_id}/documents/upload",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Document upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    result = response.json()
    print(f"✅ Document uploaded successfully")
    print(f"   Proposal ID: {result.get('id')}")
    print(f"   Proposal Number: {result.get('proposal_number')}")
    return True

def get_proposal(token, proposal_id):
    """Get proposal details"""
    print(f"\n📋 Fetching proposal {proposal_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/proposals/{proposal_id}",
        headers=headers
    )
    if response.status_code != 200:
        print(f"❌ Failed to fetch proposal: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    data = response.json()
    print(f"✅ Proposal fetched successfully")
    print(f"   Title: {data.get('title')}")
    print(f"   Status: {data.get('status')}")
    print(f"   Documents: {len(data.get('documents', []))}")
    return data

def main():
    print("🧪 Testing Proposal Flow API Endpoints\n")
    print("=" * 60)
    
    # Step 1: Login
    token = get_auth_token()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print("Please update TEST_EMAIL and TEST_PASSWORD in the script")
        return
    
    # Step 2: Create proposal
    proposal_id = create_test_proposal(token)
    if not proposal_id:
        print("\n❌ Cannot proceed without proposal ID")
        return
    
    # Step 3: Create test file
    test_file = create_test_file()
    try:
        # Step 4: Upload document
        upload_success = upload_document(token, proposal_id, test_file)
        if not upload_success:
            print("\n❌ Document upload failed")
            return
        
        # Step 5: Verify proposal with document
        proposal = get_proposal(token, proposal_id)
        if proposal:
            doc_count = len(proposal.get('documents', []))
            if doc_count > 0:
                print(f"\n✅ SUCCESS: Proposal has {doc_count} document(s)")
            else:
                print(f"\n⚠️  WARNING: Proposal created but no documents found")
        
        print("\n" + "=" * 60)
        print("✅ Proposal flow test completed successfully!")
        print(f"\nTest Proposal ID: {proposal_id}")
        print(f"You can view it at: {BASE_URL}/api/proposals/{proposal_id}")
        
    finally:
        # Cleanup test file
        if test_file.exists():
            test_file.unlink()
            print(f"\n🧹 Cleaned up test file: {test_file}")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running on", BASE_URL, "?")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

