from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AIAgenticTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    assigned_modules: Optional[List[str]] = Field(default_factory=list)
    system_prompt: str = Field(..., min_length=10)
    welcome_message: Optional[str] = None
    quick_actions: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_default: bool = False
    display_order: int = 0


class AIAgenticTemplateCreate(AIAgenticTemplateBase):
    pass


class AIAgenticTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    assigned_modules: Optional[List[str]] = None
    system_prompt: Optional[str] = Field(None, min_length=10)
    welcome_message: Optional[str] = None
    quick_actions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    display_order: Optional[int] = None


class AIAgenticTemplateResponse(AIAgenticTemplateBase):
    id: int
    org_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIAgenticTemplateListResponse(BaseModel):
    templates: List[AIAgenticTemplateResponse]
    total: int

