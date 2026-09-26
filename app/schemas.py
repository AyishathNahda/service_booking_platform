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

class BookingCreate(BaseModel):
    provider_id: int
    start_time: datetime
    end_time: datetime

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class BookingResponse(BaseModel):
    id: int
    provider_id: int
    customer_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
