import time
from typing import Optional
import jwt
from pydantic import BaseModel
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
)
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
            logger.error(f"Failed to create formbricks organization: {response.text}")
            raise Exception(
                f"Failed to create formbricks organization: {response.text}"
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
