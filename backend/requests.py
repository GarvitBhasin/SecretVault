from pydantic import BaseModel

class InitRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm: str

class AddUserRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm: str
    role: int

class ResetPasswordRequest(BaseModel):
    password: str
    confirm: str

class LoginRequest(BaseModel):
    email: str
    password: str

class DeleteSelfRequest(BaseModel):
    password: str

class CreateProjectRequest(BaseModel):
    name: str

class ResourceIDRequest(BaseModel):
    id: int

class EditProjectRequest(BaseModel):
    id: int
    name: str

class EditUserRequest(BaseModel):
    id: int
    role: int

class SecretInfoRequest(BaseModel):
    id: int
    name: str
    value: str
    description: str | None = None