from pydantic import BaseModel
from typing import Optional

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

    class Config:
        from_attributes = True



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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class FormbricksLoginTokenResponse(BaseModel):
    token: str

    class Config:
        from_attributes = True
