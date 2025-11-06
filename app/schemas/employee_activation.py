from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

class EmployeeActivationRequest(BaseModel):
    temporary_password: str
    user_role: str = "employee"
    permissions: List[str] = []
    send_welcome_email: bool = True

class EmployeeActivationResponse(BaseModel):
    user_id: UUID
    employee_id: UUID
    email: EmailStr
    role: str
    message: str
    email_sent: bool
    
    class Config:
        from_attributes = True

