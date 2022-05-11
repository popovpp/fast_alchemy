from typing import Optional
from pydantic import BaseModel, UUID4


class UserBase(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool = True
    is_verified: Optional[bool] = False
    is_superuser: Optional[bool] = False
    created: Optional[str]
    last_login: Optional[str]


class UserCreated(BaseModel):
    id: UUID4
    email: str


class UserCreating(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    password: str


class UserUpdate(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserInDBBase(UserBase):
    id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


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
