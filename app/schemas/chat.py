from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ChatMessageBase(BaseModel):
    role: str = Field(..., pattern="^(user|bot)$")
    content: str = Field(..., min_length=1)
    thinking_mode: Optional[str] = Field(None, max_length=20)
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: UUID
    session_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_id: Optional[int] = None
    selected_topics: Optional[List[str]] = Field(default_factory=list)
    selected_prompts: Optional[List[str]] = Field(default_factory=list)
    module: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionResponse(ChatSessionBase):
    id: UUID
    org_id: Optional[UUID]
    created_by: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    messages: List[ChatMessageResponse] = []


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int


class AIChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1)
    module: Optional[str] = None
    thinking_mode: Optional[str] = Field("normal", max_length=20)
    conversation_history: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None
    use_case: Optional[str] = Field(None, description="Use case: content_enrichment, content_development, suggestions, auto_enhancement, ideas")


class AIChatResponse(BaseModel):
    response: str
    thinking_mode: str
    use_case: Optional[str] = None

