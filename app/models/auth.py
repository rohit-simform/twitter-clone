from xmlrpc.client import boolean
from pydantic import BaseModel
from typing import List, Optional


# Pydantic models


class User(BaseModel):
    name: str
    email: str
    password: str
    gender: Optional[str] = None
    age: Optional[int] = None
    avatarURL: Optional[str] = None


class SignupPayload(User):
    provider: Optional[str] = None


class LoginPayload(BaseModel):
    email: str
    password: str


class SignupRespModal(BaseModel):
    success: boolean
    msg: str


class LoginResponseModal(User):
    id: str
    password: Optional[str] = None
