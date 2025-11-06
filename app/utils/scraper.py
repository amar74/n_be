import httpx
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.generativeai import types
from app.environment import environment
from typing import List, Dict, Union, Any

async def scrape_text_with_bs4(url: str) -> Dict[str, Union[str, Dict[str, str]]]:
    try:
        # Increase timeout to 30 seconds for slow websites
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()

            text = soup.get_text(separator="\n")
            visible_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

            return {"url": url, "text": visible_text}

    except httpx.TimeoutException as e:
        return {"url": url, "error": f"Website timeout after 30 seconds: {type(e).__name__}"}
    except httpx.HTTPStatusError as e:
        return {"url": url, "error": f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"}
    except httpx.RequestError as e:
        return {"url": url, "error": f"Network error: {type(e).__name__} - {str(e) or 'Connection failed'}"}
    except Exception as e:
        error_msg = str(e) if str(e) else f"{type(e).__name__}: Unknown error"
        return {"url": url, "error": f"Failed to scrape: {error_msg}"}

extract_contact_info_function = {
    "name": "extract_contact_info",
    "description": "Extracts business or individual contact details from website content.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Complete business or individual name"},
            "email": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of email addresses found"
            },
            "phone": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of phone numbers found"
            },
            "address": {
                "type": "object",
                "properties": {
                    "line1": {"type": "string"},
                    "line2": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "country": {"type": "string"},
                    "pincode": {"type": "string"},
                },
                "required": ["line1", "city", "state", "country", "pincode"]
            }
        },
        "required": ["name", "email", "phone", "address"]
    }
}

genai.configure(api_key=environment.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_info(text: str) -> Dict[str, Any]:
    try:
        prompt = f"""You are a contact information extraction assistant. Extract business or individual contact information from this website content and return it as a JSON object with the following structure:
        {{
            "name": "Business or person name",
            "email": "Email address if found",
            "phone": "Phone number if found", 
            "address": "Full address if found"
        }}
        
        If any field is missing, use "Unknown" for that field. Extract from this content:
        
        {text[:5000]}"""

        response = model.generate_content(prompt)
        
        try:
            import json
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            return {
                "name": "Unknown",
                "email": "Unknown", 
                "phone": "Unknown",
                "address": "Unknown"
            }
        
    except Exception as e:
        return {"error": f"Gemini call failed: {str(e)}"}

async def process_urls(urls: List[str]) -> List[Dict[str, Any]]:
    results = []

    for url in urls:
        page = await scrape_text_with_bs4(url)

        if "text" in page:
            info = extract_info(page["text"])
            results.append({"url": url, "info": info})
        else:
            results.append({"url": url, "error": page.get("error", "Unknown error")})

    return results
