#!/usr/bin/env python3
"""Test script to check if export endpoint works"""

import requests
import sys

# Use the token from the logs
token = "YOUR_TOKEN_HERE"  # User needs to paste their token

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "text/csv"
}

url = "http://localhost:8000/api/accounts/export"

print(f"Testing: GET {url}")
print(f"Headers: {headers}")

try:
    response = requests.get(url, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"\n✓ SUCCESS!")
        print(f"Content length: {len(response.content)} bytes")
        print(f"First 200 chars: {response.text[:200]}")
    else:
        print(f"\n✗ FAILED!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    sys.exit(1)
