import time
from typing import List, Optional
import jwt
from pydantic import BaseModel
from sqlalchemy import UUID
from app.environment import environment
from app.models.organization import Organization
import httpx

from app.models.user import User
from app.schemas.auth import AuthUserResponse
from app.schemas.formbricks import (
    CreateFormBricksProjectResponse,
    CreateOrganizationFormBricksResponse,
    CreateUserInFormBricksResponse,
    FormbricksLoginTokenResponse,
    SurveyListResponse,
    SurveyCreateRequest,
    Survey,
)
from app.models.formbricks_projects import FormbricksProject
from app.utils.error import MegapolisHTTPException
from loguru import logger


async def create_formbricks_organization(
    organization: Organization,
) -> CreateOrganizationFormBricksResponse:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{environment.FORMBRICKS_SERVER_URL}/api/v2/admin/organizations",
            json={"name": organization.name},
            headers={
                "Content-Type": "application/json",
                "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
            },
        )
        if response.status_code != 201:
            logger.error(f"Failed to create formbricks organization: {response.status_code}, {response.text[0:200]}")
            raise Exception(
                f"Failed to create formbricks organization: {response.status_code}, {response.text[0:200]}"
            )
        return CreateOrganizationFormBricksResponse.model_validate(
            response.json().get("data")
        )


async def signup_user_in_formbricks(
    organization: Organization, user: User
) -> CreateUserInFormBricksResponse:
    async with httpx.AsyncClient() as client:
        payload = {
            "name": user.email.split("@")[0],
            "email": user.email,
            "role": "owner",
            "isActive": True,
            "teams": [],
        }
        response = await client.post(
            f"{environment.FORMBRICKS_SERVER_URL}/api/v2/admin/organizations/{organization.formbricks_organization_id}/users",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
            },
        )
        if response.status_code != 201:
            logger.error(f"Failed to signup user in formbricks: {response.text}")
            raise Exception(f"Failed to signup user in formbricks: {response.text}")
        return CreateUserInFormBricksResponse.model_validate(
            response.json().get("data")
        )


async def create_formbricks_project(
    organization: Organization
) -> CreateFormBricksProjectResponse:
    async with httpx.AsyncClient() as client:
        payload = {
            "name": organization.name,
            "styling": {
                "allowStyleOverwrite": True,
                "brandColor": {"light": "#FFA500"}  # optional
            },
            "config": {"channel": "website", "industry": "saas"},  # optional
            # "inAppSurveyBranding": True,   # optional
            "linkSurveyBranding": True,    # optional
            # "placement": "bottomRight",    # optional
            # "clickOutsideClose": True,     # optional
            # "darkOverlay": False,          # optional
            "logo": {"url": "https://cdn.example.com/logo.png"},  # optional
            "teamIds": []  # optional: IDs of teams to link to the project
        }
        response = await client.post(
            f"{environment.FORMBRICKS_SERVER_URL}/api/v2/admin/organizations/{organization.formbricks_organization_id}/projects",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
            },
        )
        if response.status_code != 201:
            logger.error(f"Failed to create formbricks project: {response.text}")
            raise Exception(f"Failed to create formbricks project: {response.text}")
        
        return CreateFormBricksProjectResponse.model_validate(
            response.json().get("data")
        )



async def get_formbricks_login_token(
    user: User
) -> FormbricksLoginTokenResponse:
    # Logic to create a new JWT token
    payload = {
        "email": user.email,
        "name": user.email.split("@")[0],
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
    }
    token = jwt.encode(payload, environment.FORMBRICKS_JWT_SECRET, algorithm="HS256")
    
    return FormbricksLoginTokenResponse(token=token)







async def get_all_surveys(org_id: UUID, current_user: User) -> SurveyListResponse:
    """Get all surveys for an organization.

    Fetches surveys from Formbricks admin API using the organization's
    environment id (dev by default). Returns a normalized SurveyListResponse.
    """

    # Authorization: user must belong to the organization
    if not current_user.org_id or str(current_user.org_id) != str(org_id):
        raise MegapolisHTTPException(status_code=403, message="Forbidden")

    # Resolve Formbricks environment id for the organization
    fb_project = await FormbricksProject.get_by_organization_id(org_id)
    if not fb_project or not fb_project.prod_env_id:
        raise MegapolisHTTPException(status_code=404, message="Formbricks environment not configured")

    environment_id = fb_project.prod_env_id

    url = f"{environment.FORMBRICKS_SERVER_URL}/api/admin/environments/{environment_id}/surveys"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to fetch surveys: {response.status_code} {response.text[0:200]}")
        raise MegapolisHTTPException(status_code=502, message="Upstream Formbricks error")

    payload = response.json()
    raw_list = payload.get("data", [])

    # Map minimal fields we currently model; keep extensible
    surveys = []
    for item in raw_list:
        try:
            surveys.append({
                "id": item.get("id"),
                "environment_id": environment_id,
                "createdAt": item.get("createdAt"),
                "updatedAt": item.get("updatedAt"),
                "name": item.get("name"),
            })
        except Exception:
            # Skip malformed entries instead of failing the whole list
            continue

    return SurveyListResponse.model_validate({"surveys": surveys})



async def create_survey(current_user: User, payload: SurveyCreateRequest) -> Survey:
    """Create a new Formbricks survey for the current user's organization.

    Posts to the Formbricks admin API using the organization's production
    environment id and returns the upstream `data` payload.
    """

    if not current_user.org_id:
        raise MegapolisHTTPException(status_code=400, message="User has no organization")

    fb_project = await FormbricksProject.get_by_organization_id(current_user.org_id)
    if not fb_project or not fb_project.prod_env_id:
        raise MegapolisHTTPException(status_code=404, message="Formbricks environment not configured")

    environment_id = fb_project.prod_env_id

    url = f"{environment.FORMBRICKS_SERVER_URL}/api/admin/environments/{environment_id}/surveys"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
    }

    # Only forward required fields; rely on upstream defaults for the rest
    body = {
        "name": payload.name,
        "publish": True,
        "questions": [
            {
                "id": "q1",
                "type": "openText",
                "headline": { "default": "Your name?" },
                "required": False
            }
        ],
        "type": "link"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code not in (200, 201):
        logger.error(f"Failed to create survey: {response.status_code} {response.text[0:200]}")
        raise MegapolisHTTPException(status_code=502, message="Upstream Formbricks error")

    data = response.json().get("data", {})
    return Survey.model_validate({
        "id": data.get("id"),
        "environment_id": environment_id,
        "createdAt": data.get("createdAt"),
        "updatedAt": data.get("updatedAt"),
        "name": data.get("name"),
    })


