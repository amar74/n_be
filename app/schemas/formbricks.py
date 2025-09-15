from pydantic import BaseModel
from typing import List, Optional

class BillingLimits(BaseModel):
    monthly: dict

class Billing(BaseModel):
    plan: str
    limits: BillingLimits
    period: str
    periodStart: str
    stripeCustomerId: Optional[str] = None

class CreateOrganizationFormBricksResponse(BaseModel):
    id: str
    createdAt: str
    updatedAt: str
    name: str
    billing: Billing
    isAIEnabled: bool
    whitelabel: dict

    model_config = {
        "from_attributes": True}



class CreateUserInFormBricksResponse(BaseModel):
    id: str
    createdAt: str
    updatedAt: str
    email: str
    name: str
    lastLoginAt: Optional[str] = None
    isActive: bool
    role: str
    teams: list

    model_config = {
        "from_attributes": True}


class Environment(BaseModel):
    id: str
    createdAt: str
    updatedAt: str
    type: str
    projectId: str
    appSetupCompleted: bool

class BrandColor(BaseModel):
    light: str

class Styling(BaseModel):
    brandColor: BrandColor
    allowStyleOverwrite: bool

class Config(BaseModel):
    channel: str
    industry: str

class Logo(BaseModel):
    url: str

class CreateFormBricksProjectResponse(BaseModel):
    id: str
    createdAt: str
    updatedAt: str
    name: str
    organizationId: str
    styling: Styling
    recontactDays: int
    inAppSurveyBranding: bool
    linkSurveyBranding: bool
    config: Config
    placement: str
    clickOutsideClose: bool
    darkOverlay: bool
    environments: list[Environment]
    languages: list
    logo: Logo

    model_config = {
        "from_attributes": True}


class FormbricksLoginTokenResponse(BaseModel):
    token: str

    model_config = {
        "from_attributes": True}



class Survey(BaseModel):
    id: str
    environment_id: str
    createdAt: str
    updatedAt: str
    name: str

class SurveyListResponse(BaseModel):
    """Client-friendly list shape used by our API.

    - ListResponse: flattened array under a named key (e.g., surveys) that our
      clients consume directly. It abstracts away upstream payload wrappers.
    - ServerResponse (below): mirrors the upstream Formbricks payload, which
      wraps results under a top-level `data` field. We keep both to avoid
      leaking upstream shapes into our public API.
    """

    surveys: List[Survey]

    model_config = {
        "from_attributes": True}


class ServerResponse(BaseModel):
    """Upstream Formbricks list response wrapper.

    - ServerResponse: raw shape from Formbricks with top-level `data` array.
    - ListResponse (see SurveyListResponse): normalized shape we return.
    """

    data: List[dict]

    model_config = {
        "from_attributes": True}


class SurveyCreateRequest(BaseModel):
    """Payload to create a new Formbricks survey.

    Only requires name; server applies defaults for other fields.
    """

    name: str

    model_config = {
        "from_attributes": True}