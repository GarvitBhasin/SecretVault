from pydantic import BaseModel, EmailStr


class InitRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm: str


class AddUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm: str
    role: int


class ResetPasswordRequest(BaseModel):
    password: str
    confirm: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class DeleteSelfRequest(BaseModel):
    password: str


class NameRequest(BaseModel):
    name: str


class EditUserRequest(BaseModel):
    role: int


class SecretInfoRequest(BaseModel):
    name: str
    value: str
    description: str
