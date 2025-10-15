from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from app.schemas.address import AddressCreateResquest, AddressCreateResponse
from app.schemas.contact import ContactCreateRequest, CreateContactResponse

class OrgCreateRequest(BaseModel):

    name: str
    address: Optional[AddressCreateResquest] = None
    website: Optional[str] = None
    contact: Optional[ContactCreateRequest] = None

    model_config = {
        "from_attributes": True}

class OrgCreateResponse(BaseModel):

    name: str
    id: UUID

    model_config = {
        "from_attributes": True}

class OrgCreatedResponse(BaseModel):

    message: str
    org: OrgCreateResponse

    model_config = {
        "from_attributes": True}

class OrgUpdateRequest(BaseModel):

    name: str
    address: Optional[AddressCreateResquest] = None
    website: Optional[str] = None
    contact: Optional[ContactCreateRequest] = None

    model_config = {
        "from_attributes": True}

class OrgUpdateResponse(BaseModel):

    message: str
    org: OrgCreateResponse

    model_config = {
        "from_attributes": True}

class OrgResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    address: Optional[AddressCreateResponse] = None
    website: Optional[str] = None
    contact: Optional[CreateContactResponse] = None
    created_at: datetime
    profile_completion: int = 0  # Profile completion percentage (0-100)

    model_config = {
        "from_attributes": True}

class AddUserInOrgRequest(BaseModel):

    org_id: UUID
    role: str
    email: str

    model_config = {
        "from_attributes": True}

class AddUserInOrgResponse(BaseModel):

    id: UUID
    message: str

    model_config = {
        "from_attributes": True}

class OrgAllUserResponse(BaseModel):
    id: UUID
    org_id: UUID
    role: Optional[str]
    email: str

    model_config = {
        "from_attributes": True}

class OrgMemberResponse(BaseModel):

    email: str
    role: str
    status: str

    model_config = {
        "from_attributes": True}

class OrgMembersListResponse(BaseModel):

    members: list[OrgMemberResponse]
    total_count: int

    model_config = {
        "from_attributes": True}

class OrgMembersDataResponse(BaseModel):

    users: List[OrgAllUserResponse]
    invites: List[Any]  # Use Any to avoid circular import

    model_config = {
        "from_attributes": True}
