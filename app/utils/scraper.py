import httpx
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from app.environment import environment
from typing import List, Dict, Union, Any


# Async function to scrape and clean visible text from a webpage
async def scrape_text_with_bs4(url: str) -> Dict[str, Union[str, Dict[str, str]]]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()

            text = soup.get_text(separator="\n")
            visible_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

            print(f"[DEBUG] Scraped content from {url}:\n{visible_text[:1000]}...\n")  # Debug print

            return {"url": url, "text": visible_text}

    except Exception as e:
        return {"url": url, "error": f"Failed to scrape: {str(e)}"}


# Gemini function tool schema declaration
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

# Configure Gemini client and tool
client = genai.Client(api_key=environment.GEMINI_API_KEY)
tools = types.Tool(function_declarations=[extract_contact_info_function])
config = types.GenerateContentConfig(tools=[tools])


# Function to send text to Gemini and extract contact info using tools
def extract_info(text: str) -> Dict[str, Any]:
    try:
        print("[DEBUG] Sending text to Gemini...")

        contents = [
            types.Content(
                parts=[
                    {"text": "You are a contact information extraction assistant."},
                    {"text": "Extract business or individual contact info using the extract_contact_info function tool."},
                    {"text": f"Here is the website content:\n\n{text[:5000]}"}
                ]
            )
        ]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        print(f"[DEBUG] Gemini candidate parts: {candidate.content.parts}")

        if candidate.content.parts and hasattr(candidate.content.parts[0], "function_call"):
            function_call = candidate.content.parts[0].function_call
            print(f"[DEBUG] Gemini function call output: {function_call.args}")

            return {
                "name": function_call.args.get("name"),
                "email": function_call.args.get("email"),
                "phone": function_call.args.get("phone"),
                "address": function_call.args.get("address"),
            }

        else:
            raw_text = candidate.content.parts[0].text if candidate.content.parts else "No content"
            print(f"[DEBUG] Gemini returned non-function text:\n{raw_text[:500]}")

            return {
                "error": "No function call returned by Gemini.",
                "raw_response": raw_text
            }

    except Exception as e:
        print(f"[ERROR] Gemini call failed: {e}")
        return {"error": f"Gemini call failed: {str(e)}"}


# Process a list of URLs to scrape + extract info
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


# Example usage:
# async def run_test():
#     urls = [
#         "https://lukesmith.xyz/contact/",
#         "https://jlnst.com/",
#         "https://analox.in/contact-us"
#     ]
#     results = await process_urls(urls)
#     import json
#     print(json.dumps(results, indent=2))

# # To run from script:
# import asyncio
# asyncio.run(run_test())
