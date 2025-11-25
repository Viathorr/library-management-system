from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    reader = "reader"
    librarian = "librarian"
    
    
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str = Field(..., min_length=8)
    email: Optional[EmailStr] = None
    role: UserRole
    
    
class User(UserBase):
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True
    