from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

class EmployeeActivationRequest(BaseModel):
    temporary_password: str
    user_role: str = "employee"
    department: Optional[str] = None
    send_welcome_email: bool = True
    # Note: No override_email needed - employees login with username (employee_number)
    # Permissions are automatically assigned based on the selected role

class EmployeeActivationResponse(BaseModel):
    user_id: UUID
    employee_id: UUID
    username: str  # Employee ID for login (e.g., SFTAM001)
    email: EmailStr
    role: str
    message: str
    email_sent: bool
    
    class Config:
        from_attributes = True

