#!/usr/bin/env python3
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.data_enrichment import data_enrichment_service

# Disable AI enhancement
data_enrichment_service.disable_ai_enhancement()
print("AI enhancement has been disabled. The service will now return fallback data instead of calling the Gemini API.")