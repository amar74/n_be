from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class UserPermissionCreateRequest(BaseModel):
    userid: uuid.UUID = Field(..., description="User ID")
    accounts: List[str] = Field(default_factory=list, description="List of account permissions")
    opportunities: List[str] = Field(default_factory=list, description="List of opportunity permissions")
    proposals: List[str] = Field(default_factory=list, description="List of proposal permissions")


class UserPermissionUpdateRequest(BaseModel):
    accounts: Optional[List[str]] = Field(None, description="List of account permissions")
    opportunities: Optional[List[str]] = Field(None, description="List of opportunity permissions")
    proposals: Optional[List[str]] = Field(None, description="List of proposal permissions")


class UserPermissionResponse(BaseModel):
    userid: uuid.UUID
    accounts: List[str]
    opportunities: List[str]
    proposals: List[str]

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: uuid.UUID
    email: str
    org_id: Optional[uuid.UUID]
    role: str

    class Config:
        from_attributes = True


class UserPermissions(BaseModel):
    accounts: List[str]
    opportunities: List[str]
    proposals: List[str]

    class Config:
        from_attributes = True


class UserWithPermissionsResponse(BaseModel):
    user: UserInfo
    permissions: UserPermissions

    class Config:
        from_attributes = True