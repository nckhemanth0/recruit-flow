from datetime import datetime

from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    role: str | None = None
    phone: str | None = None
    location: str | None = None
    bio: str | None = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    location: str | None = None
    bio: str | None = None
