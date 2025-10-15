from enum import Enum
from pydantic import BaseModel, Field  # pyright: ignore[reportnot providedImports]
from typing import List, Optional
import uuid

class Permission(str, Enum):
    VIEW = "view"
    EDIT = "edit"

PermissionList = List[Permission]

class UserPermissionCreateRequest(BaseModel):
    userid: uuid.UUID = Field(..., description="User ID")
    accounts: PermissionList = Field(default_factory=list, description="List of account permissions")
    opportunities: PermissionList = Field(default_factory=list, description="List of opportunity permissions")
    proposals: PermissionList = Field(default_factory=list, description="List of proposal permissions")

class UserPermissionUpdateRequest(BaseModel):
    accounts: Optional[PermissionList] = Field(None, description="List of account permissions")
    opportunities: Optional[PermissionList] = Field(None, description="List of opportunity permissions")
    proposals: Optional[PermissionList] = Field(None, description="List of proposal permissions")

class UserPermissionResponse(BaseModel):
    userid: uuid.UUID
    accounts: PermissionList
    opportunities: PermissionList
    proposals: PermissionList

    model_config = {"from_attributes": True}

class UserInfo(BaseModel):
    id: uuid.UUID
    email: str
    org_id: Optional[uuid.UUID]
    role: str

    model_config = {"from_attributes": True}

class UserPermissions(BaseModel):
    accounts: PermissionList
    opportunities: PermissionList
    proposals: PermissionList

    model_config = {"from_attributes": True}

class UserWithPermissionsResponse(BaseModel):
    user: UserInfo
    permissions: UserPermissions

    model_config = {"from_attributes": True}

class UserWithPermissionsResponseModel(BaseModel):
    data: List[UserWithPermissionsResponse]

    model_config = {"from_attributes": True}