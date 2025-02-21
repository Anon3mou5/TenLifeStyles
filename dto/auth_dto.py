from typing import Optional

from pydantic import BaseModel, validator


class AuthenticationCreationRequestBody(BaseModel):
    fullname: str = None
    username: str
    email: Optional[str] = None
    password: str

    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Username must not be empty')
        return v

    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v