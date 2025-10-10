import os
import sys
import json
from typing import Any, Dict

import requests


API_BASE = "https://console.neon.tech/api/v2"


def read_env(name: str, required: bool = True, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if required and not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value or ""


def api_headers(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def request_json(method: str, url: str, headers: Dict[str, str], payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    response = requests.request(method, url, headers=headers, json=payload, timeout=60)
    if response.status_code >= 400:
        try:
            body = response.json()
        except Exception:
            body = {"text": response.text}
        raise RuntimeError(f"Neon API error {response.status_code} at {url}: {json.dumps(body)}")
    try:
        return response.json()
    except Exception as exc:
        raise RuntimeError(f"Failed to parse JSON from Neon API at {url}: {response.text}") from exc


def list_branches(project_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    url = f"{API_BASE}/projects/{project_id}/branches"
    return request_json("GET", url, headers)


def get_branch_id_by_name(project_id: str, branch_name: str, headers: Dict[str, str]) -> str:
    body = list_branches(project_id, headers)
    branches = body.get("branches") or body.get("data", {}).get("branches") or []
    for b in branches:
        if b.get("name") == branch_name:
            return b.get("id") or b.get("branch_id")
    raise RuntimeError(f"Parent branch named '{branch_name}' was not found")


def create_branch(project_id: str, headers: Dict[str, str], parent_branch_id: str | None = None) -> Dict[str, Any]:
    url = f"{API_BASE}/projects/{project_id}/branches"
    payload: Dict[str, Any] | None = {
        "endpoints": [
            {
                "type": "read_write",
            }
        ]
    }
    
    if parent_branch_id:
        payload["branch"] = {"parent_id": parent_branch_id}
    return request_json("POST", url, headers, payload)


def get_connection_uri(
    project_id: str,
    branch_id: str,
    database_name: str,
    role_name: str,
    headers: Dict[str, str],
    pooled: bool = False,
) -> str:
    url = f"{API_BASE}/projects/{project_id}/connection_uri"
    params = {
        "branch_id": branch_id,
        "database_name": database_name,
        "role_name": role_name,
        "pooled": pooled,
    }
    response = requests.get(url, headers=headers, params=params, timeout=60)
    if response.status_code >= 400:
        try:
            body = response.json()
        except Exception:
            body = {"text": response.text}
        raise RuntimeError(f"Neon API error {response.status_code} at {url}: {json.dumps(body)}")

    try:
        result = response.json()
        return result.get("uri", "")
    except Exception as exc:
        raise RuntimeError(f"Failed to parse JSON from Neon API at {url}: {response.text}") from exc


def main() -> None:
    api_key = read_env("NEON_API_KEY")
    project_id = read_env("NEON_PROJECT_ID")
    parent_branch_name = read_env("NEON_PARENT_BRANCH_NAME", required=False, default=None)
    database_name = read_env("NEON_DATABASE_NAME", required=False, default="neondb")
    role_name = read_env("NEON_ROLE_NAME", required=False, default="neondb_owner")

    headers = api_headers(api_key)

    parent_id: str | None = None
    if parent_branch_name:
        parent_id = get_branch_id_by_name(project_id, parent_branch_name, headers)

    branch_resp = create_branch(project_id, headers, parent_id)
    # Extract branch ID from create response
    branch = branch_resp.get("branch") or branch_resp.get("data", {}).get("branch") or {}
    branch_id = branch.get("id") or branch.get("branch_id")
    if not branch_id:
        raise RuntimeError("Failed to get branch ID from create branch response")

    # Fetch connection URI and print
    connection_uri = get_connection_uri(project_id, branch_id, database_name, role_name, headers)
    print(connection_uri)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)