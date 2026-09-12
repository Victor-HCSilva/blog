from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=12)
    password: str = Field(min_length=4, max_length=15)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=12)
    password: str | None = Field(default=None, min_length=4, max_length=15)


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(BaseModel):
    hashed_password: str
