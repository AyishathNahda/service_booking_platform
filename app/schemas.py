from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models import RoleEnum

class UserCreate(BaseModel):
    name: str
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(..., min_length=6)
    role: RoleEnum

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
