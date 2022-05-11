from typing import Optional
from pydantic import BaseModel, UUID4


# Shared properties
class UserBase(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool = True
    is_verified: Optional[bool] = False
    is_superuser: Optional[bool] = False
    created: Optional[str]
    last_login: Optional[str]


# Properties to receive via API on creation
class UserCreated(BaseModel):
    id: UUID4
    email: str

class UserCreating(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    password: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserInDBBase(UserBase):
    id: Optional[UUID4] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    pass


class HTTPErrorBase(BaseModel):
    detail: Optional[str] = None


class HTTPError(HTTPErrorBase):
    pass


class HTTPNoContentBase(BaseModel):
    detail: Optional[str] = None


class HTTPNoContent(HTTPNoContentBase):
    pass


class UserLogin(BaseModel):
    email: str
    password: str


class UserLogined(BaseModel):
    access_token: str
    refresh_token: str


class AccessTokenRefreshed(BaseModel):
    new_access_token: str
