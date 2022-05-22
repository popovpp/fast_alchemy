"""
NAME
====
schemas - модуль, содержащий схемы данных

VERSION
=======
0.1.0

SYNOPSIS
========

    from . import schemas


    @app.post(
        "/users", response_model=schemas.UserCreated, 
        status_code=HTTP_201_CREATED, tags=["users"]
    )
    async def create_user(*, db: Session = Depends(get_db), user_in: schemas.UserCreating) -> Any:

DESCRIPTION
===========
Модуль содержит классы схем входных и выходных данных, описанных в терманах пакета pydantic

MODEL
======
"""

from typing import Optional
from pydantic import BaseModel, UUID4


class UserBase(BaseModel):
    """Базовая схема данных объекта User"""
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool = True
    is_verified: Optional[bool] = False
    is_superuser: Optional[bool] = False
    created: Optional[str]
    last_login: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "first_name": "John",
                "last_name": "Brown",
                "is_active": True,
                "is_verified": False,
                "is_superuser": False,
                "created": "2022-05-21 18:26:01.602931",
                "last_login": "2022-05-21 18:26:01.602931"
            }
        }


class UserCreated(BaseModel):
    """Схема выдачи метода создания объекта User"""
    id: UUID4
    email: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "id": "689f4bd2-d4b5-45c4-889b-76e0926c2001"
            }
        }


class UserCreating(BaseModel):
    """Схема входных данных для метода создания объекта User"""
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "first_name": "John",
                "last_name": "Brown",
                "password": "password"
            }
        }


class UserUpdate(BaseModel):
    """Схема входных данных для метода обновления объекта User"""
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "first_name": "John",
                "last_name": "Brown"
            }
        }


class UserInDBBase(UserBase):
    """<fpjdfz cхема данных полного объекта User"""
    id: Optional[UUID4] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "first_name": "John",
                "last_name": "Brown",
                "is_active": True,
                "is_verified": False,
                "is_superuser": False,
                "created": "2022-05-21 18:26:01.602931",
                "last_login": "2022-05-21 18:26:01.602931",
                "id": "689f4bd2-d4b5-45c4-889b-76e0926c2001",
            }
        }


class User(UserInDBBase):
    """Схема данных полного объекта User"""
    pass


class HTTPErrorBase(BaseModel):
    """Базовая схема данных для HTTPError ответа"""
    detail: Optional[str] = None


class HTTPError(HTTPErrorBase):
    """Схема данных для HTTPError ответв"""
    pass


class HTTPNoContentBase(BaseModel):
    """Базовая схема данных для HTTPNoContent ответа"""
    detail: Optional[str] = None


class HTTPNoContent(HTTPNoContentBase):
    """Схема данных для HTTPNoContent ответа"""
    pass


class UserLogin(BaseModel):
    """Схема входных данных для метода авторизации пользователя посредством логина и пароля"""
    email: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "password": "********"
            }
        }


class UserLogined(BaseModel):
    """Схема выходных данных для методов авторизации пользователя"""
    access_token: str
    refresh_token: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTMxNjQ3NzQsImlhdCI6MTY1MzE2Mjk3NCwic2NvcGUiOiJhY2Nlc3NfdG9rZW4iLCJzdWIiOnsidXNlcm5hbWUiOiJhZG1pbkBhZG1pbi5jb20iLCJ1c2VyX2lkIjoiNzY4ODQyNDctOTJmZC00MGI1LWFiZjgtZjViZGExOGVkYjQ3In19.D1GmAwLhV5RPLeT_FcY3SVLgM7KWHlQUHuK2N1myAJs",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTMxOTg5NzQsImlhdCI6MTY1MzE2Mjk3NCwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIiwic3ViIjp7InVzZXJuYW1lIjoiYWRtaW5AYWRtaW4uY29tIiwidXNlcl9pZCI6Ijc2ODg0MjQ3LTkyZmQtNDBiNS1hYmY4LWY1YmRhMThlZGI0NyJ9fQ.11o2wYJB5cUevWpihS7JEc6pf3NAZf3rL5Szc-d213M"
            }
        }


class AccessTokenRefreshed(BaseModel):
    """Схема выходных данных для метода обновления токена доступа"""
    new_access_token: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTMxNjQ3NzQsImlhdCI6MTY1MzE2Mjk3NCwic2NvcGUiOiJhY2Nlc3NfdG9rZW4iLCJzdWIiOnsidXNlcm5hbWUiOiJhZG1pbkBhZG1pbi5jb20iLCJ1c2VyX2lkIjoiNzY4ODQyNDctOTJmZC00MGI1LWFiZjgtZjViZGExOGVkYjQ3In19.D1GmAwLhV5RPLeT_FcY3SVLgM7KWHlQUHuK2N1myAJs",
            }
        }
