from starlette.status import (HTTP_400_BAD_REQUEST,
                              HTTP_401_UNAUTHORIZED,)
from fastapi.security import HTTPBearer
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from functools import wraps

from .auth import Auth
from . import actions


security = HTTPBearer()
auth_handler = Auth()


async def get_current_user(db: Session, token: str = Depends(security)):
    email = await auth_handler.decode_token(token)
    user = await actions.user.get_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('###############')
        db = kwargs.get('db')
#        token = kwargs.get('credentials').credentials
        print(db)#, token)
        return func(*args, **kwargs)
    
    return wrapper


def is_superuser(func, *args, **kwargs):
    print('###############')
    return func(*args, **kwargs)
    def wrapper(*args1, **kwargs1):
#        db = kwargs1.get['db']
#        token = kwargs.get['credentials'].credentials
        print('qwerty')
        func(*args1, **kwargs1)
    return wrapper
