"""
NAME
====
permissions - модуль, содержащий модель User

VERSION
=======
0.1.0

SYNOPSIS
========

    from accounts.permissions import auth_required


    @app.get("/users", response_model=List[schemas.User], tags=["users"])
    @auth_required('is_superuser')
    async def list_users(*, db: Session = Depends(get_db), skip: int = 0, limit: int = 100,
                         credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:

DESCRIPTION
===========
Модуль реализует декоратор @auth_required(permissions_item), который осуществляет проверку 
значений элементов входящего запроса на соответствие заданному аргументу permissions_item.
TO DO: здесь же можно реализовать детектироание ролей, роли можно передавать в токенах.

MODEL
======
"""

from starlette.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
                              HTTP_401_UNAUTHORIZED,)
from fastapi.security import HTTPBearer
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from functools import wraps

from .auth import Auth
from .models import User

from app.app import actions


security = HTTPBearer()
auth_handler = Auth()

# Словарь прав доступа
permissions = {
    'is_superuser': 'is_superuser',
    'is_authenticated': 'is_authenticated',
    'is_owner': 'is_owner',
    'is_superuser_or_is_owner': 'is_superuser_or_is_owner',
}


async def get_current_user(db: Session, token: str = Depends(security)):
    """Выявление наличия в базе пользователя, который отправил запрос"""

    request_user = await auth_handler.decode_token(token)
    current_user = await actions.BaseActions.get_by_attr_first(User, request_user['user_id'],
                                                               'id', db=db)
    if not current_user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="The current user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not current_user.is_active:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def auth_required(permissions_item):
    """Декоратор, устанавливающий заданные права доступа из словаря прав доступа"""

    def auth_required_wrapper(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = await get_current_user(db=kwargs.get('db'),
                                                  token=kwargs.get('credentials').credentials)
            if permissions_item == 'is_superuser':
                if not current_user.is_superuser:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                    )
            elif permissions_item == 'is_owner':
                if not (kwargs.get('email')==current_user.email or kwargs.get('id')==current_user.id):
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                    )
            elif permissions_item == 'is_superuser_or_is_owner':
                if not (current_user.is_superuser or
                       (kwargs.get('email')==current_user.email or kwargs.get('id')==current_user.id)):
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                    )
            return await func(*args, **kwargs)    
        return wrapper
    return auth_required_wrapper
