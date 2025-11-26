import json
from datetime import datetime
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
import google.generativeai as genai
from app.environment import environment
from typing import List, Dict, Union, Any, Optional

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

            return {"url": url, "text": visible_text, "html": response.text}

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
model = genai.GenerativeModel("gemini-pro")

PROJECT_DETAILS_PROMPT = """You are an infrastructure opportunity analyst. Review the provided project page content and return ONLY valid JSON matching this schema:
{{
  "overview": string | null,
  "project_value_text": string | null,
  "project_value_numeric": number | null,
  "expected_rfp_date": string | null,
  "start_date": string | null,
  "completion_date": string | null,
  "scope_summary": string | null,
  "scope_items": [string, ...],
  "location": {{
    "line1": string | null,
    "line2": string | null,
    "city": string | null,
    "state": string | null,
    "country_code": string | null,
    "pincode": string | null
  }},
  "contacts": [
    {{
      "name": string | null,
      "role": string | null,
      "organization": string | null,
      "email": [string, ...],
      "phone": [string, ...]
    }}
  ],
  "documents": [
    {{
      "title": string | null,
      "url": string | null,
      "type": string | null
    }}
  ]
}}

Rules:
- Use null for unknown fields.
- Ensure email/phone arrays contain only clean strings.
- Never include markdown or commentary, return JSON only.

Content:
\"\"\"{content}\"\"\""""


def _truncate_text(text: str, limit: int = 12000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


def _safe_json_loads(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        if "\n" in candidate:
            candidate = candidate.split("\n", 1)[1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return {}


def _normalize_string_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    return []


def extract_documents_from_html(html: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Enhanced document extraction that finds all document links including:
    - PDFs, Word docs, Excel, PowerPoint
    - CAD files (DWG, DGN)
    - Links in document/resource sections
    - Download links
    """
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    documents: List[Dict[str, Any]] = []
    seen_urls: set[str] = set()
    
    # Document file extensions to look for
    doc_extensions = [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".dwg", ".dgn", ".zip", ".rar", ".txt", ".csv", ".xml"
    ]
    
    # Keywords that indicate document links
    doc_keywords = [
        "download", "document", "pdf", "specification", "spec", "drawing",
        "plan", "report", "study", "assessment", "rfp", "tender", "bid",
        "attachment", "resource", "file", "manual", "guide"
    ]
    
    # Find all links
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue
        
        text = link.get_text(" ", strip=True).strip()
        normalized_href = href.lower()
        normalized_text = text.lower() if text else ""
        
        # Check if it's a document by extension
        has_doc_extension = any(ext in normalized_href for ext in doc_extensions)
        
        # Check if it's a document by keyword in URL or text
        has_doc_keyword = any(keyword in normalized_href or keyword in normalized_text for keyword in doc_keywords)
        
        # Also check parent elements for document indicators
        parent_text = ""
        parent = link.parent
        if parent:
            parent_text = parent.get_text(" ", strip=True).lower()
        has_parent_indicator = any(keyword in parent_text for keyword in ["document", "download", "resource", "attachment", "file"])
        
        # Include if it matches any criteria
        if not (has_doc_extension or has_doc_keyword or has_parent_indicator):
            continue
        
        # Convert to absolute URL
        absolute_url = urljoin(base_url, href)
        
        # Skip duplicates
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)
        
        # Determine document type
        doc_type = None
        for ext in doc_extensions:
            if ext in normalized_href:
                doc_type = ext[1:].upper()  # Remove dot and uppercase
                break
        
        # Extract title - prefer link text, fallback to filename
        title = text if text else None
        if not title:
            # Try to get title from filename
            filename = href.split("/")[-1].split("?")[0]
            if filename and "." in filename:
                title = filename
        
        documents.append({
            "title": title or "Document",
            "url": absolute_url,
            "type": doc_type,
            "description": None,  # Will be filled by AI if available
        })
    
    # Also look for document links in specific sections
    doc_sections = soup.find_all(["section", "div"], class_=lambda x: x and any(
        keyword in x.lower() for keyword in ["document", "resource", "download", "attachment", "file"]
    ))
    
    for section in doc_sections:
        for link in section.find_all("a", href=True):
            href = link.get("href")
            if not href:
                continue
            absolute_url = urljoin(base_url, href)
            if absolute_url not in seen_urls:
                text = link.get_text(" ", strip=True).strip()
                if text or any(ext in href.lower() for ext in doc_extensions):
                    seen_urls.add(absolute_url)
                    documents.append({
                        "title": text or "Document",
                        "url": absolute_url,
                        "type": None,
                        "description": None,
                    })
    
    return documents


async def enrich_opportunity_details(
    detail_url: str,
    prefetched_page: Optional[Dict[str, Union[str, Dict[str, str]]]] = None,
) -> Dict[str, Any]:
    detail_page = prefetched_page or await scrape_text_with_bs4(detail_url)
    if "text" not in detail_page:
        return {"detail_error": detail_page.get("error")}

    text = detail_page["text"]
    html = detail_page.get("html") or ""
    documents = extract_documents_from_html(html, detail_url)

    prompt = PROJECT_DETAILS_PROMPT.format(content=_truncate_text(text))
    structured: Dict[str, Any] = {}
    try:
        response = model.generate_content(prompt)
        raw = response.text if response else ""
        structured = _safe_json_loads(raw)
    except Exception:
        structured = {}

    if not structured.get("contacts"):
        fallback_contact = extract_info(text)
        if isinstance(fallback_contact, dict):
            structured["contacts"] = [
                {
                    "name": fallback_contact.get("name"),
                    "role": None,
                    "organization": None,
                    "email": _normalize_string_list(fallback_contact.get("email")),
                    "phone": _normalize_string_list(fallback_contact.get("phone")),
                }
            ]

    location = structured.get("location") or structured.get("location_details")
    if isinstance(location, dict):
        structured["location_details"] = {
            "line1": location.get("line1") or location.get("address"),
            "line2": location.get("line2"),
            "city": location.get("city"),
            "state": location.get("state"),
            "country_code": location.get("country_code") or location.get("country"),
            "pincode": location.get("pincode") or location.get("zip"),
        }

    scope_items = structured.get("scope_items") or structured.get("scopeItems") or []
    structured["scope_items"] = _normalize_string_list(scope_items)
    structured["documents"] = structured.get("documents") or documents
    structured["overview"] = structured.get("overview") or structured.get("summary")
    structured["project_value_text"] = structured.get("project_value_text") or structured.get("project_value")

    numeric_value = structured.get("project_value_numeric")
    if isinstance(numeric_value, str):
        try:
            structured["project_value_numeric"] = float(
                numeric_value.replace(",", "").replace("$", "").strip()
            )
        except ValueError:
            structured["project_value_numeric"] = None

    structured["metadata"] = {
        "detail_source": detail_url,
        "refreshed_at": datetime.utcnow().isoformat(),
    }

    return structured

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

def extract_opportunities(text: str, html: str, base_url: str, max_items: int = 20) -> List[Dict[str, Any]]:
    from bs4 import BeautifulSoup

    parsed_opportunities: List[Dict[str, Any]] = []

    if html:
        soup = BeautifulSoup(html, "html.parser")

        project_items = soup.select(".page-projects-list__item")
        seen_titles: set[str] = set()

        for item in project_items:
            title_element = item.select_one(".page-projects-list__item-title a")
            if not title_element:
                continue

            title = title_element.get_text(strip=True)
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            detail_href = title_element.get("href") or ""
            detail_url = urljoin(base_url, detail_href.strip())

            summary_element = item.select_one(".page-projects-list__item-summary")
            summary = summary_element.get_text(" ", strip=True) if summary_element else None

            status_element = item.select_one(".page-projects-list__item-status-status")
            status = status_element.get_text(strip=True) if status_element else None

            if summary and status and summary.endswith(status):
                summary = summary[: -len(status)].rstrip(" -:;,.")

            parsed_opportunities.append(
                {
                    "title": title,
                    "status": status,
                    "description": summary,
                    "detail_url": detail_url,
                    "client": None,
                    "location": None,
                    "budget_text": None,
                    "deadline": None,
                    "tags": [],
                }
            )

            if len(parsed_opportunities) >= max_items:
                break

    if parsed_opportunities:
        return parsed_opportunities

    prompt = f"""You are an analyst extracting infrastructure or procurement opportunities from structured or semi-structured website content.
Return ONLY JSON that conforms strictly to the following schema:
{{
  "opportunities": [
    {{
      "title": string | null,
      "status": string | null,
      "description": string | null,
      "client": string | null,
      "location": string | null,
      "budget_text": string | null,
      "deadline": string | null,
      "detail_url": string | null,
      "tags": [string, ...]
    }}
  ]
}}

Guidelines:
- Include up to {max_items} distinct project or tender records described in the content.
- Use null when a field is missing.
- If a relative link to a detailed page exists, convert it into an absolute URL using the base \"{base_url}\".
- Focus on sections that clearly resemble projects, tenders, or program listings.
- Ignore navigation, unrelated content, or repeated headers.

Content to analyse:
\"\"\"{text[:15000]}\"\"\""""

    try:
        response = model.generate_content(prompt)
        raw = response.text if response else ""
        data = json.loads(raw)
        opportunities = data.get("opportunities", [])
        normalized: List[Dict[str, Any]] = []
        for item in opportunities:
            if not isinstance(item, dict):
                continue
            detail_url = item.get("detail_url") or item.get("url")
            if detail_url:
                detail_url = urljoin(base_url, detail_url.strip())
            tags = item.get("tags") or []
            if isinstance(tags, str):
                tags = [tags]
            if not isinstance(tags, list):
                tags = []
            normalized.append(
                {
                    "title": (item.get("title") or item.get("name") or "").strip() or None,
                    "status": (item.get("status") or item.get("phase") or "").strip() or None,
                    "description": (item.get("description") or item.get("summary") or "").strip() or None,
                    "client": (item.get("client") or item.get("owner") or "").strip() or None,
                    "location": (item.get("location") or item.get("region") or "").strip() or None,
                    "budget_text": (item.get("budget_text") or item.get("budget") or item.get("value") or "").strip() or None,
                    "deadline": (item.get("deadline") or item.get("due_date") or item.get("timeline") or "").strip() or None,
                    "detail_url": detail_url,
                    "tags": [str(tag).strip() for tag in tags if str(tag).strip()],
                }
            )
        return normalized[:max_items]
    except (json.JSONDecodeError, AttributeError):
        return []
    except Exception:
        return []


async def process_urls(urls: List[str]) -> List[Dict[str, Any]]:
    results = []

    for url in urls:
        page = await scrape_text_with_bs4(url)

        if "text" in page:
            info = extract_info(page["text"])
            base_opportunities = extract_opportunities(
                page["text"],
                page.get("html") or "",
                url,
            )
            enriched_opportunities: List[Dict[str, Any]] = []
            for opportunity in base_opportunities:
                detail_url = opportunity.get("detail_url")
                detail_payload: Dict[str, Any] = {}
                if detail_url:
                    detail_payload = await enrich_opportunity_details(detail_url)
                elif len(base_opportunities) == 1:
                    detail_payload = await enrich_opportunity_details(url, prefetched_page=page)

                merged = {**opportunity}
                merged.update(
                    {k: v for k, v in detail_payload.items() if v is not None}
                )
                enriched_opportunities.append(merged)

            results.append({"url": url, "info": info, "opportunities": enriched_opportunities})
        else:
            results.append({"url": url, "error": page.get("error", "Unknown error")})

    return results
