from datetime import datetime

from pydantic import BaseModel, Field

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
    email: str | None = None

class BookingCreate(BaseModel):
    provider_id: int
    start_time: datetime
    end_time: datetime

class BookingUpdate(BaseModel):
    status: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None

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

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None

class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    rating: int
    comment: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewSummarizeRequest(BaseModel):
    provider_id: int

class ReviewSummarizeResponse(BaseModel):
    message: str
    job_id: str
