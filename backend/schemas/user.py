from pydantic import BaseModel

from backend.core.constants import ROLE_NORMAL


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = ROLE_NORMAL


class UpdateUserRequest(BaseModel):
    password: str | None = None
    role: str | None = None
    status: int | None = None


class RegisterRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
