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
    SurveyLinkCreateRequest,
    SurveyLinkResponse,
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
            logger.error(f"failed to signup user in formbricks: {response.text}")
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
            "linkSurveyBranding": True,    # optional
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
            raise Exception(f"failed to create formbricks project: {response.text}")
        
        return CreateFormBricksProjectResponse.model_validate(
            response.json().get("data")
        )

async def get_formbricks_login_token(
    user: User
) -> FormbricksLoginTokenResponse:
    payload = {
        "email": user.email,
        "name": user.email.split("@")[0],
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
    }
    token = jwt.encode(payload, environment.FORMBRICKS_JWT_SECRET, algorithm="HS256")
    
    return FormbricksLoginTokenResponse(token=token)

async def get_all_surveys(org_id: UUID, current_user: User) -> SurveyListResponse:

    if not current_user.org_id or str(current_user.org_id) != str(org_id):
        raise MegapolisHTTPException(status_code=403, message="Forbidden")

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
            continue

    return SurveyListResponse.model_validate({"surveys": surveys})

async def create_survey(current_user: User, payload: SurveyCreateRequest) -> Survey:

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

async def create_survey_link(
    current_user: User, survey_id: str, payload: SurveyLinkCreateRequest
) -> SurveyLinkResponse:

    if not current_user.org_id:
        raise MegapolisHTTPException(status_code=400, message="User has no organization")

    fb_project = await FormbricksProject.get_by_organization_id(current_user.org_id)
    if not fb_project or not fb_project.prod_env_id:
        raise MegapolisHTTPException(status_code=404, message="Formbricks environment not configured")

    try:
        env_id = fb_project.prod_env_id
        list_url = f"{environment.FORMBRICKS_SERVER_URL}/api/admin/environments/{env_id}/surveys"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
        }
        async with httpx.AsyncClient() as client:
            list_resp = await client.get(list_url, headers=headers)
        if list_resp.status_code == 200:
            surveys = (list_resp.json() or {}).get("data", [])
            survey_ids = {item.get("id") for item in surveys if isinstance(item, dict)}
            if survey_id not in survey_ids:
                raise MegapolisHTTPException(status_code=404, message="Survey not found for organization")
        else:
            logger.warning(
                f"Unable to verify survey existence: {list_resp.status_code} {list_resp.text[0:200]}"
            )
    except MegapolisHTTPException:
        raise
    except Exception:
        logger.warning("Survey verification failed; proceeding to link creation")

    link_url = f"{environment.FORMBRICKS_SERVER_URL}/api/admin/surveys/{survey_id}/link"
    link_headers = {
        "Content-Type": "application/json",
        "x-admin-secret": environment.FORMBRICKS_ADMIN_SECRET,
    }
    body = {"email": payload.email}

    async with httpx.AsyncClient() as client:
        response = await client.post(link_url, headers=link_headers, json=body)

    if response.status_code != 200:
        logger.error(f"failed to create survey link: {response.status_code} {response.text[0:200]}")
        raise MegapolisHTTPException(status_code=502, message="Upstream Formbricks error")

    data = (response.json() or {}).get("data", {})
    url = data.get("url")

    if not url:
        logger.error("Malformed response from Formbricks while creating survey link")
        raise MegapolisHTTPException(status_code=502, message="Malformed response from Formbricks")

    return SurveyLinkResponse(url=url)

