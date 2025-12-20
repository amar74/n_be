import re
import uuid
from typing import Any, Optional


def sanitize_filename(filename: str) -> str:
   
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = filename.replace("\\", "").replace("/", "").replace("..", "")
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


def mask_id(user_id: str) -> str:
    
    if not user_id or len(user_id) < 12:
        return "***"
    
    if len(user_id) <= 16:
        return user_id[:4] + "***" + user_id[-4:]
    
    return user_id[:8] + "***" + user_id[-4:]


def sanitize_log_data(data: Any) -> Any:
   
    if isinstance(data, dict):
        sensitive_keys = {
            'password', 'token', 'secret', 'api_key', 'access_key',
            'authorization', 'cookie', 'session', 'credit_card', 'ssn'
        }
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_log_data(value)
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    else:
        return data


def validate_uuid(uuid_string: str) -> bool:
    
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def sanitize_html(html_content: str, allowed_tags: Optional[list] = None) -> str:
   
    if not html_content:
        return ""
    
    # Basic script tag removal
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'on\w+\s*=', '', html_content, flags=re.IGNORECASE)
    
    # For production, use: from bleach import clean
    # return clean(html_content, tags=allowed_tags or [])
    
    return html_content


def validate_file_type(filename: str, allowed_extensions: list) -> bool:
   
    if not filename:
        return False
    
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return file_ext in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return 0 < file_size <= max_size_bytes

