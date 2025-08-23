import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import re
import json
from app.environment import environment

# Configure Gemini
genai.configure(api_key="AIzaSyBvLqYU5OogN2CPiqP-QEKmdic_HDrujPU")
gemini_model = genai.GenerativeModel("gemini-2.0-flash")


def scrape_text_with_bs4(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style", "noscript"]):
            script_or_style.extract()

        text = soup.get_text(separator="\n")
        visible_text = "\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )
        return {"url": url, "text": visible_text}
    except Exception as e:
        return {"url": url, "error": f"Failed to scrape: {str(e)}"}


def extract_info(text):
    prompt = (
        "You are an AI assistant for a payment processing system that needs to extract and structure contact information from business websites for secure database storage. Extract complete and accurate information:\n\n"
        "Required Information:\n"
        "- Business/Company Name or Full Name of Individual\n"
        "- Email Addresses (collect all available emails as an array)\n"
        "- Phone Numbers (collect all available phone numbers as an array)\n"
        "- Complete Business Address (required for payment processing compliance)\n\n"
        "Address Requirements for Payment Processing:\n"
        "- Street Address Line 1 (building number, street name)\n"
        "- Street Address Line 2 (suite, apartment, floor - if applicable)\n"
        "- City/Town\n"
        "- State/Province/Region\n"
        "- Country\n"
        "- Postal/ZIP Code\n"
        f"Website Content:\n{text[:5000]}\n\n"
        "IMPORTANT: Extract ONLY real, verifiable information from the website content. Do not fabricate or guess missing information.\n\n"
        "Return data in this exact JSON format for database insertion:\n"
        """{
            "name": "Complete business/individual name",
            "email": ["primary@company.com", "support@company.com"],
            "phone": ["+1-555-123-4567", "+1-555-987-6543"],
            "address": {
                "line1": "123 Business Street",
                "line2": "Suite 456",
                "city": "Business City",
                "state": "State/Province",
                "country": "Country Name",
                "pincode": "12345",
            }
        }"""
        "\n\nNote: If any information is not available on the website, use null for that field. Ensure all extracted data is accurate and verifiable from the source content."
    )

    try:
        response = gemini_model.generate_content(prompt)
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return {"error": "No JSON found", "raw": response.text}
    except Exception as e:
        return {"error": f"Gemini failed: {e}"}


def process_urls(urls):
    results = []

    for url in urls:
        page = scrape_text_with_bs4(url)
        if "text" in page:
            info = extract_info(page["text"])
            results.append({"url": url, "info": info})
        else:
            results.append({"url": url, "error": page.get("error", "Unknown error")})

    return results


# Example usage
# if _name_ == "_main_":
#     urls = [
#         "https://medium.com",
#         "https://lukesmith.xyz/contact/",
#         "https://jlnst.com/",
#         "https://analox.in/contact-us"
#     ]
#     output = process_urls(urls)
#     print(json.dumps(output, indent=2))
