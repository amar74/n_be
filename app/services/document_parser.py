"""
Document Parser Service
Handles parsing of PDF, DOCX, XLS files and extracts structured data using AI.
"""
import io
import mimetypes
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import httpx
import google.generativeai as genai
from app.environment import environment
from app.utils.logger import get_logger

logger = get_logger("document_parser")

# Configure Gemini
genai.configure(api_key=environment.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


async def download_document(url: str) -> Optional[bytes]:
    """Download document from URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Error downloading document from {url}: {e}")
        return None


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF using PyPDF2 or pdfplumber."""
    try:
        try:
            import PyPDF2
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            try:
                import pdfplumber
                pdf_file = io.BytesIO(pdf_content)
                text = ""
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                logger.warning("Neither PyPDF2 nor pdfplumber installed. Install one: pip install PyPDF2 or pip install pdfplumber")
                return ""
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(docx_content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc_file = io.BytesIO(docx_content)
        doc = Document(doc_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except ImportError:
        logger.warning("python-docx not installed. Install: pip install python-docx")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""


def extract_text_from_xls(xls_content: bytes, file_extension: str) -> str:
    """Extract text from XLS/XLSX file."""
    try:
        if file_extension.lower() == '.xlsx':
            import openpyxl
            workbook = openpyxl.load_workbook(io.BytesIO(xls_content))
            text = ""
            for sheet in workbook.worksheets:
                text += f"\nSheet: {sheet.title}\n"
                for row in sheet.iter_rows(values_only=True):
                    row_text = " | ".join([str(cell) if cell else "" for cell in row])
                    if row_text.strip():
                        text += row_text + "\n"
            return text
        else:
            # For .xls files, would need xlrd
            logger.warning("XLS file parsing requires xlrd. Only XLSX supported with openpyxl.")
            return ""
    except ImportError:
        logger.warning("openpyxl not installed. Install: pip install openpyxl")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from XLS: {e}")
        return ""


async def parse_document(url: str) -> Dict[str, Any]:
    """
    Parse a document from URL and extract structured data.
    
    Returns:
        Dictionary with parsed text and extracted structured data
    """
    result = {
        "url": url,
        "file_type": None,
        "text": "",
        "structured_data": {},
        "error": None
    }
    
    try:
        # Download document
        content = await download_document(url)
        if not content:
            result["error"] = "Failed to download document"
            return result
        
        # Determine file type
        parsed_url = urlparse(url)
        file_path = parsed_url.path.lower()
        
        if file_path.endswith('.pdf'):
            result["file_type"] = "PDF"
            text = extract_text_from_pdf(content)
        elif file_path.endswith('.docx'):
            result["file_type"] = "DOCX"
            text = extract_text_from_docx(content)
        elif file_path.endswith(('.xls', '.xlsx')):
            result["file_type"] = "XLS" if file_path.endswith('.xls') else "XLSX"
            text = extract_text_from_xls(content, file_path[-4:])
        else:
            result["error"] = f"Unsupported file type: {file_path}"
            return result
        
        if not text:
            result["error"] = "No text extracted from document"
            return result
        
        result["text"] = text[:50000]  # Limit text size
        
        # Use AI to extract structured data
        structured_data = await extract_structured_data_from_text(text, url)
        result["structured_data"] = structured_data
        
    except Exception as e:
        logger.error(f"Error parsing document {url}: {e}")
        result["error"] = str(e)
    
    return result


async def extract_structured_data_from_text(text: str, source_url: str) -> Dict[str, Any]:
    """
    Use Gemini AI to extract structured data from document text.
    Focuses on opportunity-related information.
    """
    prompt = f"""You are an expert at extracting structured data from project documents, RFPs, tenders, and proposals.

Analyze the following document text and extract structured information about the opportunity/project:

Document Text:
{text[:20000]}

Extract and return ONLY valid JSON with this structure:
{{
  "project_title": "string or null",
  "client_name": "string or null",
  "project_value": "string or null (e.g., $2.5M, $500K)",
  "project_value_numeric": number or null,
  "deadline": "ISO date string or null",
  "expected_rfp_date": "ISO date string or null",
  "location": "string or null",
  "scope_summary": "string or null",
  "scope_items": ["string", ...],
  "requirements": ["string", ...],
  "contact_info": {{
    "name": "string or null",
    "email": "string or null",
    "phone": "string or null",
    "organization": "string or null"
  }},
  "key_dates": {{
    "submission_deadline": "ISO date string or null",
    "bid_opening": "ISO date string or null",
    "project_start": "ISO date string or null"
  }},
  "technical_requirements": ["string", ...],
  "budget_breakdown": {{
    "categories": [
      {{"name": "string", "amount": "string or number"}}
    ]
  }},
  "tags": ["string", ...]
}}

Rules:
- Use null for unknown fields
- Extract all relevant dates and convert to ISO format (YYYY-MM-DD)
- Extract all scope items and requirements as separate array items
- Identify project value in any format and provide both text and numeric versions
- Extract contact information if available
- Generate relevant tags based on project type, sector, location

Return ONLY the JSON object, no markdown or commentary."""

    try:
        response = model.generate_content(prompt)
        import json
        
        # Clean response text
        response_text = response.text.strip()
        if response_text.startswith("```"):
            # Remove markdown code blocks
            response_text = response_text.strip("```")
            if "\n" in response_text:
                lines = response_text.split("\n")
                if lines[0].startswith("json"):
                    lines = lines[1:]
                response_text = "\n".join(lines)
        
        structured_data = json.loads(response_text)
        return structured_data
    except Exception as e:
        logger.error(f"Error extracting structured data with AI: {e}")
        return {}


async def parse_multiple_documents(urls: List[str]) -> List[Dict[str, Any]]:
    """Parse multiple documents in parallel."""
    import asyncio
    tasks = [parse_document(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    parsed_results = []
    for result in results:
        if isinstance(result, Exception):
            parsed_results.append({"error": str(result)})
        else:
            parsed_results.append(result)
    
    return parsed_results

