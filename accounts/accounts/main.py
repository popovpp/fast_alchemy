"""
NAME
====
main - главный модуль приложения accounts

VERSION
=======
0.1.0

SYNOPSIS
========

DESCRIPTION
===========
Модуль, содержит методы API:
    GET /users - получить список пользователей
    POST /users - создать пользователя
    PUT /users/{id} - изменить поля записи пользователя с идентификатором id
    GET /users/{id} - получить запись пользователя с идентификатором id
    GET /users/email/{email} - получить запись пользователя, имеющего электронный 
    почтовый ящик email
    DELETE /users/{id} - удалить запись пользователя, имеющего идентификатор id
    POST /login - аутентификацич пользователя по логину и паролю
    GET /refresh_token - обновить токен доступа

MODEL
======
"""

from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException, Security
from pydantic import UUID4
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import (HTTP_201_CREATED, HTTP_404_NOT_FOUND,
                              HTTP_400_BAD_REQUEST,)
from typing import TypeVar

from . import schemas
from .db import get_db
from .models import User
from .auth import Auth
from . permissions import get_current_user, auth_required

from app.app import actions


class UserActions(actions.BaseActions[schemas.User, schemas.UserCreated, schemas.UserUpdate]):
    """Класс UserActions с базовыми CRUD операциями"""

    pass

# Экземпляр класса UserAction для использования в методах
user_actions = UserActions()


app = FastAPI()


security = HTTPBearer()
auth_handler = Auth()


@app.get("/users", response_model=List[schemas.User], tags=["users"])
@auth_required('is_superuser')
async def list_users(*, db: Session = Depends(get_db), skip: int = 0, limit: int = 100,
                     credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    """Метод GET /users - получить список пользователей"""

    users = await user_actions.get_all(User, 'created',db=db, skip=skip, limit=limit)
    return users


@app.post(
    "/users", response_model=schemas.UserCreated, status_code=HTTP_201_CREATED, tags=["users"]
)
async def create_user(*, db: Session = Depends(get_db), user_in: schemas.UserCreating) -> Any:
    """
    Метод POST /users - создать пользователя.
    TO DO: Реализовать в auth.py валидацию пароля по сложности при создании.
    """

    user_in_data = jsonable_encoder(user_in)
    user = await user_actions.get_by_attr_first(User, user_in_data['email'], 'email', db=db)
    if user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User with same email already exist")
    db_user = User(**user_in_data)
    db_user.set_password(user_in_data['password'])
    db_user.set_is_verified_false()
    db_user.set_is_superuser_false()
    db_user.set_created()
    user = await user_actions.create(db=db, db_obj=db_user)
    return {'id': user.id,
            'email': user.email}


@app.put(
    "/users/{id}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
@auth_required('is_superuser_or_is_owner')
async def update_user(*, db: Session = Depends(get_db), id: UUID4, 
                      user_in: schemas.UserUpdate,
                      credentials: HTTPAuthorizationCredentials = Security(security),
                      request: Request) -> Any:
    """Метод PUT /users/{id} - изменить поля записи пользователя с идентификатором id"""

    user = await user_actions.get_by_attr_first(User, id, 'id', db=db)
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = await user_actions.update(db=db, db_obj=user, obj_in=user_in)
    return user


@app.get(
    "/users/{id}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=['users'],
)
@auth_required('is_superuser_or_is_owner')
async def get_user_by_id(*, db: Session = Depends(get_db), id: UUID4,
                         credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    """Метод GET /users/{id} - получить запись пользователя с идентификатором id"""

    user = await user_actions.get_by_attr_first(User, id, 'id', db=db)
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@app.get(
    "/users/email/{email}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
@auth_required('is_superuser_or_is_owner')
async def get_user_by_email(*, db: Session = Depends(get_db), email: str,
                            credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    """
    Метод GET /users/email/{email} - получить запись пользователя, имеющего электронный 
    почтовый ящик email
    """

    user = await user_actions.get_by_attr_first(User, email, 'email', db=db)
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@app.delete(
    "/users/{id}",
    response_model=schemas.HTTPNoContent,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
@auth_required('is_superuser')
async def delete_user(*, db: Session = Depends(get_db), id: UUID4,
                      credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    """Метод DELETE /users/{id} - удалить запись пользователя, имеющего идентификатор id"""

    user = await user_actions.get_by_attr_first(User, id, 'id', db=db)
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = await user_actions.remove(user, db=db)
    return {'detail': 'No content'}


@app.post(
    '/login',
    response_model=schemas.UserLogined,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["auth"],
)
async def login(*, db: Session = Depends(get_db), user_in: schemas.UserLogin):
    """Метод POST /login - аутентификацич пользователя по логину и паролю"""

    user_in_data = jsonable_encoder(user_in)
    user = await user_actions.get_by_attr_first(User, user_in_data['email'], 'email', db=db)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if not await auth_handler.verify_password(user_in_data['password'], user.password):
        raise HTTPException(status_code=401, detail='Invalid password')
    access_token = await auth_handler.encode_token(user)
    refresh_token = await auth_handler.encode_refresh_token(user)
    user.set_last_login()
    await user_actions.update(db=db, db_obj=user, obj_in={'last_login': user.last_login})
    return {'access_token': access_token, 'refresh_token': refresh_token}


@app.get(
    '/refresh_token',
    response_model=schemas.AccessTokenRefreshed,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["auth"],
)
async def refresh_token(*, db: Session = Depends(get_db),
                        credentials: HTTPAuthorizationCredentials = Security(security)):
    """Метод GET /refresh_token - обновить токен доступа"""

    refresh_token = credentials.credentials
    new_token = await auth_handler.refresh_token(refresh_token)
    await get_current_user(db=db, token=new_token)
    return {'new_access_token': new_token}
