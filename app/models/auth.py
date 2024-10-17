from xmlrpc.client import boolean
from pydantic import BaseModel
from typing import List, Optional


# Pydantic models

# User DB Modal
class User(BaseModel):
    name: str
    email: str
    password: str
    gender: Optional[str] = None
    age: Optional[int] = None
    avatarURL: Optional[str] = None

# Signup Request Payload


class SignupPayload(User):
    provider: Optional[str] = None

# Login Request Payload


class LoginPayload(BaseModel):
    email: str
    password: str

# Signup Response Payload


class SignupRespModal(BaseModel):
    success: boolean
    msg: str

# Login Data model


class LoginResponseModal(User):
    id: str
    password: Optional[str] = None


# ====================== JWT model =======================

class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    userId: str
    email: str | None = None
